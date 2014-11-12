import math
import networkx as nx
import Queue as queue

from fibonacci_heap_mod import Fibonacci_heap
from graph_util import *


_EDGE_CAPACITY_ATTR = 'capacity'


# Graph compression/sparsification --
#   Reduce a graph with N vertices and M edges to
#   one with N vertices and O(n log n) edges, in linear
#   time, with high probability 1 - O(n ** -d)
#
# "Randomized Approximation Schemes for Cuts and Flows in Capacitated Graphs"
#   Benczur, Karger 2008


def sparsify(g, epsilon):
  compressed_g = nx.Graph()
  n = g.number_of_nodes()
  edge_strength = estimation(g.copy(), 1)
  print 'edge strength estimates:', edge_strength
  d = 1
  compression_factor = 3 * (d + 4) * math.log(n) / (epsilon ** 2)
  for u, v, edge_data in g.edges(data=True):
    w = edge_data[_EDGE_CAPACITY_ATTR]
    p_e = min(1, compression_factor / edge_strength[(u, v)])
    if p_e is 1 or random.random() < p_e:
      # keep the edge
      compressed_g.add_edge(u, v, {_EDGE_CAPACITY_ATTR: w / p_e})
  return compressed_g


def estimation(h, k):
  print 'estimation()'
  print 'h:', h.edges()
  print 'k:', k
  approx_edge_strength = {}
  edges = weak_edges(h.copy(), 2*k)
  print str(2*k) + '-weak edges:', edges
  for e in edges:
    approx_edge_strength[e] = k
    h.remove_edge(*e)
  for connected_comp in nx.connected_components(h):
    print 'comp:', connected_comp
    if len(connected_comp) <= 1:
      continue
    approx_edge_strength.update(estimation(h.subgraph(connected_comp), 2*k))
  return approx_edge_strength


def weak_edges(g, k):
  edges = set()
  print 'for i in range(%d)' % int(math.log(g.number_of_nodes(), 2)+0.5)
  for i in range(int(math.log(g.number_of_nodes(), 2)+0.5)):
    cert = certificate(g.copy(), 2*k)
    edges.update(cert)
    for e in cert:
      g.remove_edge(*e)
  return edges


def certificate(g, k):
  forest = nagamochi_forest(g)
  if k in forest:
    return nagamochi_forest(g)[k]
  else:
    return set()


def weighted_certificate(g, k):
  edges = set()
  capforest = nagamochi_capforest(g)
  for key, val in capforest.items():
    if val <= k:
      edges.add(key)
  return edges


def partition(g, k):
  if g.number_of_edges() <= 2 * k * (g.number_of_nodes() - 1):
    return set(g.edges())
  else:
    cert = certificate(g, k)
    for e in cert:
      contract_edge(g, e)
    partition(g, k)


# Finding forests of k-connected subtrees
#     "Computing Edge-Connectivity in Multigraphs and Capacitated Graphs"
#         Hiroshi Nagamochi, Toshihide Ibaraki 1992


def nagamochi_forest(g):
  unscanned_edges = set(edge_iter(g))
  r = dict((node, 0) for node in g)

  graph_to_heap = {}
  unscanned_r_heap = Fibonacci_heap()
  for node in g:
    graph_to_heap[node] = unscanned_r_heap.enqueue(node, 0)

  partitions = {}

  while unscanned_r_heap:
    x_heap_node = unscanned_r_heap.dequeue_min()
    x = x_heap_node.get_value()
    graph_to_heap[x] = None
    for y in g[x].keys():
      edge = (x, y)
      if not edge in unscanned_edges:
        continue
      unscanned_edges.remove(edge)
      unscanned_edges.remove((y, x))

      k = r[y] + 1
      if not k in partitions:
        partitions[k] = set()
      partitions[k].add(edge)

      if r[x] is r[y]:
        r[x] += 1
      r[y] += 1
      y_heap_node = graph_to_heap[y]
      y_prio = y_heap_node.get_priority()
      unscanned_r_heap.decrease_key(y_heap_node, y_prio - 1)
  return partitions


def nagamochi_capforest(g):
  unscanned_edges = set(edge_iter(g))
  r = dict((node, 0) for node in g)
  q = {}

  graph_to_heap = {}
  unscanned_r_heap = Fibonacci_heap()
  for node in g:
    graph_to_heap[node] = unscanned_r_heap.enqueue(node, 0)

  while unscanned_r_heap:
    x_heap_node = unscanned_r_heap.dequeue_min()
    x = x_heap_node.get_value()
    for y, edge_data in g[x].items():
      edge = (x, y)
      if not edge in unscanned_edges:
        continue
      unscanned_edges.remove(edge)
      unscanned_edges.remove((y, x))
      c = edge_data[_EDGE_CAPACITY_ATTR]
      
      q[edge] = r[y] + c
      r[y] = r[y] + c
      y_heap_node = graph_to_heap[y]
      y_prio = y_heap_node.get_priority()
      unscanned_r_heap.decrease_key(y_heap_node, y_prio - c)
  return q
