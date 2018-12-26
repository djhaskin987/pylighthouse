# pylighthouse
It finds safe harbor for workloads.

# Quick Start
With a JSON file that looks like this for example:

```json
{
  "rubric": {
    "cpu": 1,
    "mem": 0.5,
    "disk": 0.025
  },
  "nodes": [
    {
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
  ],
  "loads": [
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
    }
  ]
}
```


```python
import pylighthouse

with open('loadsnnodes.json', 'r', encoding='utf-8', errors='ignore') as j:
    contents = json.load(j)

nodes = [pylighthouse.Node.from_dict(n) for n in contents['nodes']]
loads = [pylighthouse.Workload.from_dict(l) for l in contents['loads']]
rubric = pylighthouse.Rubric(contents['rubric'])

d = pylighthouse.BinPackDistributor(rubric, nodes)
assignment_results = d.attempt_assign_loads(loads)
for lname, nname in assignment_results.items():
  if nname is None:
    print("Load could not be assigned: {n}".format(n=lname))
  else:
    print("Load {l} assigned to {n}".format(l=lname, n=nname))
```

In the above example, the json showing what nodes has what resources
show how much resources a node has *left*, not how much a node has
*total*.
