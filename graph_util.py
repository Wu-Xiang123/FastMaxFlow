from __future__ import division
import networkx as nx
import random


_EDGE_CAPACITY_ATTR = 'capacity'


def get_edge_capacities(g):
  return [c for _, _, c in capacity_edge_iter(g)]


def get_edge_capacity(g, e):
  u, v = e
  return g[u][v][_EDGE_CAPACITY_ATTR]


def set_edge_capacity(g, e, cap):
  u, v = e
  g[u][v][_EDGE_CAPACITY_ATTR] = cap


def complete_graph(n):
  return diluted_complete_graph(n, 1.0)


def diluted_complete_graph(n, p):
  g = nx.DiGraph()
  g.add_nodes_from(range(n))
  g.add_edges_from([(i, j) for i in range(n) for j in range(i+1, n) if
      random.random() < p])
  for e in g.edges():
    set_edge_capacity(g, e, 1)
  return g


def edge_iter(g):
  for n, neighbor_dict in g.adjacency_iter():
    for neighbor, _ in neighbor_dict.items():
      yield (n, neighbor)


def capacity_edge_iter(g):
  for n, neighbor_dict in g.adjacency_iter():
    for neighbor, edge_data in neighbor_dict.items():
      yield (n, neighbor, edge_data[_EDGE_CAPACITY_ATTR])


def cut_weight(g, vs):
  weight = 0
  for v in vs:
    adj_dict = g[v]
    for neighbor, data_dict in adj_dict.items():
      if not neighbor in vs:
        weight += data_dict[_EDGE_CAPACITY_ATTR]
  return weight


def set_edge_weight(g, vs):
  weight = 0
  for v in vs:
    adj_dict = g[v]
    for neighbor, data_dict in adj_dict.items():
      if (not neighbor in vs) or neighbor < v:
        weight += data_dict[_EDGE_CAPACITY_ATTR]
  return weight


def cut_conductance(g, vs):
  not_vs = set([v for v in g.nodes()]) - vs
  min_s_edge_weight = min(set_edge_weight(g, vs), set_edge_weight(g, not_vs))
  if min_s_edge_weight is 0:
    return float("inf")
  else:
    return cut_weight(g, vs) / min_s_edge_weight


def estimate_conductance(g, n_samples):
  return min([cut_conductance(g, set(
      [v for v in g.nodes() if random.random() < 0.5])) for i in range(n_samples)])
