from __future__ import division

import math
import networkx as nx
import Queue as queue

from fibonacci_heap_mod import Fibonacci_heap
from graph_util import *


# Graph compression/sparsification --
#   Reduce a graph with N vertices and M edges to
#   one with N vertices and O(n log n) edges, in linear
#   time, with high probability 1 - O(n ** -d)
#
# "Randomized Approximation Schemes for Cuts and Flows in Capacitated Graphs"
#   Benczur, Karger 2008


def sparsify(g, epsilon, d=0.5):
  compressed_g = nx.Graph()
  n = g.number_of_nodes()
  edge_strength = estimation(g, 1)
  compression_factor = 3 * (d + 4) * math.log(n) / (epsilon ** 2)
  for u, v, edge_data in g.edges(data=True):
    w = edge_data[EDGE_CAPACITY_ATTR]
    if (u,v) in edge_strength:
      edge_str = edge_strength[(u,v)]
    else:
      edge_str = edge_strength[(v,u)]
    p_e = min(1, compression_factor / edge_str)
    if p_e is not 1 and random.random() > p_e:
      continue
    # keep the edge
    compressed_g.add_edge(u, v, {EDGE_CAPACITY_ATTR: w / p_e})
  return compressed_g


def estimation(g, k):
  h = g.copy()
  approx_edge_strength = {}
  edges = weak_edges(h, 2*k)
  for e in edges:
    approx_edge_strength[e] = k
    h.remove_edge(*e)
  for connected_comp in nx.connected_components(h):
    if len(connected_comp) <= 1:
      continue
    approx_edge_strength.update(estimation(h.subgraph(connected_comp), 2*k))
  return approx_edge_strength


def weak_edges(g, k):
  edges = set()
  g_ = nx.MultiGraph(g)
  for i in range(int(math.log(g_.number_of_nodes(), 2)+0.5)):
    cert = partition(g_, 2*k)
    edges.update(cert)
    g_.remove_edges_from(cert)
  return edges


def certificate(g, k):
  cert = set()
  forest = nagamochi_forest(g)
  for kk, es in forest.items():
    if kk <= k:
      cert.update(es)
  return cert


def weighted_certificate(g, k):
  edges = set()
  capforest = nagamochi_capforest(g)
  for key, val in capforest.items():
    if val <= k:
      edges.add(key)
  return edges


def partition(multi_g, k):
  for u, v, edict in multi_g.edges(data=True):
    edict['original_edge'] = (u, v)

  while multi_g.number_of_edges() > 2 * k * (multi_g.number_of_nodes() - 1):
    cert = weighted_certificate(multi_g, k)
    multi_g = multigraph_contract_edges(multi_g, cert)
  return set(edict['original_edge'] for (_, _, edict) in multi_g.edges(data=True))


# Finding forests of k-connected subtrees
#     "Computing Edge-Connectivity in Multigraphs and Capacitated Graphs"
#         Hiroshi Nagamochi, Toshihide Ibaraki 1992
# Note that the Nagamochi-Ibaraki FOREST and CAPFOREST routines MUST work
# on multigraphs to be useful for Benczur's sparsification scheme.


# Return a list iterator over all the edges in a multigraph (two for each
# undirected edge, backwards and forwards) as a triple of
# (vertex, vertex, edge index)
# This makes keeping track of scanned edges easy since the triples returned
# are hashable.
def multigraph_edges_as_triples(g):
  return [(u, v, i) for (u, vdict) in g.adjacency_iter() for (v, uvdict) in vdict.items() for i in uvdict.keys()]


# This is the Nagamochi-Ibaraki FOREST routine for unit-weight multigraphs.
# It returns a dictionary of partitions E_1, E_2, ... E_|E| as described in
# Nagamochi's paper.
# The union of partitions G_k = (V, union(E_1, E_2, ... E_k)) is a
# k-edge-connected spanning subgraphs. 
def nagamochi_forest(g):
  unscanned_edges = set(multigraph_edges_as_triples(g))
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
    for y, xy_es in g[x].items():
      for i, edge_dict in xy_es.items():
        edge = (x, y, i)
        if not edge in unscanned_edges:
          continue
        unscanned_edges.remove(edge)
        unscanned_edges.remove((y, x, i))

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


# This is the Nagamochi-Ibaraki CAPFOREST routine, which is similar to above
# but for capacitated multigraphs.
# The edge capacity property is assumed to be graph_util.EDGE_CAPACITY_ATTR.
# Returns similar partitions as above, but returns them as a dictionary from
# edge triples to partition index value 'q' as described in the paper.
def nagamochi_capforest(g):
  unscanned_edges = set(multigraph_edges_as_triples(g))
  r = dict((node, 0) for node in g)
  q = {}

  graph_to_heap = {}
  unscanned_r_heap = Fibonacci_heap()
  for node in g:
    graph_to_heap[node] = unscanned_r_heap.enqueue(node, 0)

  while unscanned_r_heap:
    x_heap_node = unscanned_r_heap.dequeue_min()
    x = x_heap_node.get_value()
    for y, xy_dict in g[x].items():
      for i, edge_data in xy_dict.items():
        edge = (x, y, i)
        if not edge in unscanned_edges:
          continue
        unscanned_edges.remove(edge)
        unscanned_edges.remove((y, x, i))
        c = edge_data[EDGE_CAPACITY_ATTR]
      
        q[edge] = r[y] + c
        r[y] = r[y] + c
        y_heap_node = graph_to_heap[y]
        y_prio = y_heap_node.get_priority()
        unscanned_r_heap.decrease_key(y_heap_node, y_prio - c)
  return q
