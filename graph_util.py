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


def deserialize_exxon_graph(s):
  g = nx.DiGraph()
  node_id_dict = {}
  for line in s.splitlines():
    line = line.strip()
    row = line.split('\t')
    if len(row) < 2:
      print 'warning: possibly malformed input line `%s`' % line
      continue
    num_adj = int(row[1])
    if len(row) != (2 + 2 * num_adj):
      print 'warning: possibly malformed input line `%s`' % line
      continue
    for i in range(num_adj):
      edge_capacity = float(row[2 + 2*i + 1])
      if edge_capacity == 0.0:
        continue
      node = int(row[0])
      if not node in node_id_dict:
        node_id_dict[node] = len(node_id_dict)
      node_id = node_id_dict[node]
      g.add_node(node_id)

      neighbor_node = int(row[2 + 2*i])
      if not neighbor_node in node_id_dict:
        node_id_dict[neighbor_node] = len(node_id_dict)
      neighbor_node_id = node_id_dict[neighbor_node]
      g.add_edge(node_id, neighbor_node_id, {_EDGE_CAPACITY_ATTR: edge_capacity})
  return g, node_id_dict


def deserialize_exxon_node_list(s):
  return [int(line.strip()) for line in s.splitlines() if line.strip()]


def contract_edge(g, e):
  u, v = e
  g.remove_edge(u, v)
  for neighbor, edge_data in g[v].items():
    g.add_edge(u, neighbor, edge_data)
  g.remove_node(v)


def approx_min_cut_from_residuals(g, resid_map, source_vert, epsilon):
  def dfs_on_unsaturated(curnode, visited):
    if not curnode in visited:
      visited.add(curnode)
      for neighbor in g[curnode].keys():
        edge = (curnode, neighbor)
        resid = resid_map[edge]
        if resid > epsilon:
          dfs_on_unsaturated(g, neighbor, visited, resid_map)
  visited = set()
  dfs_on_unsaturated(source_vert, visited)

  cut_edges = set()
  for visited_node in visited:
    for neighbor in g[visited_node].keys():
      if not neighbor in visited:
        cut_edges.add((visited_node, neighbor))
  return cut_edges
  

def min_cut_from_residuals(g, resid_map, source_vert):
  return approx_min_cut_from_residuals(g, resid_map, source_vert, 0)
