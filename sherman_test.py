from __future__ import division
import graph_util
import networkx as nx
import numpy as np
import numpy.linalg as la
import sherman
import unittest


class ShermanTest(unittest.TestCase):
  def test_max_flow_on_complete_graphs(s):
    epsilon = 0.1
    p = 0.8
    for n in range(8, 16):
      for i in range(10):
        g = graph_util.diluted_complete_graph(n, p)
        flow, flow_value = sherman.max_flow(g, 0, 1, epsilon)
        actual_flow_value, actual_flow = nx.ford_fulkerson(
            g.to_undirected(), 0, 1)
        s.assertGreater(flow_value, (1.0 - epsilon) * actual_flow_value)
        s.assertLess(flow_value, (1.0 + epsilon) * actual_flow_value)


if __name__ == '__main__':
  unittest.main()
