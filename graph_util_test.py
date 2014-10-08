from __future__ import division
import graph_util
import networkx
import unittest


class GraphUtilTest(unittest.TestCase):
  def test_complete_graph(s):
    for n in range(2, 100):
      g = graph_util.complete_graph(n).to_undirected()
      for i in range(n):
        for j in range(i+1,n):
          s.assertTrue(g.has_edge(i,j))
          s.assertEqual(1, graph_util.get_edge_capacity(g, (i,j)))

  def test_edge_capacity(s):
    g = networkx.DiGraph()

    e1 = (0, 1)
    e2 = (1, 0)
    g.add_edge(*e1)
    g.add_edge(*e2)
    graph_util.set_edge_capacity(g, e1, 3.4)
    graph_util.set_edge_capacity(g, e2, 7.7)
    s.assertEqual(3.4, graph_util.get_edge_capacity(g, e1))
    s.assertEqual(7.7, graph_util.get_edge_capacity(g, e2))

  def test_edge_iters(s):
    for n in range(2, 100):
      g = graph_util.complete_graph(n)
    
      edges = [e for e in graph_util.edge_iter(g)]
      s.assertEqual(g.number_of_edges(), len(edges))

      edges_with_capacities = [e for e in graph_util.capacity_edge_iter(g)]
      s.assertEqual(g.number_of_edges(), len(edges_with_capacities))

      for i in range(g.number_of_edges()):
        u1, v1 = edges[i]
        u2, v2, _ = edges_with_capacities[i]
        s.assertEqual(u1, u2)
        s.assertEqual(v1, v2)
        s.assertIn(u1, range(g.number_of_nodes()))
        s.assertIn(v1, range(g.number_of_nodes()))


if __name__ == '__main__':
  unittest.main()
