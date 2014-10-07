from __future__ import division
import numpy as np
import numpy.linalg as la
import math
from soft_max import soft_max,grad_soft_max


class ShermanMaxFlowConductance:
  def __init__(s, g):
    s.graph = g
    s.vertex_degrees = [1.0 * g.degree(v) for v in g.nodes()]
    s.edge_capacities = [
        1.0 * edge_data['capacity'] for _, _, edge_data in
            g.edges(data=True)]
    s.alpha = (g.number_of_nodes() + 1) / (g.number_of_nodes())

    
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
    for edge_from, edge_to, edge_data in s.graph.edges(data=True):
      edge_i = edge_data['number']
      excess[edge_from] -= x[edge_i]
      excess[edge_to] += x[edge_i]
    return excess


  def compute_BT(s, x):
    potentials = np.zeros(s.graph.number_of_edges())
    for edge_from, edge_to, edge_data in s.graph.edges(data=True):
      edge_i = edge_data['number']
      potentials[edge_i] = -x[edge_from] + x[edge_to]
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
    k1 = 3.5
    k2 = 2/7

    scaling = 1
    f = np.zeros(m)
    b = np.array(demands)
    norm_Rb = la.norm(s.compute_R(b), np.inf)
    scaling *= abs(k1 * math.log(n) / (2 * s.alpha * norm_Rb))
    b = b * scaling

    while True:
      while s.phi(f, b) < k1 * math.log(n):
        f = (k1 + 1) / k1 * f
        b = (k1 + 1) / k1 * b
        scaling *= (k1 + 1) / k1

      grad_phi_f = s.grad_phi(f, b)
      delta = la.norm(s.compute_C(grad_phi_f), 1)
      if delta >= k2 * epsilon:
          f -= delta / (1 + 4 * s.alpha**2) * s.compute_C(
              np.sign(grad_phi_f))
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


  def max_flow(s, source_i, sink_i, epsilon):
    demands = np.zeros(s.graph.number_of_nodes())
    demands[source_i] = -1
    demands[sink_i] = 1
    
    flow = s.min_congestion_flow(demands, epsilon)
    max_edge_congestion = la.norm(s.compute_Cinv(flow), np.inf)
    return flow / max_edge_congestion


def get_edge_capacities(g):
  return [edge_data['capacity'] for _, _, edge_data in g.edges(data=True)]


def get_edge_capacity(g, e):
  u, v = e
  return g[u][v]['capacity']


def set_edge_capacity(g, e, cap):
  u, v = e
  g[u][v]['capacity'] = cap


def get_edge_number(g, e):
  u, v = e
  return g[u][v]['number']


def set_edge_number(g, e, num):
  u, v = e
  g[u][v]['number'] = num


def min_congestion_flow(g, demands, epsilon):
  conductance_cong_approx = ShermanMaxFlowConductance(g)
  return conductance_cong_approx.min_congestion_flow(demands, epsilon)


def max_flow(g, source_i, sink_i, epsilon):
  conductance_cong_approx = ShermanMaxFlowConductance(g)
  return conductance_cong_approx.max_flow(source_i, sink_i, epsilon)
