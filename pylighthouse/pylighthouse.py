# -*- coding: utf-8 -*-

"""Main module."""

from sortedcontainers import SortedDict

class LighthouseException(Exception):
    pass

class Workload(object):
    def __init__(self, name, requirements, tolerations, aversion_groups):
        self.name = name
        self.requirements = requirements
        self.tolerations = tolerations
        self.aversion_groups = aversion_groups
        self.assignment

class Node(object):
    def __init__(self, name, resources, assigned_workloads={}):
        self.name = name
        self.resources = resources
        self.assigned_workloads = assigned_workloads

    def has_averse_loads(self, load):
        groups = load.aversion_groups
        for w in self.assigned_workloads:
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
            if k not in load.tolerations and \
                    v < 0:
                return False
            used[k] = v

        # and then check keys of resources that aren't being used
        check_keys = have_keys.difference(used_keys)
        for k in check_keys:
            if k not in load.tolerations and \
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

class Distributor(object):
    @classmethod
    def from_list(nodes):
        pass

    def attempt_placement(self, placer, load):
        pass

class PrioritizedDistributor(Distributor):
    def __init__(self, nodes):
        self.nodes = nodes

    @classmethod
    def from_list(nodes):
        return PrioritizedDistributor(nodes)

    def attempt_placement(self, placer, load):
        for i in range(0,len(self.nodes)):
            result = placer(self.nodes[i], load)
            if result:
                return self.nodes[i]
        return None

class RoundRobinDistributor(Distributor):
    def __init__(self, nodes):
        self.nodes = nodes
        self.next = 0

    @classmethod
    def from_list(nodes):
        return RoundRobinDistributor(nodes)

    def attempt_placement(self, placer, load):
        size = len(self.nodes)
        index = 0
        for i in range(0,size):
            index = (i + self.next) % size
            result = placer(self.nodes[index],load)
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
        self.size = len(keys_rubric)

    def score(self, parts):
        keys_parts = set(parts.keys())
        shared_keys = self.keys_rubric.intersection(keys_parts)

        if len(shared_keys) != self.size:
            raise LighthouseRubricException('not all keys present in rubric')

        result = 0
        for k in shared:
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
            score = self.rubric.score(n)
            self.nodes[(n.name,score)] = n
            self.scores[n.name] = score

    @classmethod
    def from_list(rubric, nodes):
        return BinPackDistributor(rubric, nodes)

    def attempt_placement(self, placer, load):
        found_node = None
        found_name = None
        found_old_score = None
        for (name,old_score), node in self.nodes.items():
            result = placer(node, load)
            if result:
                found_node = node
                found_name = name
                found_old_score = old_score
                break
        if not (found_node is None):
            new_score = self.rubric.score(found_node.resources)
            self.score[n.name] = new_score
            del self.nodes[(found_name, found_old_score)]
            self.nodes[(found_name, new_score)] = found_node
            return found_node
        return None

class ResourceManager(object):
    def __init__(self, distributor):
        self.distributor = distributor
        self.assignments = assignments

    def attempt_assign_load(self, load):
        attempts = [
                lambda n,l: n.attempt_attach_amicable(l),
                lambda n,l: n.attempt_attach(l)
            ]
        for attempt in attempts:
            n = self.distributor.attempt_placement(attempt, load)
            if not (n is None):
                self.assignments[load.name] = n.name
                return True
        return False

    def attempt_assign_loads(self, loads):
        bad_loads = []
        for l in loads:
            if not self.attempt_assign_load(l):
                bad_loads.append(l)
        return bad_loads
