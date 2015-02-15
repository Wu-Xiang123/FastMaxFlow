

# A congestion approximator represents (abstractly) a matrix R such that:
# ||Rb||_inf <= opt(b) <= alpha ||Rb||_inf
# IE, it hits node demand vectors, b, and gives an estimation of the congestion
# incurred along some subset of edges within some factor alpha.

class CongestionApprox:
  # For a congestion approximator R, compute R x
  def compute_dot(s, x):
    return None


  # For a congestion approximator R, compute R^T x
  def compute_transpose_dot(s, x):
    return None

  # For a congestion approximator R and demands b, return the error term alpha
  # In using ||RB||_inf to approximate the flow min congestion
  def alpha(s, b):
    return None
