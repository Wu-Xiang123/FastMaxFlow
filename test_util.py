from __future__ import division
import networkx as nx
import graph_util
import random


def create_complete_graph(n):
  return diluted_complete_graph(n, 1.0)


def diluted_complete_graph(n, p):
  G = nx.Graph()
  G.add_nodes_from(range(n))
  G.add_edges_from([(i, j) for i in range(n) for j in range(i+1, n) if
      random.random() < p])
  i = 0
  for e in G.edges():
    graph_util.set_edge_capacity(G, e, 1)
    graph_util.set_edge_number(G, e, i)
    i += 1
  return G
