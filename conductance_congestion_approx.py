from __future__ import division
import numpy as np
from congestion_approx import CongestionApprox


class ConductanceCongestionApprox(CongestionApprox):
  def __init__(s, g):
    s.vertex_degrees_inv = [
        1.0 / g.degree(v) if g.degree(v) > 0 else 0 for v in g.nodes()]

  
  def compute_dot(s, x):
    return np.multiply(x, s.vertex_degrees_inv)


  def compute_transpose_dot(s, x):
    return np.multiply(x, s.vertex_degrees_inv)


  def alpha(s):
    # TODO: this probably isn't quite right.
    return 1.0
