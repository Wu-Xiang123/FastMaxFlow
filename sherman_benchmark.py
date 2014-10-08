from __future__ import division
import numpy as np
import sys
import time
import graph_util
import sherman


if len(sys.argv) != 3:
  print 'usage: ' + sys.argv[0] + ' <num vertices> <epsilon>'
  exit(1)

n = int(sys.argv[1])
epsilon = float(sys.argv[2])
print '%f-approximate max-flow on %d-complete graph\n' % (epsilon, n)

g = graph_util.complete_graph(n)
print 'n:',n
print 'm:', g.number_of_edges()

start_time = time.clock()
flow, _ = sherman.max_flow(g, 0, 1, epsilon)
stop_time = time.clock()

print 'final flow:\n',flow
print 'time:', stop_time - start_time
exit(0)
