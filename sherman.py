from __future__ import division
import numpy as np
import numpy.linalg as la
import math
import graph_util
from soft_max import soft_max, grad_soft_max


class ShermanMaxFlowConductance:
  def __init__(s, g):
    s.graph = g
    s.vertex_degrees = [1.0 * g.degree(v) for v in g.nodes()]
    s.edge_capacities = [1.0 * c for c in graph_util.get_edge_capacities(g)]
    # TODO generalize beyond just complete graphs
    s.alpha = 1.0
    #s.alpha = 1.0 / graph_util.estimate_conductance(g, 100)
    # print 'estimate that alpha = inv conductance is', s.alpha

    
  def compute_R(s, x):
    return np.multiply(x, np.reciprocal(s.vertex_degrees))


  def compute_RT(s, x):
    return s.compute_R(x)


  def compute_C(s, x):
    return np.multiply(x, s.edge_capacities)


  def compute_Cinv(s, x):
    return np.multiply(x, np.reciprocal(s.edge_capacities))


  def compute_B(s, x):
    excess = np.zeros(s.graph.number_of_nodes())
    edge_i = 0
    for edge_from, edge_to in graph_util.edge_iter(s.graph):
      excess[edge_from] -= x[edge_i]
      excess[edge_to] += x[edge_i]
      edge_i += 1
    return excess


  def compute_BT(s, x):
    potentials = np.zeros(s.graph.number_of_edges())
    edge_i = 0
    for edge_from, edge_to in graph_util.edge_iter(s.graph):
      potentials[edge_i] = -x[edge_from] + x[edge_to]
      edge_i += 1
    return potentials


  def phi(s, f, b):
    resid = b - s.compute_B(f)
    return soft_max(s.compute_Cinv(f)) + soft_max(
        2 * s.alpha * s.compute_R(resid))


  def grad_phi(s, f, b):
    x1 = s.compute_Cinv(f)
    p1 = grad_soft_max(x1)
 
    resid = b - s.compute_B(f)
    x2 = 2 * s.alpha * s.compute_R(resid)
    p2 = grad_soft_max(x2)
 
    return s.compute_Cinv(p1) - 2 * s.alpha * (
        s.compute_BT(s.compute_RT(p2)))


  def almost_route(s, demands, epsilon):
    n = s.graph.number_of_nodes()
    m = s.graph.number_of_edges()

    # TODO: fiddle around with these constants. They come from
    #   (loose) bounds in the correctness proof, and have a
    #   significant effect on performance.
    k1 = 7 / 2 / epsilon
    k2 = 2 / 7

    scaling = 1
    f = np.zeros(m)
    y = np.array(f)
    b = np.array(demands)
    norm_Rb = la.norm(s.compute_R(b), np.inf)
    scaling *= abs(k1 * math.log(n) / (2 * s.alpha * norm_Rb))
    b = b * scaling
    iters = 1

    while True:
      while s.phi(f, b) < k1 * math.log(n):
        f = (k1 + 1) / k1 * f
        y = (k1 + 1) / k1 * y
        b = (k1 + 1) / k1 * b
        scaling *= (k1 + 1) / k1

      grad_phi_y = s.grad_phi(y, b)
      delta = la.norm(s.compute_C(grad_phi_y), 1)
      if delta >= k2 * epsilon:
          f_prev = np.array(f)
          f = y - delta / (1 + 4 * s.alpha**2) * s.compute_C(
              np.sign(grad_phi_y))
          y = f + (iters - 1) / (iters + 2) * (f - f_prev)
          iters += 1
      else:
        return f / scaling


  def min_congestion_flow(s, demands, epsilon):
    n = s.graph.number_of_nodes()
    m = s.graph.number_of_edges()
    f_total = np.zeros(m)
    for i in range(int(math.log(2*m))):
      f = s.almost_route(demands, epsilon)
      demands = demands - s.compute_B(f)
      epsilon = 0.5
      f_total += f
    return f_total


  def max_flow(s, demands, epsilon):
    flow = s.min_congestion_flow(demands, epsilon)
    max_edge_congestion = la.norm(s.compute_Cinv(flow), np.inf)
    max_flow = flow / max_edge_congestion
    max_flow_value = 0
    sink_nodes = np.maximum(np.sign(demands), np.zeros(len(demands)))
    max_flow_value = np.dot(s.compute_B(max_flow), sink_nodes)
    return max_flow, max_flow_value


  def max_st_flow(s, source_i, sink_i, epsilon):
    demands = np.zeros(s.graph.number_of_nodes())
    demands[source_i] = -1
    demands[sink_i] = 1
    return s.max_flow(demands, epsilon)


def min_congestion_flow(g, demands, epsilon):
  conductance_cong_approx = ShermanMaxFlowConductance(g)
  return conductance_cong_approx.min_congestion_flow(demands, epsilon)


def max_flow(g, demands, epsilon):
  conductance_cong_approx = ShermanMaxFlowConductance(g)
  return conductance_cong_approx.max_flow(demands, epsilon)


def max_st_flow(g, s, t, epsilon):
  conductance_cong_approx = ShermanMaxFlowConductance(g)
  return conductance_cong_approx.max_st_flow(s, t, epsilon)
