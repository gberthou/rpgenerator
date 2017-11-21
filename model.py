import random
import utils

class ScenarioNode:
    def __init__(self, node_id, layer):
        self.id = node_id
        self.layer = layer

    def __str__(self):
        return "node_%d_%d" % (self.layer, self.id)
        
class Scenario:
    def __init__(self, max_beginnings, max_endings, layer_count, max_layer_width, diversity_factor):
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

            # TODO: Fix magic value
            self.edges = self.edges.union(set(utils.erode_subgraph_of(previous_layer, nodes_to_add, False, diversity_factor)))

            # Update previous_layer
            previous_layer = nodes_to_add

            self.layers.append(nodes_to_add)

        # Finally connect last layer to endings
        # TODO: Fix magic value
        self.edges = self.edges.union(set(utils.erode_subgraph_of(previous_layer, self.endings, True, diversity_factor)))

        self.layers.append(self.endings)

    def to_dot_format(self):
        s  = "digraph {\n"
        s += "    graph[compound=true];\n\n"

        for i, layer in enumerate(self.layers):
            s += "    subgraph cluster_layer_%d {" % i
            s += " ".join(str(node) for node in layer)
            s += ";}\n"

        s += "\n".join("    %s -> %s;" % edge for edge in self.edges)
        s += "\n}\n"
        return s
        
