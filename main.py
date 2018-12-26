import sys
from scenariograph import GraphBuilder

gb = GraphBuilder(sys.argv[1])
graph = gb.build_action_graph("end*")

print(graph.to_dot())
