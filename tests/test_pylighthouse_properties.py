#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 the pylighthouse authors, see the AUTHORS.rst file.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

'''
Tests for `pylighthouse` package.
'''

import pytest
import pylighthouse.pylighthouse as lighthouse

from hypothesis import given, assume
import hypothesis.strategies as st
from string import printable


# So like
# generate a dictionary of printables and integers,
# make a node and a load and then add one more key to one of them
# and see what happens
@given(traits=st.dictionaries(st.text(printable), st.integers()),
        newtrait=st.text(printable),
        newval=st.integers(min_value=0),
        nname=st.text(printable),
        lname=st.text(printable))
def test_tagging(traits, newtrait, newval, nname, lname):
    '''
    node tagging lets arbitrary workloads on but tagged workloads need the tag
    '''
    assume(newtrait not in traits.keys())
    expanded = dict(traits)
    expanded[newtrait] = newval
    n = lighthouse.Node.from_dict({
        'name': nname,
        'resources': traits})
    l = lighthouse.Workload.from_dict({
        'name': lname,
        'requirements': expanded})
    assert not n.attempt_attach(l)
    N = lighthouse.Node.from_dict({
        'name': nname,
        'resources': expanded})
    L = lighthouse.Workload.from_dict({
        'name': lname,
        'requirements': traits})
    assert N.attempt_attach(L)


def implies(a,b):
    return (not a) or b

@given(nname=st.text(printable),
        lname=st.text(printable),
        data=st.data())
def test_assignment_time_invariant(nname, lname, data):
    '''
    all traits must be non-zero at assignment time
    '''
    size = data.draw(st.integers(min_value=0, max_value=10))
    names = data.draw(st.lists(st.text(printable), min_size=size,
        max_size=size, unique=True))
    have = data.draw(st.lists(st.integers(), min_size=size, max_size=size))
    need = data.draw(st.lists(st.integers(), min_size=size, max_size=size))
    resources = dict(zip(names, have))
    requirements = dict(zip(names, need))
    n = lighthouse.Node.from_dict({
        'name': nname,
        'resources': resources
        })
    l = lighthouse.Workload.from_dict({
        'name': lname,
        'requirements': requirements
        })
    sum0 = True
    for i in range(0,size):
        sum0 = sum0 and ((have[i] - need[i]) >= 0)
    result = n.attempt_attach(l)
    assert implies(result, sum0)

@given(lname=st.text(printable),
        nname=st.text(printable),
        traitn=st.text(printable),
        traitv=st.integers())
def test_wards(lname, nname, traitn, traitv):
    resources = {traitn: traitv}
    n = lighthouse.Node.from_dict({
        'name': nname,
        'resources': resources
        })
    l = lighthouse.Workload.from_dict({
        'name': lname,
        'requirements': {},
        'immunities': set([traitn])
        })
    assert n.attempt_attach(l)

# TODO: Test binpack: this would be when
# two nodes are given. one is 'smaller' than
# the other, but both are way bigger than all the
# workloads. Then all the workloads will be
# scheduled onto the smaller load.
