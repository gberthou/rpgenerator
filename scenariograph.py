import re

def remove_space(s):
    tmp = re.sub(r"^\s+", "", s)
    return re.sub(r"\s+$", "", tmp)

class Action:
    def __init__(self, name, creates):
        self.name    = str(name)
        self.creates = set(creates)

class Target:
    def __init__(self, name, deps):
        self.name = str(name)
        self.deps = set(deps)

class Node:
    def __init__(self, n, initial = False, final = False):
        self.n = n
        self.past_actions = set()
        self.isinitial = initial
        self.isfinal = final

    def same_actions_as(self, other):
        return self.past_actions == other.past_actions

class Edge:
    def __init__(self, node_from, node_to, label):
        self.node_from = node_from
        self.node_to   = node_to
        self.label     = label

    def same_as(self, other):
        return self.node_from == other.node_from and self.node_to == other.node_to and self.label == other.label

class Graph:
    def __init__(self):
        self.nodes = set()
        self.edges = set()
        self.node_id = 0

        self.initial_nodes = set()

    def create_node(self, initial = False, final = False):
        tmp = Node(self.node_id, initial, final)
        self.nodes |= {tmp}
        self.node_id += 1
        return tmp

    def create_edge(self, node_from, node_to, label):
        self.edges |= {Edge(node_from, node_to, label)}

    def remove_useless_edges_and_nodes(self):
        useless_edges = set(i for i in self.edges if i.label == "")
        for uedge in useless_edges:
            incoming_edges = set(i for i in self.edges if i.node_to == uedge.node_from)
            for iedge in incoming_edges:
                iedge.node_to = uedge.node_to

        self.nodes -= set(i.node_from for i in useless_edges)
        self.edges -= useless_edges

    def annotate_nodes(self, nodes, actions):
        # TODO: compute and use dominance graph

        for node in nodes:
            node.past_actions |= actions
            for edge in self.edges:
                if edge.node_from == node:
                    self.annotate_nodes({edge.node_to}, actions | {edge.label})

    def replace_node(self, node_to_replace, node):
        for edge in self.edges:
            if edge.node_from == node_to_replace:
                edge.node_from = node
            if edge.node_to == node_to_replace:
                edge.node_to = node

        self.nodes -= {node_to_replace}

    # Nodes must be annotated before (cf. annotate_nodes)
    def remove_identical_nodes(self):
        oldnodes = set(self.nodes)
        for node in oldnodes:
            if node not in self.nodes:
                continue

            for other in self.nodes - {node}:
                if node.same_actions_as(other):
                    self.replace_node(other, node)

    # Must be called after remove_identical_nodes
    def remove_identical_edges(self):
        oldedges = set(self.edges)
        for edge in oldedges:
            if edge not in self.edges:
                continue

            self.edges -= set(i for i in self.edges-{edge} if i.same_as(edge))

    def finalize(self):
        self.remove_useless_edges_and_nodes()
        self.annotate_nodes(self.initial_nodes, set())
        self.remove_identical_nodes()
        self.remove_identical_edges()

    def to_dot(self):

        ret = "digraph g {\n"

        ret += "    "
        ret += "\n    ".join("node [shape = doublecircle] %d;" % n.n for n in self.nodes if n.isfinal)
        ret += "\n    node [shape = circle];\n"

        ret += "    "
        ret += "\n    ".join('%d -> %d [label="%s"];' % (e.node_from.n, e.node_to.n, e.label) for e in self.edges) + "\n"
        ret += "}\n"

        return ret

class GraphBuilder:
    def __init__(self, filename):
        self.targets = list()
        self.endings = list()
        self.actions = list()

        self.from_file(filename)

        self.target_names   = set(i.name for i in self.targets)
        self.creation_names = set()
        for action in self.actions:
            self.creation_names |= action.creates

    def from_file(self, filename):
        # TODO: Use a real grammar
        with open(filename, "r") as f:
            for line in f:
                if "->" in line:  # action
                    ops = line.split("->")
                    name = remove_space(ops[0])
                    outs = list(remove_space(i) for i in ops[1].split())
                    self.actions.append(Action(name, outs))
                elif ":" in line: # target
                    ops = line.split(":")
                    name = remove_space(ops[0])
                    deps = list(remove_space(i) for i in ops[1].split())
                    target = Target(name, deps)
                    self.targets.append(target)

                    if name[-1] == "*": # ending
                        self.endings.append(target)

    def flatten_deps(self, deps):
        if deps & self.creation_names:
            return deps

        # Here, everything is target
        ret = set()
        for targetname in deps:
            ret |= self.flatten_deps(list(i for i in self.targets if i.name == targetname)[0].deps)
        return ret

    def rec_action_graph(self, remaining_deps, graph, actionname, parent):
        deps = self.flatten_deps(remaining_deps)

        if parent:
            node = graph.create_node(final = False)
            graph.create_edge(node, parent, actionname)
        else:
            node = graph.create_node(final = True)

        actions = set(i for i in self.actions if len(i.creates & remaining_deps))
        targets = set(i for i in self.targets if i.name in remaining_deps)
        if len(actions):
            for action in actions:
                self.rec_action_graph(deps - action.creates, graph, action.name, node)
        elif len(targets):
            for target in targets:
                self.rec_action_graph(deps - {target.name}, graph, "", node)
        else:
            graph.initial_nodes |= {node}

    def build_action_graph(self, name):
        if not name in self.target_names:
            return set()

        graph = Graph()
        self.rec_action_graph({name}, graph, "", None)

        return graph
