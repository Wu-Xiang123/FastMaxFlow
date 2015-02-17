from congestion_approx import CongestionApprox
from graph_util import EDGE_CAPACITY_ATTR


class TreeCongestionApprox(CongestionApprox):
  def __init__(s, tree, tree_root, alpha):
# TODO: node to index
    s.tree = tree.copy()
    s.root = tree_root
    s.cached_dfs_edges = list(s.recursive_dfs_edges(s.root, set(), False))
    s.cached_dfs_edges_data = list(s.recursive_dfs_edges(s.root, set(), True))
    s.alpha = alpha


  def route_flow(s, demands):
    node_flow = dict(zip(s.tree.nodes(), demands))
    edge_flow = {}
    for parent, child in reversed(s.dfs_edges()):
      child_flow = node_flow[child]
      node_flow[parent] += child_flow
      edge_flow[(parent, child)] = child_flow
    return edge_flow


  def compute_node_potentials(s, edge_potentials):
    node_potentials = dict([(s.root, 0)])
    for edge, potential in zip(s.dfs_edges(), edge_potentials):
      parent, child = edge
      node_potentials[child] = node_potentials[parent] + potential
    return node_potentials


  def recursive_dfs_edges(s, cur_node, visited, data):
    if cur_node in visited:
      return
    visited.add(cur_node)
    if data:
      for neighbor, edict in s.tree[cur_node].items():
        if neighbor in visited:
          continue
        yield (cur_node, neighbor, edict)
        for e in s.recursive_dfs_edges(neighbor, visited, data):
          yield e
    else:
      for neighbor in s.tree[cur_node].keys():
        if neighbor in visited:
          continue
        yield (cur_node, neighbor)
        for e in s.recursive_dfs_edges(neighbor, visited, data):
          yield e


  def dfs_edges(s, data=False):
    if data:
      return s.cached_dfs_edges_data
    else:
      return s.cached_dfs_edges


  def compute_dot(s, b):
    flow = s.route_flow(b)
    return list(flow[(u, v)] / edict[EDGE_CAPACITY_ATTR] for (u, v, edict) in (
        s.dfs_edges(data=True)))


  def compute_transpose_dot(s, x):
    edge_potentials = (xi / edict[EDGE_CAPACITY_ATTR] for (xi, (u,v,edict)) in(
        zip(x, s.dfs_edges(data=True))))
    node_potentials = s.compute_node_potentials(edge_potentials)
    return list(node_potentials[n] for n in s.tree.nodes())


  def alpha(s):
    return s.alpha
