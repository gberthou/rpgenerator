import random
import math

def iteration_subgraph_of(previous_layer, new_layer, is_end_layer):
    previous_layer = list(previous_layer)
    new_layer      = list(new_layer)

    # First, all edges between previous_layer nodes and new_layer nodes
    ret = list((i, j) for j in new_layer for i in previous_layer)

    if not is_end_layer:
        # Then, all edges between new_layer nodes
        ret.extend(list((new_layer[i], new_layer[j]) for i in range(len(new_layer)) for j in range(len(new_layer)) if i != j))
    return ret

def is_in_graph_from(element, graph):
    return element in set(edge[0] for edge in graph)

def is_in_graph_to(element, graph):
    return element in set(edge[1] for edge in graph)

def erode_subgraph_of(previous_layer, new_layer, is_end_layer, diversity_factor):
    graph = iteration_subgraph_of(previous_layer, new_layer, is_end_layer)
    random.shuffle(graph)

    unremovable_edges = list()

    max_edges_to_remove = int(math.ceil((1. - diversity_factor) * len(graph)))

    for i in range(max_edges_to_remove):
        # Copy graph without head
        attempt_graph = list(graph)[1:]
        attempt_graph.extend(unremovable_edges)
        accept = True

        # If removing the first edge makes a node from previous_layer a leaf, then accept = False as we want only ending nodes to be leaves
        for node_from in previous_layer:
            if not is_in_graph_from(node_from, attempt_graph):
                accept = False
                break

        if accept:
            # If removing the first edge makes a node from new_layer unreachable, then accept = False
            for node_to in new_layer:
                if not is_in_graph_to(node_to, attempt_graph):
                    accept = False
                    break

        if not accept:
            unremovable_edges.append(graph[0])

        # Regardless of edge being unremovable, pop head
        graph = graph[1:]

    # /!\ At this point there might be edges from previous_layer nodes to
    # new_layer nodes that are removed but the subgraph is still valid since
    # All nodes from new_layer are guaranteed to be reachable.
    # For instance:
    #   0_0 -> 1_1
    #   1_1 -> 1_2
    # Here 1_2 is not connected to any node from layer 0, but it is reachable
    # from another node so it is still valid.
    # As a result this situation would create a "sublayer" but it does not break
    # the scenario.

    # Finally add unremovable edges back
    graph.extend(unremovable_edges)

    return graph

