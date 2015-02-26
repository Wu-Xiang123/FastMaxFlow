from tree_congestion_approx import TreeCongestionApprox
import networkx as nx
from graph_util import maximum_spanning_tree, EDGE_CAPACITY_ATTR

class MstCongestionApprox(TreeCongestionApprox):
  def __init__(s, g):
    mst = maximum_spanning_tree(g)
    TreeCongestionApprox.__init__(s, mst, mst.nodes()[0], g.number_of_edges())
