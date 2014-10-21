from __future__ import division
import graph_util
import networkx as nx
import numpy as np
import numpy.testing as npt
import numpy.linalg as la
import sherman
import unittest


class ShermanTest(unittest.TestCase):
  def test_compute_C(s):
    g = graph_util.complete_graph(5)
    graph_util.set_edge_capacity(g, (0, 1), 12)
    graph_util.set_edge_capacity(g, (0, 2), 13)
    congestion_approximator = sherman.ShermanMaxFlowConductance(g)

    x = np.ones(g.number_of_edges())
    x[0] = 2
    x[1] = 3
    expected = np.ones(g.number_of_edges())
    expected[0] = 2 * 12
    expected[1] = 3 * 13
    npt.assert_array_equal(expected, congestion_approximator.compute_C(x))

    expected[0] = 2 / 12
    expected[1] = 3 / 13
    npt.assert_array_equal(expected, congestion_approximator.compute_Cinv(x))


  def test_compute_B(s):
    g = graph_util.complete_graph(5)
    congestion_approximator = sherman.ShermanMaxFlowConductance(g)

    x = np.zeros(g.number_of_edges())
    x[0] = 2
    x[1] = -1.2
    x[2] = -0.1
    expected = np.zeros(g.number_of_nodes())
    expected[0] = -2 + 1.2 + 0.1
    expected[1] = 2
    expected[2] = -1.2
    expected[3] = -0.1
    actual_Bx = congestion_approximator.compute_B(x)
    npt.assert_array_equal(expected, actual_Bx)

    # TODO test BT


  def test_compute_R(s):
    # TODO
    # TODO test RT
    return


  def test_max_flow_on_complete_graphs(s):
    epsilon = 0.1
    n = 10
    for p in [0.7, 0.8, 0.9, 1.0]:
      for i in range(100):
        g = graph_util.diluted_complete_graph(n, p)
        if not g.has_edge(0, 1):
          g.add_edge(0, 1, {'capacity': 1})
        flow, flow_value = sherman.max_st_flow(g, 0, 1, epsilon)
        actual_flow_value, actual_flow = nx.ford_fulkerson(
            g.to_undirected(), 0, 1)
        s.assertGreater(flow_value, (1.0 - epsilon) * actual_flow_value)
        s.assertLess(flow_value, (1.0 + epsilon) * actual_flow_value)


if __name__ == '__main__':
  unittest.main()
