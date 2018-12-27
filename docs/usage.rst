.. _Usage:

=====
Usage
=====

To use pylighthouse in a project::

    import pylighthouse.pylighthouse as lighthouse

Basic Scheduling
----------------

.. highlight: python3

You can schedule workloads onto nodes like this::

    import pylighthouse.pylighthouse as lighthouse

    distor = lighthouse.PrioritizedDistributor.from_list(
        nodes=lighthouse.Node.from_list([{
            "name": "cluster-member-1",
            "resources": {
                "cpu": 6,
                "mem": 12,
                "disk": 50
            }
        },
        {
            "name": "cluster-member-2",
            "resources": {
                "cpu": 4,
                "mem": 16,
                "disk": 40
            }
        },
        {
          "name": "cluster-member-3",
          "resources": {
              "cpu": 0.7,
              "mem": 1.3,
              "disk": 17
          }
        }
    ]))
    distor.attempt_assign_loads(lighthouse.Workload.from_list([
        {
            "name": "vm-1",
            "requirements": {
                "cpu": 0.2,
                "mem": 0.1
            }
        },
        {
            "name": "vm-2",
            "requirements": {
                "cpu": 0.3,
                "mem": 0.3,
                "disk": 1
            }
        }]))
   # =>
   #{
   #    "vm-1": "cluster-member-1",
   #    "vm-2": "cluster-member-1"
   #}

As you can see, ``attempt_assign_loads`` takes a list of workloads and
attempts to assign workloads to the nodes given to the distributor at
construction time. It returns a dictionary with keys being the names of the
workloads and values being the names of the nodes to which those loads
were assigned. If workload could not be assigned to a node, the value
is ``None`` for that key instead.

