from __future__ import division
import numpy as np
import sys
import time
import test_util
import graph_util


if len(sys.argv) != 3:
    print 'usage: ' + sys.argv[0] + ' <num vertices> <epsilon>'
    exit(1)

n = int(sys.argv[1])
epsilon = float(sys.argv[2])
print '%f-approximate max-flow on %d-complete graph\n' % (epsilon, n)

g = test_util.create_complete_graph(n)
b = np.zeros(g.number_of_nodes())
b[0] = -1
b[1] = 1

start_time = time.clock()
flow = graph_util.max_flow(g, b, epsilon)
stop_time = time.clock()

print 'final flow:\n',flow
print 'time:', stop_time - start_time
exit(0)
