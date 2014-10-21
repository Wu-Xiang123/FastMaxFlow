from __future__ import division
import numpy as np
import networkx as nx
import graph_tool
import graph_tool.all as gt
import sys
import time
import graph_util
import sherman


if len(sys.argv) != 6:
  print 'usage: ' + sys.argv[0] + ' <fulkerson|boykov|sherman> <graph file> <source node list file> <sink node list file> <epsilon>'
  exit(1)

algorithm = sys.argv[1]
graph_file = sys.argv[2]
source_file = sys.argv[3]
sink_file = sys.argv[4]
epsilon = float(sys.argv[5])

g, node_id_dict = graph_util.deserialize_exxon_graph(open(graph_file).read())
sources = graph_util.deserialize_exxon_node_list(open(source_file).read())
sinks = graph_util.deserialize_exxon_node_list(open(sink_file).read())

print 'n:', g.number_of_nodes()
print 'm:', g.number_of_edges()

demands = np.zeros(g.number_of_nodes())
for s in sources:
  demands[node_id_dict[s]] = -1
for s in sinks:
  demands[node_id_dict[s]] = 1

if algorithm == 'sherman':
  print 'starting sherman'
  start_time = time.clock()
  flow, flow_value = sherman.max_flow(g, demands, epsilon)
  stop_time = time.clock()
  print 'sherman flow:\n',flow
  print 'sherman flow value:',flow_value
  print 'sherman time:', stop_time - start_time
elif algorithm == 'fulkerson':
  demand_dict = {}
  for s in sources:
    demand_dict[node_id_dict[s]] = -1
  for s in sinks:
    demand_dict[node_id_dict[s]] = 1
  
  g = g.to_undirected()
  super_source = g.number_of_nodes()
  g.add_node(super_source)
  super_sink = g.number_of_nodes()
  g.add_node(super_sink)
  for s in sources:
    g.add_edge(super_source, node_id_dict[s], {'capacity': 1})
  for s in sinks:
    g.add_edge(node_id_dict[s], super_sink, {'capacity': 1})
  print 'starting fulkerson'
  
  start_time = time.clock()
  flow_val, flow = nx.ford_fulkerson(g, super_source, super_sink)
  stop_time = time.clock()
  print 'Networkx flow value:',flow_val
  print 'Networkx time:', stop_time - start_time
elif algorithm == 'boykov':
  g2 = gt.Graph(directed=True)
  g2.add_vertex(g.number_of_nodes())
  cap_dict = g2.new_edge_property("float")
  for u, v, c in graph_util.capacity_edge_iter(g):
    e = g2.add_edge(u, v)
    cap_dict[e] = c
    e = g2.add_edge(v, u)
    cap_dict[e] = c
  super_source = g2.add_vertex()
  super_sink = g2.add_vertex()
  for s in sources:
    e = g2.add_edge(super_source, node_id_dict[s])
    cap_dict[e] = 1
    e = g2.add_edge(node_id_dict[s], super_source)
    cap_dict[e] = 1
  for s in sinks:
    e = g2.add_edge(node_id_dict[s], super_sink)
    cap_dict[e] = 1
    e = g2.add_edge(super_sink, node_id_dict[s])
    cap_dict[e] = 1
  print 'starting boykov'

  start_time = time.clock()
  res = gt.boykov_kolmogorov_max_flow(g2, super_source, super_sink, cap_dict)
  res.a = cap_dict.a - res.a
  max_flow = sum(res[e] for e in super_sink.in_edges())
  stop_time = time.clock()
  print 'Graph-tool boykov flow value:', max_flow
  print 'Graph-tool boykov time:', stop_time - start_time
else:
  print 'Unknown algorithm: `%s`' % algorithm
  exit(1)

exit(0)
