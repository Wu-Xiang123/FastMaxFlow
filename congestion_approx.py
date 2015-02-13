

# A congestion approximator represents (abstractly) a matrix R such that:
# ||Rb||_inf <= opt(b) <= alpha ||Rb||_inf
# IE, it hits node demand vectors, b, and gives an estimation of the congestion
# incurred along some subset of edges within some factor alpha.

class CongestionApprox:
  # For a congestion approximator R, compute Rb
  def approximate_congestion(s, b):
    return None


  # For a congestion approximator R, compute R^T b
  def approximate_potentials(s, b):
    return None

  # For a congestion approximator R, return the error term alpha
  def alpha(s, b):
    return None
