from __future__ import division
from graph_util import EDGE_CAPACITY_ATTR
from tree_congestion_approx import TreeCongestionApprox
import networkx as nx
import unittest


class TreeCongestionApproxTest(unittest.TestCase):
  def test_route_flow(s):
    g = nx.Graph()
    g.add_edge(0, 1)
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    g.add_edge(2, 4)
    for u, v, edict in g.edges(data=True):
      edict[EDGE_CAPACITY_ATTR] = 1.0

    demands = [-4, 0, 1, 1, 2]
    t = g
    root = 1
    tree_approx = TreeCongestionApprox(g, t, root)
    flow = tree_approx.route_flow(demands)
    s.assertEqual(-4, flow[(1, 0)])
    s.assertEqual(4, flow[(1, 2)])
    s.assertEqual(1, flow[(2, 3)])
    s.assertEqual(2, flow[(2, 4)])
    s.assertEqual(4, len(flow.keys()))

    Rb = tree_approx.compute_dot(demands)
    s.assertEqual(4, Rb[0])
    s.assertEqual(4, Rb[1])
    s.assertEqual(1, Rb[2])
    s.assertEqual(2, Rb[3])
    s.assertEqual(len(g.edges()), len(Rb))


if __name__ == '__main__':
  unittest.main()
