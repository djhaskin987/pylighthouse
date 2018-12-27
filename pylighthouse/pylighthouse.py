# -*- coding: utf-8 -*-

"""Main module."""

from sortedcontainers import SortedDict
import math


class LighthouseException(Exception):
    pass


class Workload(object):
    def __init__(self, name, requirements, immunities=set(),
                 aversion_groups=set()):
        self.name = name
        self.requirements = requirements
        self.immunities = immunities
        self.aversion_groups = aversion_groups

    def __eq__(self, other):
        return type(self) == type(other) and \
                self.__dict__ == other.__dict__

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    @staticmethod
    def from_list(ds):
        return [Workload.from_dict(d) for d in ds]

    @staticmethod
    def from_dict(d):
        if 'immunities' in d and type(d['immunities']) == list:
            immunities = set(d['immunities'])
        elif 'immunities' in d and type(d['immunities']) == set:
            immunities = d['immunities']
        else:
            immunities = set()

        if 'aversion_groups' in d and type(d['aversion_groups']) == list:
            aversion_groups = set(d['aversion_groups'])
        elif 'aversion_groups' in d and type(d['aversion_groups']) == set:
            aversion_groups = d['aversion_groups']
        else:
            aversion_groups = set()
        return Workload(d['name'],
                        d['requirements'],
                        immunities,
                        aversion_groups)


class Node(object):
    def __init__(self, name, resources, assigned_workloads=None):
        self.name = name
        self.resources = resources
        if assigned_workloads:
            self.assigned_workloads = assigned_workloads
        else:
            self.assigned_workloads = dict()

    def __eq__(self, other):
        return type(self) == type(other) and \
                self.__dict__ == other.__dict__

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    @staticmethod
    def from_list(ns):
        return [Node.from_dict(n) for n in ns]

    @staticmethod
    def from_dict(d):
        if 'assigned_workloads' in d:
            return Node(d['name'], d['resources'], d['assigned_workloads'])
        else:
            return Node(d['name'], d['resources'])

    def has_averse_loads(self, load):
        groups = load.aversion_groups
        for nw, w in self.assigned_workloads.items():
            if len(groups.intersection(w.aversion_groups)) > 0:
                return True
        return False

    # Returns True if it worked, False otherwise
    def attempt_attach(self, load):
        have_keys = set(self.resources.keys())
        need_keys = set(load.requirements.keys())
        present_keys = have_keys.union(need_keys)

        # Check that requirements are a subset of resources
        if len(present_keys) > len(have_keys):
            return False

        used_keys = have_keys.intersection(need_keys)
        used = dict()

        # Check to make sure all un-tolerated
        # values are zero or above,
        # first in the keys of resources that will be used
        for k in used_keys:
            v = self.resources[k] - load.requirements[k]
            if k not in load.immunities and \
                    v < 0:
                return False
            used[k] = v

        # and then check keys of resources that aren't being used
        check_keys = have_keys.difference(used_keys)
        for k in check_keys:
            if k not in load.immunities and \
                    self.resources[k] < 0:
                return False

        # Everything looks good, commit the resource
        # allocation and return True
        self.resources.update(used)
        self.assigned_workloads[load.name] = load
        return True

    def attempt_attach_amicable(self, load):
        if self.has_averse_loads(load):
            return False
        else:
            return self.attempt_attach(load)

    def detach_all(self):
        for wname, w in self.assigned_workloads.items():
            for k, v in w.requirements.items():
                self.resources[k] = self.resources[k] + v
        self.assigned_workloads = dict()

    def add_ward(self, ward):
        self.resources[ward] = -math.inf


class Distributor(object):

    def _attempt_placement(self, placer, load):
        pass

    def _attempt_assign_load(self, load):
        attempts = [
                lambda n, l: n.attempt_attach_amicable(l),
                lambda n, l: n.attempt_attach(l)
            ]
        for attempt in attempts:
            n = self._attempt_placement(attempt, load)
            if not (n is None):
                return n.name
        return None

    def attempt_assign_loads(self, loads):
        results = {}
        for l in loads:
            results[l.name] = self._attempt_assign_load(l)
        return results


class PrioritizedDistributor(Distributor):
    def __init__(self, nodes):
        self.nodes = nodes

    @staticmethod
    def from_list(nodes):
        return PrioritizedDistributor(nodes)

    def _attempt_placement(self, placer, load):
        for i in range(0, len(self.nodes)):
            result = placer(self.nodes[i], load)
            if result:
                return self.nodes[i]
        return None


class RoundRobinDistributor(Distributor):
    def __init__(self, nodes):
        self.nodes = nodes
        self.next = 0

    @staticmethod
    def from_list(nodes):
        return RoundRobinDistributor(nodes)

    def _attempt_placement(self, placer, load):
        size = len(self.nodes)
        index = 0
        for i in range(0, size):
            index = (i + self.next) % size
            result = placer(self.nodes[index], load)
            if result:
                self.next = (self.next + 1) % size
                return self.nodes[index]
        return None


class LighthouseRubricException(LighthouseException):
    pass


class Rubric(object):
    def __init__(self, rubric):
        self.rubric = rubric
        self.keys_rubric = set(self.rubric.keys())
        self.size = len(self.keys_rubric)

    def score(self, parts):
        keys_parts = set(parts.keys())
        shared_keys = self.keys_rubric.intersection(keys_parts)

        result = 0
        for k in shared_keys:
            result = result + (self.rubric[k] * parts[k])

        return result

    # Intended for use with BinPackDistributor
    # sort workloads biggest workload first
    def sort_workloads(self, loads):
        return sorted(loads,
                      key=(lambda l: self.score(l.requirements)),
                      reverse=True)


class BinPackDistributor(Distributor):

    def __init__(self, rubric, nodes):
        self.rubric = rubric
        self.scores = {}
        self.nodes = SortedDict({})
        for n in nodes:
            sc = self.rubric.score(n.resources)
            self.nodes[(sc, n.name)] = n
            self.scores[n.name] = sc

    @staticmethod
    def from_list(rubric, nodes):
        return BinPackDistributor(Rubric(rubric), nodes)

    def _attempt_placement(self, placer, load):
        found_node = None
        found_name = None
        found_old_score = None
        for (nscore, name), node in self.nodes.items():
            if nscore < load[0]:
                continue
            result = placer(node, load[1])
            if result:
                found_node = node
                found_name = name
                found_old_score = nscore
                break
        if not (found_node is None):
            new_score = self.rubric.score(found_node.resources)
            self.scores[found_name] = new_score
            del self.nodes[(found_old_score, found_name)]
            self.nodes[(new_score, found_name)] = found_node
            return found_node
        return None

    def attempt_assign_loads(self, loads):
        annotated_loads = []
        for l in loads:
            load_score = self.rubric.score(l.requirements)
            annotated_loads.append((load_score, l))
        annotated_loads = sorted(annotated_loads,
                                 key=(lambda x: x[0]),
                                 reverse=True)
        results = {}
        for l in annotated_loads:
            results[l[1].name] = self._attempt_assign_load(l)
        return results
