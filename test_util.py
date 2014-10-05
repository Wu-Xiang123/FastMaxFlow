from __future__ import division
import networkx as nx
import numpy as np
import graph_util


def create_complete_graph(n):
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from([(i, j) for i in range(n) for j in range(i+1, n)])
    i = 0
    for e_from, e_to in G.edges():
        graph_util.set_edge_capacity(G, (e_from, e_to), 1)
        graph_util.set_edge_number(G, (e_from, e_to), i)
        i += 1
    return G
