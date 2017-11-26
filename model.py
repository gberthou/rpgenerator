import random
import utils

def tuple2edge(x):
    return ScenarioEdge(x[0], x[1])

class ScenarioNode:
    def __init__(self, node_id, layer):
        self.node_id = node_id
        self.layer = layer

    def __str__(self):
        return "node_%d_%d" % (self.layer, self.node_id)

class ScenarioEdge:
    def __init__(self, node_from, node_to):
        self.node_from = node_from
        self.node_to   = node_to
        self.quest     = None

    def is_unmissable(self, edgeset):
        for e in edgeset - {self}:
            if e.node_from == self.node_from:
                return False
        return True

    def must_be_distinct_from_list(self, edgeset):
        return [e for e in edgeset - {self} if e.node_from == self.node_from]

    def must_be_compatible_with_list(self, edgeset):
        return [e for e in edgeset - {self} if e.precedes_edge(self, edgeset)]

    def precedes_edge(self, edge, edgeset):
        if self.node_to == edge.node_from:
            return True

        open_nodes = {self.node_to}
        edgeset = edgeset- {self}
        while len(edgeset) > 0:
            # subset = all edges that come from any node from open_nodes
            subset = set(e for e in edgeset if e.node_from in open_nodes)
            # If there is no such edge, dead end => self does not precede edge
            if len(subset) == 0:
                return False

            # New open_nodes value = all nodes that are reachable using edges in susbet
            open_nodes = set(e.node_to for e in subset)
            # If the origin of edge is reachable from edges in subset, then self precedes edge
            if edge.node_from in open_nodes:
                return True
            # Remove considered edges
            edgeset = edgeset - subset
        return False

    def __str__(self):
        return "%s -> %s [label=\"%s\"]" % (self.node_from, self.node_to, self.quest)

class Scenario:
    def __init__(self, lore, max_beginnings, max_endings, layer_count, max_layer_width, diversity_factor):
        self.lore = lore

        self.beginning_count = random.randint(1, max_beginnings)
        self.ending_count    = random.randint(1, max_endings)

        # Beginning nodes have ids from 0 to self.beginning_count-1
        self.beginnings = set(ScenarioNode(i, 0) for i in range(self.beginning_count))

        # Ending nodes have ids from self.beginning_count to self.beginning_count+self.ending_count-1
        self.endings = set(ScenarioNode(self.beginning_count + i, layer_count + 1) for i in range(self.ending_count))

        # Create edges (empty first)
        self.edges = set()

        # Create layers (ordered list of unordered set)
        self.layers = [self.beginnings]

        next_node_id = self.beginning_count + self.ending_count
        previous_layer = set(self.beginnings)

        # For each layer
        for layer in range(layer_count):
            # Create node_count nodes
            node_count    = random.randint(1, max_layer_width)
            nodes_to_add  = set(ScenarioNode(next_node_id + i, layer + 1) for i in range(node_count))
            next_node_id += node_count

            self.edges = self.edges.union(tuple2edge(i) for i in set(utils.erode_subgraph_of(previous_layer, nodes_to_add, False, diversity_factor)))

            # Update previous_layer
            previous_layer = nodes_to_add

            self.layers.append(nodes_to_add)

        # Finally connect last layer to endings
        self.edges = self.edges.union(tuple2edge(i) for i in set(utils.erode_subgraph_of(previous_layer, self.endings, True, diversity_factor)))

        self.layers.append(self.endings)

        self.build_quests()

    def build_quests(self):
        for edge in self.edges:
            is_unmissable   = edge.is_unmissable(self.edges)
            distinct_from   = list(e for e in edge.must_be_distinct_from_list(self.edges) if e.quest != None)
            compatible_with = list(e for e in edge.must_be_compatible_with_list(self.edges) if e.quest != None)

            # Call user-defined constraint solver and put the result in the quest field of the current edge
            quest = self.lore.create_quest(is_unmissable, distinct_from, compatible_with)
            if quest == None:
                raise Exception("Lore: create_quest cannot return None")
            edge.quest = quest

    def to_dot_format(self):
        s  = "digraph {\n"
        s += "    graph[compound=true];\n\n"

        for i, layer in enumerate(self.layers):
            s += "    subgraph cluster_layer_%d {" % i
            s += " ".join(str(node) for node in layer)
            s += ";}\n"

        s += "\n".join("    %s;" % edge for edge in self.edges)
        s += "\n}\n"
        return s

