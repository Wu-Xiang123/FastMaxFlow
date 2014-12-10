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


  def test_cut_from_flow_easy_case(s):
    g = networkx.DiGraph()
    g.add_edge('a', 'b')
    g.add_edge('b', 'd')
    g.add_edge('a', 'c')
    g.add_edge('c', 'd')

    source = 'a'
    residuals = {
        ('a', 'b'): 1,
        ('a', 'c'): 0,
        ('b', 'd'): 0,
        ('c', 'd'): 1,
    }

    cut_edges = graph_util.min_cut_from_residuals(g, residuals, source)
    s.assertItemsEqual(cut_edges, set([('a', 'c'), ('b', 'd')]))


  def test_cut_from_flow(s):
    g = networkx.DiGraph()
    for node in ['b', 'c', 'd']:
      g.add_edge('a', node)
      g.add_edge(node, 'e')
    g.add_edge('e', 'f')
    for node in ['g', 'h', 'i']:
      g.add_edge('f', node)
      g.add_edge(node, 'j')

    source = 'a'
    saturated_edges = [('a', 'c'), ('c', 'e'), ('d', 'e'), ('e', 'f')]

    residuals = dict((e, 1) for e in g.edges())
    residuals.update(dict((e, 0) for e in saturated_edges))

    cut_edges = graph_util.min_cut_from_residuals(g, residuals, source)
    s.assertItemsEqual(cut_edges, set([('e', 'f')]))


if __name__ == '__main__':
  unittest.main()
