from __future__ import division
import numpy as np
from congestion_approx import CongestionApprox


class ConductanceCongestionApprox(CongestionApprox):
  def __init__(s, g):
    s.vertex_degrees_inv = [
        1.0 / g.degree(v) if g.degree(v) > 0 else 0 for v in g.nodes()]

  
  def approximate_congestion(s, b):
    return np.multiply(b, s.vertex_degrees_inv)


  def approximate_potentials(s, b):
    return np.multiply(b, s.vertex_degrees_inv)


  def alpha(s, b):
    return 1.0
