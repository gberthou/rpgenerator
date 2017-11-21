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

def exists_path_from_old_layer_to(old_layer, node, unremovable_edges, attempt_graph):
    for old_node in old_layer:
        edge = (old_node, node)
        if edge in unremovable_edges or edge in attempt_graph:
            return True
    return False

def erode_subgraph_of(previous_layer, new_layer, is_end_layer, diversity_factor):
    graph = iteration_subgraph_of(previous_layer, new_layer, is_end_layer)
    random.shuffle(graph)

    unremovable_edges = list()

    max_edges_to_remove = int(math.ceil((1. - diversity_factor) * len(graph)))

    i = 0
    while i < max_edges_to_remove and len(graph) > 0:
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
            # If removing the first edge makes a node from new_layer unreachable from all previous_layer nodes then accept = False
            for node_to in new_layer:
                if not exists_path_from_old_layer_to(previous_layer, node_to, unremovable_edges, attempt_graph):
                    accept = False
                    break

        if not accept:
            unremovable_edges.append(graph[0])
        else:
            i += 1

        # Regardless of edge being unremovable, pop head
        graph = graph[1:]

    # Finally add unremovable edges back
    graph.extend(unremovable_edges)

    return graph