.. caution:: The ``name`` field for each workload and node must be unique
             to that node or workload, or bad things will happen to innocent
             people (you. At least, I *hope* you're innocent :P).

Node resources and Workload requirements are free-form and can be arbitrary.

Note that the requirements in a workload need not include all the types
of resources found in nodes. In the above example, each node has
``mem``, ``cpu`` and ``disk`` attributes, but the requirements
need not list all of these as requirements.

Placement of workloads onto nodes is not guaranteed. That is, simply because
room exists for all workloads, this does not mean that pylighthouse will be
able to figure this out. You can help pylighthouse get better at packing nodes
tightly using the `BinPackDistributor`_ discussed below, and you can also
increase the capacity of the nodes.

Distributors and the nodes they contain are stateful. They remember workloads
previously given. So after this code::

    parent = lighthouse.Node.from_list([
        "name": "parent",
        "resources": {
            "patience": 1
        }
    ])
    a = lighthouse.Workload.from_dict({
        "name": "kid-a",
        "requirements": {
            "patience": 1
        }
    })
    b = lighthouse.Workload.from_dict({
        "name": "kid-b",
        "requirements": {
            "patience": 1
        }
    })
    pr = lighthouse.PrioritizedDistributor.from_list([parent])
    result1 = pr.attempt_assign_loads([a])
    # =>
    #{
    #    "kid-a": "parent"
    #}

Running this code afterwards::

    result2 = pr.attempt_assign_loads([b])

Would result in this assignment::

    {
        "kid-b": None
    }

This reflects that there is no current room for the second workload, as the
first has consumed all resources.

Placement Strategies
--------------------

pylighthouse comes with several different distributor classes, all of which
place workloads onto nodes. ``PrioritizedDistributor`` is the simplest,
but may not offer the best fit of loads onto nodes. ``RoundRobinDistributor``
is also offered as a simple way to distribute workloads semi-evenly across
a cluster of nodes. In general, ``BinPackDistributor`` will attempt to pack
as many workloads as possible onto as few nodes as possible and is, in general,
recommended.

The following code will be referred to when discussing each of the
placement strategies below::

    import pylighthouse.pylighthouse as lighthouse

    nodes=lighthouse.Node.from_list([
        {
          "name": "node-1",
          "resources": {
            "cpu": 2,
            "mem": 8,
            "disk": 60
          }
        },
        {
          "name": "node-2",
          "resources": {
            "cpu": 6,
            "mem": 6,
            "disk": 20
          }
        },
        {
          "name": "node-3",
          "resources": {
            "cpu": 4,
            "mem": 2,
            "disk": 40
          }
        }
    ])
    workloads = lighthouse.Workload.from_list([
        {
          "name": "req-1",
          "requirements": {
            "cpu": 8,
            "mem": 8,
            "disk": 80
          }
        },
        {
          "name": "req-2",
          "requirements": {
            "cpu": 8,
            "mem": 8,
            "disk": 80
          }
        },
        {
          "name": "req-3",
          "requirements": {
            "cpu": 8,
            "mem": 8,
            "disk": 60
          }
        }
    ])

Prioritized
+++++++++++

With a ``PrioritizedDistributor``, pylighthouse will attempt to assign
workloads to nodes in the order they appear in the given list of nodes, and in
the order the workloads appear.

This is the result if the above were run with ``PrioritizedDistributor``::

    distor = lighthouse.PrioritizedDistributor.from_list(nodes)
    distor.attempt_assign_loads(workloads)
    # =>
    #{
    #    "req-1": "node-1",
    #    "req-3": "node-1",
    #    "req-2": "node-1"
    #}

In this example, all nodes are assigned to ``node-1`` because they can all
fit on ``node-1`` and it appears first in the list of nodes given, so it is
tried first every time when loads are assigned to nodes.

RoundRobin
++++++++++

With a ``RoundRobinDistributor``, assignment of workloads is done in the order
given in the list, but placement attempts for each successive load starts on
the node just after the successful placement of the previous load -- in a
"round robin" fashion.

This is the result if the above were run with ``RoundRobinDistributor``::
``RoundRobin``::

    distor = lighthouse.RoundRobinDistributor.from_list(nodes)
    distor.attempt_assign_loads(workloads)
    # =>
    #{
    #    "req-1": "node-1",
    #    "req-3": "node-3",
    #    "req-2": "node-2"
    #}

.. _BinPackDistributor:

BinPack
+++++++

This strategy requires additional information. A *rubric* must be specified.
In discussing the example above, we will assume in our discussion that the
following code is also part of the script we are building::

    rubric_dict = {
        "cpu": 1,
        "mem": 0.5,
        "disk": 0.025
    }

``BinPackDistributor`` attempts to pack in as many requirements into as few
nodes as possible.  In order to do so, the caller must specify a rubric.
This gives quantities that will be used to score each workload and node by
multiplying each quantity for a given node or workload and summing the results.
If a quantity isn't in the rubric but is in a node's resources or a load's
requirements, the quantity won't count towards the score.
if a quantity is in the rubric but isn't in a node's resources or a load's
requirements, the score will be computed as if the quantity was ``0``.

The score of any given node or workload semantically corresponds to the node
or load's "size". Therefore, as long as the quantities in nodes and loads that
are scored via the rubric are positive, it is recommended to always specify
positive quantities in the rubric as well.

.. caution:: Specifying negative quantities in the rubric is possible, but
    should be rare, and should be intended only to multiply against a
    requirement or resource which will also *always* be negative, such as those
    discussed below under `Wards and Immunities`_. If this rule is not
    followed, ``BinPackDistributor`` may misbehave. As a rule,
    if the value is expected to be negative, don't include it in the rubric.

If ``BinPackDistributor`` was used in the above example, the result would look
like this::

    distor = lighthouse.RoundRobinDistributor.from_list(rubric_dict, nodes)
    distor.attempt_assign_loads(workloads)
    # =>
    #{
    #    "req-1": "node-3",
    #    "req-3": "node-3",
    #    "req-2": "node-3"
    #}

In this example, all workloads were assigned to ``node-3``, since ``node-3``
had the least room in it going into scheduling, since it had the least disk
space.

``BinPackDistributor`` first attempts to place workloads by score, but if two
workloads share the same score, BinPackDistributor will try to place the
workload in sorted order ascending by name of the nodes. So a node named
"a" will be tried before a node named "b" if both nodes share the same
score.

Placement Enforcement
---------------------

At the time of placement of a workload onto a node, the requirements are
subtracted from the node's resources so as to keep track of what nodes still
have room left for more assignments. In particular, all attributes associated
with the *node* must register with a quantity at or above zero in order for the
assignment to succeed at *assignment time*.

This allows for some interesting possibilities for how to enforce where
workloads can be assigned in your cluster of nodes.

Node Tagging
++++++++++++

Sometimes it is desirable to mark a particular node as specifically dedicated
to a particular type of workload. When this is desired, it is simply a matter
of adding a resource to a node with zero as the quantity::



    nodes = lighthouse.Nodes.from_list([
        {
            "name": "node1",
            "resources": {
               "dedicated": 0.0,
               #...
            }
        }
    ])

Then, simply place a similar attribute in the requirements dictionary
of the workloads that should be run on the dedicated nodes::

    workloads = lighthouse.Workloads.from_list([
        {
            "name": "workload1",
            "requirements": {
                "dedicated": 0.0,
                #...
            }
        }
    ])

This works because all requirements listed for a workload must be present
on the node and none may be allowed to be below zero, but zero is okay.

For example::

    nodes = lighthouse.Node.from_list([
        {
            "name": "phillip",
            "resources": {
                "bravery": 25,
                "kindness": 25
            }
        },
        {
            "name": "charming",
            "resources": {
                "bravery": 25,
                "kindness": 25,
                "nice-castle": 0,
            }
        }
    ])
    workloads = lighthouse.Workload.from_list([
        {
            "name": "snow-white",
            "requirements": {
                "nice-castle": 0,
            }
        }])

Any distributor attempting to assign these workloads to the nodes
via ``attempt_assign_loads`` will yield the following assignment::

    {
        "snow-white": "charming"
    }

This is because prince ``charming`` has the ``nice-castle`` "tag", while
``phillip`` does not.

Tags also ensure that no assignment will be made if tags are not present::

    no_room = lighthouse.Node.from_list([
        {
            "name": "phillip",
            "resources": {
                "bravery": 25,
                "kindness": 25
            }
        },
        {
            "name": "charming",
            "resources": {
                "bravery": 25,
                "kindness": 25
            }
        }
    ])

Any distributor attempting to assign these workloads to the nodes
via ``attempt_assign_loads`` will yield the following assignment::

    {
        "snow-white": None
    }

This is because none of the princes (nodes) had a ``nice-castle`` "tag"
present in their resources.

Semaphores
++++++++++

Often it is convenient to limit how many of a particular type of workload
is allowed to be placed on a node. This is done simply by listing a
resource in a node's resource map and in relevant workload's requirements maps.
The pattern is to list the number of workloads a node can handle at the same
time in the semaphore as the number for the resource in the node, and list
``1`` as the quantity for the requirement for each workload. For example::


    nodes = lighthouse.Node.from_list([
        {
            "name": "prince",
            "resources": {
                "bravery": 25,
                "kindness": 25,
                "nice-castle": 0,
                "wife": 1
            }
        }
    ])
    workloads = lighthouse.Workload.from_list([
        {
            "name": "aurora",
            "requirements": {
                "bravery": 12,
                "nice-castle": 0,
                "wife": 1,
            }
        },
        {
            "name": "buttercup",
            "requirements": {
                "bravery": 12,
                "nice-castle": 0,
                "wife": 1,
            }
        },
        {
            "name": "cinderella",
            "requirements": {
                "bravery": 12,
                "nice-castle": 0,
                "wife": 1,
            }
        }
    ])

In this example, the node is a potential suitor for a number of fairy tale
princesses. The prince can only have a single wife, and so ``wife`` is listed
as a resource with quantity ``1``. This is the semaphore. Any distributor
based off of those nodes will yield the same results as assignments if
``attempt_assign_loads`` is called::

    {
        "aurora": "prince",
        "buttercup": None,
        "cinderella": None
    }

The ``PrioritizedDistributor`` and ``RoundRobinDistributor`` will both
schedule the first given princess in the list, ``aurora``, but will
not be able to schedule the remaining princesses. ``BinPackDistributor``
will likewise schedule ``aurora`` first because the scores of the workloads
based on any reasonable (non-negative) rubric will show that they have the same
sizes of requirements, and ``aurora`` sorts before the other names.

.. _Wards and Immunities:

Wards and Immunities
++++++++++++++++++++

This concept is similar to Kubernetes' `Taints and Tolerations`_ idea, but also
has nuances to it that make it more flexible.

The idea is to mark a particular set of nodes as unavailable for workloads
unless those workloads specifically opt into being run on those nodes.

We do this in pylighthouse using Wards and Immunities.

It is perfectly valid to list negative values for resources at *node
construction time*; however, as has been previously explained, if there are any
resources in a node with negative quantity at *assignment time of a workload*,
the workload will not be able to be attached to the node.

A negative resource with a finite quantity is called a
*shortcoming*, while a negative resource of infinite or very large quantity
may be termed a *ward*.

Negative resources can be overcome by a resource in one of two ways.

First, for negative resources of *finite* quantity, this can be overcome by
simply listing a negative requirement. That way, when one is subtracted from
the other, the result will be zero::

    nodes = lighthouse.Node.from_list([
        {
            "id: "node1",
            "resources": {
               "flies": -5.0,
               #...
            }
        }
    ])
    workloads = lighthouse.Workload.from_list([
        {
            "name": "workload1",
            "requirements": {
                "flies": -5.0,
                #...
            }
        }
    ])

This may be used to list "shortcomings" of a node that precludes it from having
workloads scheduled on it unless at least one workload has a sufficient
tolerance to the shortcoming.

Second, we list a node up front at construction time with a ward::

    nodes = lighthouse.Node.from_list([
        {
            "name": "node1",
            "resources": {
               "spiders": -float("inf")
               #...
            }
        }
    ]

In this scenario, workloads will not be able to overcome the ward no
matter how finitely resilient the workload is. However, we can list an
immunity on the workload.

An *immunity* in a workload tells pylighthouse to ignore whatever value exists
for a resource in a node at assignment time of the workload. So, in order to
schedule a workload on the node listed above, we can simply add ``"spiders"``
to the set of immunities for the workload::

    workloads = lighthouse.Workload.from_list([
        {
            "name": "workload1",
            "requirements": {
                #...
            },
            "immunities": set([
                "spiders",
                #...
            ])
        }
    ])

.. _Taints and Tolerations: https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/

Aversion Groups
---------------

Aversion Groups correspond to anti-affinity groups in other scheduling schemes.

Put simply, any aversion group listed for a workload causes that workload
to "prefer" to be scheduled on a node without any other workloads listed
as "belonging" to the same aversion group, like this:::

    # ...
    nodes = lighthouse.Node.from_list([
        {
            "name": "node1",
            "resources": {
               # ...
            }
        },
        {
            "name": "node2",
            "resources": {
               # ...
            }
        }

    ])
    workloads = lighthouse.Workload.from_list([
        {
            "name": "workload1",
            "requirements": {
                # ...
            },
            "aversion_groups": set([
                "io-bound",
                # ...
            ])
        },
        {
            "name": "workload2",
            "requirements": {
                # ...
            },
            "aversion_groups": set([
                "io-bound",
                # ...
            ])
        }
    ])

In the above example, both ``workload1`` and ``workload2`` will try really hard
to be scheduled on different nodes, becuase they both list the ``io-bound``
aversion group in their aversion groups list.

In this example, we have two houses and two college students. Each
student goes to a different local university and is part of the same
cross-school rivalry. We may model this scenario like this::

    nodes = lighthouse.Node.from_list([
        {
            "name": "house-1",
            "resources": {
                "bathroom": 25,
                "bedroom": 10,
                "kitchen": 10
            }
        },
        {
            "name": "house-2",
            "resources": {
                "bathroom": 25,
                "bedroom": 10,
                "kitchen": 15
            }
        }
    ])
    workloads = lighthouse.Workload.from_list([
        {
            "name": "college-student-1",
            "requirements": {
                "bathroom": 5,
                "bedroom": 2,
                "kitchen": 2
                },
            "aversion_groups": [
                "north_south_rivalry"
            ]
        },
        {
            "name": "college-student-2",
            "requirements": {
                "bathroom": 5,
                "bedroom": 2,
                "kitchen": 2
                },
            "aversion_groups": [
                "north_south_rivalry"
            ]
        }
    ])

.. note:: The above example shows that ``aversion_groups`` can be specified as
    a list or set when calling ``Workload.from_list``, but they are internally
    represented as sets.

Although there is plenty of room for both college students to live
in the same house, any distributor attempting to assign these workloads to the
nodes via ``attempt_assign_loads`` will yield the following assignment::

    {
        "college-student-1": "house-1",
        "college-student-2": "house-2"
    }

As can be seen, even though there is plenty of room for both students to be
in the same house, they are put in different houses due to them being in the
same rivalry (aversion group).

However, if there is no other house in which they might live, the students
will still reluctantly be scheduled together. Using this list of nodes instead
of the one above::

    nodes = lighthouse.Node.from_list([
        {
            "name": "house-1",
            "resources": {
                "bathroom": 25,
                "bedroom": 10,
                "kitchen": 10
            }
        }
    ])

The assignments would look like this instead::

    {
        "college-student-1": "house-1",
        "college-student-2": "house-1"
    }

