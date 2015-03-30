from __future__ import division
import numpy as np
import networkx as nx
import sys
import time
import graph_util
from graph_util import EDGE_CAPACITY_ATTR
import sherman
import sparsification


if len(sys.argv) != 6:
  print 'usage: ' + sys.argv[0] + ' <fulkerson|sherman> <graph file> <source node list file> <sink node list file> <epsilon>'
  exit(1)

algorithm = sys.argv[1]
graph_file = sys.argv[2]
source_file = sys.argv[3]
sink_file = sys.argv[4]
epsilon = float(sys.argv[5])

g = graph_util.deserialize_exxon_graph(open(graph_file).read())
for i in range(max(g.nodes())):
  g.add_node(i)
for u, v, c in graph_util.capacity_edge_iter(g):
  if c == 0.0:
    g.remove_edge(u, v)
sources = set(graph_util.deserialize_exxon_node_list(open(source_file).read()))
sinks = set(graph_util.deserialize_exxon_node_list(open(sink_file).read()))

print 'n:', g.number_of_nodes()
print 'm:', g.number_of_edges()


min_weight_edge = min(edict[EDGE_CAPACITY_ATTR] for (u, v, edict) in g.edges(data=True))
max_weight_edge = max(edict[EDGE_CAPACITY_ATTR] for (u, v, edict) in g.edges(data=True))
scaling = 1.0 / min_weight_edge
print 'prescaling: %f' % scaling
for u, v, data in g.edges(data=True):
  data[graph_util.EDGE_CAPACITY_ATTR] *= scaling

print 'sparsifying...'
sparse_g = sparsification.sparsify(g.to_undirected(), epsilon)
print 'sparsification factor:', sparse_g.number_of_edges() / g.number_of_edges()

for u, v, data in g.edges(data=True):
  data[graph_util.EDGE_CAPACITY_ATTR] /= scaling

demands = np.array([(-1 if v in sources else (1 if v in sinks else 0)) for v in g.nodes()])

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
    demand_dict[s] = -1
  for s in sinks:
    demand_dict[s] = 1
  
  g = g.to_undirected()
  super_source = g.number_of_nodes()
  g.add_node(super_source)
  super_sink = g.number_of_nodes()
  g.add_node(super_sink)
  for s in sources:
    g.add_edge(super_source, s, {'capacity': 1})
  for s in sinks:
    g.add_edge(s, super_sink, {'capacity': 1})
  print 'starting fulkerson'
  
  start_time = time.clock()
  flow_val, flow = nx.ford_fulkerson(g, super_source, super_sink)
  stop_time = time.clock()
  print 'Networkx flow value:',flow_val
  print 'Networkx time:', stop_time - start_time
else:
  print 'Unknown algorithm: `%s`' % algorithm
  exit(1)

exit(0)