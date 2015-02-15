from congestion_approx import CongestionApprox
from graph_util import EDGE_CAPACITY_ATTR


class TreeCongestionApprox(CongestionApprox):
  def __init__(s, graph, tree, tree_root):
    s.graph = graph.copy()
    s.tree = tree.copy()
    s.root = tree_root


  def route_flow(s, demands):
    node_flow = {}
    edge_flow = {}
    def recursive_route_flow(cur_node):
      node_flow[cur_node] = demands[cur_node]
      for neighbor in s.tree[cur_node].keys():
        if neighbor in node_flow:
          continue
        recursive_route_flow(neighbor)
        edge_flow[(cur_node, neighbor)] = node_flow[neighbor]
        node_flow[cur_node] += node_flow[neighbor]
    recursive_route_flow(s.root)
    return edge_flow


  def compute_node_potentials(s, edge_potentials):
    node_potentials = {}
    def recursive_potentials(cur_node):
      for neighbor in s.tree[cur_node].keys():
        if neighbor in node_potentials:
          continue
        node_potentials[neighbor] = (
            node_potentials[cur_node] + edge_potentials[(cur_node, neighbor)])
    node_potentials[s.root] = 0
    recursive_potentials(s.root)
    return node_potentials


  def compute_dot(s, b):
    edge_flow = s.route_flow(b)
    for u, v in s.graph.edges():
      if (u, v) not in edge_flow:
        edge_flow[(u, v)] = -edge_flow[(v, u)]
    a = s.alpha(b)
    return [
        edge_flow[(u, v)] / edict[EDGE_CAPACITY_ATTR] / a for (u, v, edict) in s.graph.edges(data=True)]


  def compute_transpose_dot(s, x):
    a = s.alpha(b)
    node_potentials = s.compute_node_potentials(
        x[(u, v)] / edict[EDGE_CAPACITY_ATTR] / a for (u, v, edict) in s.graph.edges(data=True))
    return [node_potentials[n] for n in s.graph.nodes()]


  def alpha(s, b):
    # TODO -- by routing b through the tree and computing 
    return 1.0
