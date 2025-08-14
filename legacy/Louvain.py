# never got this to work the way that I wanted it to, but it might be worth looking at in the future. on the backburner for now.

# alpha = 0.5 # cause I ain't doing all that
# import numpy as np
# infl_pos = []
# infl_neg = []
#
#
# def analyze_Louvain(round_num, num_players, player_idx, popularities, influence):
#
#     # migth have to rewrite this to be a class.
#     infl_pos = np.positive(influence).clip(0)
#     infl_neg = np.negative(influence).clip(0)
#
#     A_pos = compute_adjacency(num_players)
#     A_neg = compute_neg_adjacency(num_players)
#
#
#     communities_ph1, modularity_ph1 = louvain_c_method_phase1(num_players, A_pos, A_neg)
#     communities_mega, modularity = louvain_method_phase2(communities_ph1, A_pos, A_neg)
#     communities = enumerate_community(modularity_ph1, communities_ph1, modularity, communities_mega)
#
#     coalition_target = compute_coalition_target(round_num, popularities, communities, player_idx)
#     self.printT(player_idx, " coalition_target: " + str(self.coalition_target))
#
#
#     return communities
#
#
#
#
# def compute_adjacency(num_players):
#     A = self.infl_pos.copy()
#     for i in range(num_players):
#         A[i][i] = self.infl_pos[i][i]
#         for j in range(i+1, num_players):
#             theAve = (self.infl_pos[i][j] + self.infl_pos[j][i]) / 2.0
#             theMin = min(self.infl_pos[i][j], self.infl_pos[j][i])
#             A[i][j] = (theAve + theMin) / 2.0
#             A[j][i] = A[i][j]
#
#     return A
#
# def louvain_c_method_phase1(num_players, A_pos, A_neg):
#     current_communities = list(range(num_players))
#
#     if num_players == 0:
#         communities = []
#         return communities, 0.0
#
#     the_groups = set(range(num_players))
#     com_matrix = np.identity(num_players)
#     # print(len(A_pos))
#     m_pos = sum(sum(A_pos))
#     K_pos = sum(A_pos)
#     m_neg = sum(sum(A_neg))
#     K_neg = sum(A_neg)
#     com_counts = np.ones(num_players, dtype=int)
#     hay_cambio = True
#
#     while hay_cambio:
#         hay_cambio = False
#         for i in range(num_players):
#             mx_com = current_communities[i]
#             best_dQ = 0.0
#             for j in the_groups:
#                 if current_communities[i] == j:
#                     continue
#
#                 dQ_pos = self.move_i_to_j(num_players, com_matrix, m_pos, K_pos, A_pos, i, j,
#                                           current_communities[i])
#                 dQ_neg = self.move_i_to_j(num_players, com_matrix, m_neg, K_neg, A_neg, i, j,
#                                           current_communities[i])
#                 # print("   dQ_pos: " + str(dQ_pos) + "; dQ_neg: " + str(dQ_neg))
#
#                 dQ = self.alpha * dQ_pos - (1 - self.alpha) * dQ_neg
#                 if dQ > best_dQ:
#                     mx_com = j
#                     best_dQ = dQ
#
#             if best_dQ > 0.0:
#                 com_matrix[current_communities[i]][i] = 0
#                 com_counts[current_communities[i]] -= 1
#                 if (com_counts[current_communities[i]] <= 0):
#                     the_groups.remove(current_communities[i])
#                 com_matrix[mx_com][i] = 1
#                 com_counts[mx_com] += 1
#                 current_communities[i] = mx_com
#                 hay_cambio = True
#
#     communities = []
#     for i in range(num_players):
#         if com_counts[i] > 0:
#             s = set()
#             for j in range(num_players):
#                 if com_matrix[i][j] == 1:
#                     s.add(j)
#             communities.append(s)
#
#     the_modularity = alpha * compute_modularity(num_players, current_communities, A_pos)
#     the_modularity -= (1 - alpha) * compute_modularity(num_players, current_communities, A_neg)
#
#     return communities, the_modularity
#
# def compute_neg_adjacency(num_players):
#     A = infl_neg.copy()
#     for i in range(num_players):
#         A[i][i] = infl_neg[i][i]
#         for j in range(i+1, num_players):
#             theAve = (infl_neg[i][j] + nfl_neg[j][i]) / 2.0
#             theMax = max(infl_neg[i][j], infl_neg[j][i])
#             A[i][j] = theMax #(theAve + theMax) / 2.0
#             A[j][i] = A[i][j]
#
#     return A
#
# def louvain_method_phase2(communities_ph1, A_pos, A_neg):
#     num_communities = len(communities_ph1)
#     # print("    num_communities: " + str(num_communities))
#
#     # Lump individuals into communities: compute B_pos and B_neg
#     B_pos = np.zeros((num_communities, num_communities), dtype=float)
#     B_neg = np.zeros((num_communities, num_communities), dtype=float)
#
#     for i in range(num_communities):
#         for j in range(num_communities):
#             for k in communities_ph1[i]:
#                 for m in communities_ph1[j]:
#                     B_pos[i][j] += A_pos[k][m]
#                     B_neg[i][j] += A_neg[k][m]
#
#     # print(B_pos)
#
#     return louvain_c_method_phase1(num_communities, B_pos, B_neg)
#
# def enumerate_community(modularity_ph1, communities_ph1, modularity, communities_mega):
#     if modularity > modularity_ph1:
#         communities = []
#         for m in communities_mega:
#             communities.append(set())
#             for i in m:
#                 for j in communities_ph1[i]:
#                     communities[len(communities) - 1].add(j)
#
#     else:
#         communities = communities_ph1
#
#     return communities
#
#
#
# def compute_coalition_target(round_num, popularities, communities, player_idx):
#     # compute self.coalition_target
#     if self.genes["coalitionTarget"] < 80:
#         if self.genes["coalitionTarget"] < 5:
#             return 0.05
#         else:
#             return self.genes["coalitionTarget"] / 100.0
#     elif round_num < 3:
#         return 0.51
#     else:
#         in_mx = False
#         mx_ind = -1
#         fuerza = []
#         tot_pop = sum(popularities)
#         for s in communities:
#             tot = 0.0
#             for i in s:
#                 tot += popularities[i]
#
#             fuerza.append(tot / tot_pop)
#             if mx_ind == -1:
#                 mx_ind = 0
#             elif tot > fuerza[mx_ind]:
#                 mx_ind = len(fuerza)-1
#                 if player_idx in s:
#                     in_mx = True
#                 else:
#                     in_mx = False
#
#         fuerza.sort(reverse=True)
#         self.printT(player_idx, "   fuerza: " + str(fuerza))
#         if in_mx:
#             return min(fuerza[1] + 0.05, 55)
#         else:
#             return min(fuerza[0] + 0.05, 55)
