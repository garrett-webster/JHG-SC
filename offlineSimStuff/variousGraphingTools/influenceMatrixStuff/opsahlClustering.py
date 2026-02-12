# SIMPLY do NOT worry about this
#
# import numpy as np
# import networkx as nx
#
# def OpsahlClustering(adj_matrix, alpha=0.5):
#     G = nx.from_numpy_array(adj_matrix, create_using=nx.DiGraph)
#     node_clustering = {}
#
#     for v in G.nodes():
#         out_neighbors = list(G.successors(v))
#         k_out = len(out_neighbors)
#
#         if k_out < 2:
#             node_clustering[v] = 0.0
#             continue
#
#         triangle_weight_sum = 0.0
#         possible_triplets = k_out * (k_out - 1)
#
#         for i in range(len(out_neighbors)):
#             for j in range(len(out_neighbors)):
#                 if i == j:
#                     continue
#
#                 u = out_neighbors[i]
#                 w = out_neighbors[j]
#
#                 # Only count triangle if it forms a closed loop: v → u → w → v
#                 if G.has_edge(v, u) and G.has_edge(u, w) and G.has_edge(w, v):
#                     w1 = G[v][u]['weight']
#                     w2 = G[u][w]['weight']
#                     w3 = G[w][v]['weight']
#                     triangle_weight_sum += (w1 * w2 * w3) ** alpha
#
#         # Normalize
#         clustering_value = triangle_weight_sum / possible_triplets
#         node_clustering[v] = clustering_value
#
#     global_clustering = np.mean(list(node_clustering.values()))
#     return node_clustering, global_clustering
