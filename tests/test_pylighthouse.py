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

def assert_good(n, r, rdict):
    assert n.attempt_attach(r)
    pr = lighthouse.PrioritizedDistributor.from_list([n])

    assert pr.attempt_assign_loads([r]) == {
        r.name: n.name
    }
    rr = lighthouse.RoundRobinDistributor.from_list([n])

    assert rr.attempt_assign_loads([r]) == {
        r.name: n.name
    }
    bp = lighthouse.BinPackDistributor.from_list(rdict, [n])

    assert pr.attempt_assign_loads([r]) == {
        r.name: n.name
    }

def assert_bad(n, r, rdict):
    assert not n.attempt_attach(r)
    pr = lighthouse.PrioritizedDistributor.from_list([n])

    assert pr.attempt_assign_loads([r]) == {
        r.name: None
    }
    rr = lighthouse.RoundRobinDistributor.from_list([n])

    assert rr.attempt_assign_loads([r]) == {
        r.name: None
    }
    bp = lighthouse.BinPackDistributor.from_list(rdict, [n])

    assert pr.attempt_assign_loads([r]) == {
        r.name: None
    }


def test_bad_req_fail(req):
    n = lighthouse.Node.from_dict({
        "name": "mynode",
        "resources": {
            "cpu": 10,
            "mem": 10
        }
    })
    assert_bad(n, req, {
        "cpu": 1,
        "mem": 1,
        "disk": 1
        })

def test_off_req_fail(req):
    n = lighthouse.Node.from_dict({
        "name": "mynode",
        "resources": {
            "disk": 40
        }
    })
    assert_bad(n, req, {
        "cpu": 1,
        "mem": 1,
        "disk": 1
        })

def test_zilch_node_fail(req):
    n = lighthouse.Node.from_dict({
        "name": "mynode",
        "resources": {}
    })
    assert_bad(n, req, {
        "cpu": 1,
        "mem": 1,
        "disk": 1
        })

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
