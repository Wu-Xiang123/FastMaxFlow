from __future__ import division
import numpy as np
import networkx as nx
import sys
import time
import graph_util


if len(sys.argv) != 2:
  print 'usage: ' + sys.argv[0] + ' <num vertices>'
  exit(1)

n = int(sys.argv[1])
print 'max-flow on %d-complete graph\n' % (n)

g = graph_util.complete_graph(n).to_undirected()
print 'n:',n
print 'm:', g.number_of_edges()

start_time = time.clock()
flow_val, flow = nx.ford_fulkerson(g, 0, 1, capacity='capacity')
stop_time = time.clock()

#print 'final flow:\n',flow
print 'time:', stop_time - start_time
exit(0)
