#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Tests for `pylighthouse` package.
'''

import pytest

import pylighthouse.pylighthouse as lighthouse

@pytest.fixture
def req():
    req = lighthouse.Workload.from_dict({
        "name": "good",
        "requirements": {
            "cpu": 38,
            "mem": 24
        }
    })
    return req

def test_no_nodes(req):
    '''
    Test when there are no nodes in the distributor.
    '''
    empty_pr_distributor = lighthouse.PrioritizedDistributor.from_list([])
    results = empty_pr_distributor.attempt_assign_loads([req])
    assert results[req.name] == None

    empty_rr_distributor = lighthouse.RoundRobinDistributor.from_list([])
    results = empty_rr_distributor.attempt_assign_loads([req])
    assert results[req.name] == None

    empty_bp_distributor = lighthouse.BinPackDistributor.from_list({},[])
    results = empty_bp_distributor.attempt_assign_loads([req])
    assert results[req.name] == None

def test_standard_case(req):
    second_node_dict = {
                "name": "second",
                "resources": {
                    "cpu": 20,
                    "mem": 40
                }
            }

    normal_pr_distor = lighthouse.PrioritizedDistributor.from_list(
        lighthouse.Node.from_list([
            {
                "name": "first",
                "resources": {
                    "cpu": 40,
                    "mem": 80
                    }
            },
            second_node_dict
        ]))
    results = normal_pr_distor.attempt_assign_loads([req])
    assert results[req.name] == "first"
    assert normal_pr_distor.nodes == lighthouse.Node.from_list([
                {
                    "name": "first",
                    "resources": {
                        "cpu": 2,
                        "mem": 56
                    },
                    "assigned_workloads": {
                        "good": req
                    }
                },
                second_node_dict
            ])

def test_stateful():
    '''
    Test that the Nodes and Distributors are stateful
    '''

    parents = lighthouse.Node.from_list([{
        "name": "parent",
        "resources": {
            "patience": 1
        }
    }])
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
    pr = lighthouse.PrioritizedDistributor.from_list(parents)
    result1 = pr.attempt_assign_loads([a])
    assert result1 == {
        "kid-a": "parent"
    }
    result2 = pr.attempt_assign_loads([b])
    assert result2 == {
        "kid-b": None
    }

def make_rdict(n):
    rdict = {}
    for k, v in n.resources.items():
        if v >= 0:
            rdict[k] = 1
    return rdict


def assert_good(n, r, rdict=None):
    if not rdict:
        rdict = make_rdict(n)

    start_n = lighthouse.Node.from_dict(n.__dict__)
    assert n.attempt_attach(r)

    n.detach_all()
    assert n == start_n

    pr = lighthouse.PrioritizedDistributor.from_list([n])
    assert pr.attempt_assign_loads([r]) == {
        r.name: n.name
    }

    n.detach_all()
    assert n == start_n

    rr = lighthouse.RoundRobinDistributor.from_list([n])
    assert rr.attempt_assign_loads([r]) == {
        r.name: n.name
    }

    n.detach_all()
    assert n == start_n

    bp = lighthouse.BinPackDistributor.from_list(rdict, [n])
    assert pr.attempt_assign_loads([r]) == {
        r.name: n.name
    }

def assert_bad(n, r, rdict=None):
    if not rdict:
        rdict = make_rdict(n)

    start_n = lighthouse.Node.from_dict(n.__dict__)
    assert not n.attempt_attach(r)
    assert n == start_n

    pr = lighthouse.PrioritizedDistributor.from_list([n])
    assert pr.attempt_assign_loads([r]) == {
        r.name: None
    }
    assert n == start_n

    rr = lighthouse.RoundRobinDistributor.from_list([n])
    assert rr.attempt_assign_loads([r]) == {
        r.name: None
    }
    assert n == start_n

    bp = lighthouse.BinPackDistributor.from_list(rdict, [n])

    assert pr.attempt_assign_loads([r]) == {
        r.name: None
    }
    assert n == start_n

def test_bad_req_fail(req):
    n = lighthouse.Node.from_dict({
        "name": "mynode",
        "resources": {
            "cpu": 10,
            "mem": 10
        }
    })
    assert_bad(n, req, { "cpu": 1, "mem": 1, "disk": 1 })

def test_off_req_fail(req):
    n = lighthouse.Node.from_dict({
        "name": "mynode",
        "resources": {
            "disk": 40
        }
    })
    assert_bad(n, req, { "cpu": 1, "mem": 1, "disk": 1 })

def test_zilch_node_fail(req):
    n = lighthouse.Node.from_dict({
        "name": "mynode",
        "resources": {}
    })
    assert_bad(n, req, { "cpu": 1, "mem": 1, "disk": 1 })

def test_zilch_req():
    n = lighthouse.Node.from_dict({
        "name": "mynode",
        "resources": {
            "cpu": 10,
            "mem": 10
        }
    })
    r = lighthouse.Workload.from_dict({
        "name": "vacuous-req",
        "requirements": {}
        })
    assert_good(n, r, {
        "cpu": 1,
        "mem": 1,
        "disk": 1
        })

def test_doc_example_1():
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
    assert distor.attempt_assign_loads(lighthouse.Workload.from_list([
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
        }])) == {
            "vm-1": "cluster-member-1",
            "vm-2": "cluster-member-1"
        }

@pytest.fixture
def placestrat():
    nodes=lighthouse.Node.from_list([
        {
          "name": "node-1",
          "resources": {
            "cpu": 8,
            "mem": 8,
            "disk": 80
          }
        },
        {
          "name": "node-2",
          "resources": {
            "cpu": 8,
            "mem": 8,
            "disk": 80
          }
        },
        {
          "name": "node-3",
          "resources": {
            "cpu": 8,
            "mem": 8,
            "disk": 60
          }
        }
    ])
    workloads = lighthouse.Workload.from_list([
        {
          "name": "req-1",
          "requirements": {
            "cpu": 2,
            "mem": 2,
            "disk": 10
          }
        },
        {
          "name": "req-2",
          "requirements": {
            "cpu": 2,
            "mem": 2,
            "disk": 10
          }
        },
        {
          "name": "req-3",
          "requirements": {
            "cpu": 2,
            "mem": 2,
            "disk": 10
          }
        }
    ])
    return {"nodes": nodes, "workloads": workloads}

def test_doc_placestrat_prioritized(placestrat):
    '''
    Test documentation examples for placment strategies: Prioritized
    '''

    distor = lighthouse.PrioritizedDistributor.from_list(placestrat['nodes'])
    assert distor.attempt_assign_loads(placestrat['workloads']) == {
        "req-1": "node-1",
        "req-3": "node-1",
        "req-2": "node-1"
    }

def test_doc_placestrat_roundrobin(placestrat):
    '''
    Test documentation examples for placment strategies: RoundRobin
    '''
    distor = lighthouse.RoundRobinDistributor.from_list(placestrat['nodes'])
    distor.attempt_assign_loads(placestrat['workloads']) == {
        "req-1": "node-1",
        "req-3": "node-3",
        "req-2": "node-2"
    }


def test_doc_placestrat_binpack(placestrat):
    '''
    Test documentation examples for placment strategies: BinPack
    '''
    rubric_dict = {
        "cpu": 1,
        "mem": 0.5,
        "disk": 0.025
    }
    distor = lighthouse.BinPackDistributor.from_list(rubric_dict,
                                                        placestrat['nodes'])
    assert distor.attempt_assign_loads(placestrat['workloads']) == {
        "req-1": "node-3",
        "req-3": "node-3",
        "req-2": "node-3"
    }

def test_ward():
    '''
    Infinite negative value wards things off
    '''
    nd = lighthouse.Node.from_dict({
        "name": "oldhouse",
        "resources": {
            "room": 1,
            "board": 1,
            "spiders": -float("inf")
            }
        })
    wk = lighthouse.Workload.from_dict({
        "name": "boarder",
        "requirements": {
            "room": 1,
            "board": 1
        }
    })
    assert_bad(nd, wk)

def test_immunity_basic():
    nd = lighthouse.Node.from_dict({
        "name": "oldhouse",
        "resources": {
            "room": 1,
            "board": 1,
            "spiders": -float("inf")
            }
        })
    wk = lighthouse.Workload.from_dict({
        "name": "boarder",
        "requirements": {
            "room": 1,
            "board": 1
        },
        "immunities": set([
            "spiders"
        ])
    })
    assert_good(nd, wk)

def test_immunity_rugsweep():
    '''
    Can I take more than I'm allowed if I declare immunity
    '''
    nd = lighthouse.Node.from_dict({
        "name": "oldhouse",
        "resources": {
            "room": 1,
            "board": 1,
            }
        })
    wk = lighthouse.Workload.from_dict({
        "name": "boarder",
        "requirements": {
            "room": 4,
            "board": 1
        },
        "immunities": set([
            "room"
        ])
    })
    assert_good(nd, wk)

def test_shortcoming_failure():
    '''
    Shortcoming offering fell short
    '''
    nd = lighthouse.Node.from_dict({
        "name": "oldhouse",
        "resources": {
            "room": 1,
            "board": 1,
            "spiders": -5
            }
        })
    wk = lighthouse.Workload.from_dict({
        "name": "boarder",
        "requirements": {
            "room": 1,
            "board": 1,
            "spiders": -4
        }
    })
    assert_bad(nd, wk)

def assert_uniform_assignment(nodes, loads, outcome, rdict=None):
    if not rdict:
        rdict = make_rdict(nodes[0])

    pr = lighthouse.PrioritizedDistributor.from_list(nodes)
    assert pr.attempt_assign_loads(loads) == outcome
    for n in nodes:
        n.detach_all()
    rr = lighthouse.RoundRobinDistributor.from_list(list(nodes))
    assert pr.attempt_assign_loads(loads) == outcome
    for n in nodes:
        n.detach_all()
    bp = lighthouse.BinPackDistributor.from_list(rdict, list(nodes))
    assert bp.attempt_assign_loads(loads) == outcome

def test_tagging():
    '''
    Tags are zero-quantity requirements
    '''
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
    assert_uniform_assignment(nodes, workloads,
            {
                "snow-white": "charming"
            })
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
    assert_uniform_assignment(no_room, workloads,
            {
                "snow-white": None
            })

def test_semaphore_basic():
    '''
    Semaphores are like aversions, but are more enforced
    '''

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
    # This is not only testing semaphore,
    # but something else:
    # The sort for binpack goes by score, then name
    assert_uniform_assignment(nodes, workloads, {
        "aurora": "prince",
        "buttercup": None,
        "cinderella": None
        })

def test_aversion_group():
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
    assert_uniform_assignment(nodes, workloads, {
        "college-student-1": "house-1",
        "college-student-2": "house-2"
        })
    no_room = lighthouse.Node.from_list([
        {
            "name": "house-1",
            "resources": {
                "bathroom": 25,
                "bedroom": 10,
                "kitchen": 10
            }
        }
    ])
    assert_uniform_assignment(no_room, workloads, {
        "college-student-1": "house-1",
        "college-student-2": "house-1"
        })
