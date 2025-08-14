import numpy as np
import sys


class CommunityEvaluation():

    def __init__(self, _s, _modularity, _centrality, _collective_strength, _familiarity, _prosocial):
        self.s = _s
        self.modularity = _modularity
        self.centrality = _centrality
        self.collective_strength = _collective_strength
        self.familiarity = _familiarity
        self.prosocial = _prosocial

        self.score = 0.0
        self.target = 0.0


    # Change on May 9
    def compute_score(self, genes):
        self.score = 1.0
        self.score = ((100-genes["w_modularity"]) + (genes["w_modularity"] * self.modularity)) / 100.0
        self.score *= ((100-genes["w_centrality"]) + (genes["w_centrality"] * self.centrality)) / 100.0
        self.score *= ((100-genes["w_collective_strength"]) + (genes["w_collective_strength"] * self.collective_strength)) / 100.0
        self.score *= ((100-genes["w_familiarity"]) + (genes["w_familiarity"] * self.familiarity)) / 100.0
        self.score *= ((100-genes["w_prosocial"]) + (genes["w_prosocial"] * self.prosocial)) / 100.0

        # Change on May 12
        # REMOVING RANDOM
        # self.score += random.random() / 10000.0    # random tie-breaking


    def print(self):
        # print(str(self.s) + ": " + str(self.modularity))
        print()
        print("set: " + str(self.s))
        print("   modularity: " + str(self.modularity))
        print("   centrality: " + str(self.centrality))
        # cs_weight = pow(0.5, abs((self.collective_strength - self.target) / .125))
        print("   collective_strength: " + str(self.collective_strength))
        print("   familiarity: " + str(self.familiarity))
        print("   prosocial: " + str(self.prosocial))
        # print("   viability: " + str(self.viability))
        print("   score: " + str(self.score))
        print()



class GeneAgentMixin:

    # determines relationship (in size) of player_idx's group with that of the other groups
    #   -1: in same group
    #   0: (no competition) player_idx's group is much bigger
    #   1: (rivals) player_idx's group if somewhat the same size and one of us is in the most powerful group
    #   2: (fear) player_idx's group is much smaller
    def groupCompare(self, num_players, player_idx, popularities, communities):
        group_cat = np.zeros(num_players, dtype=int)
        if self.genes["groupAware"] < 50:
            # don't do anything different -- player is not group aware
            return group_cat

        comm_idx = np.zeros(num_players, dtype=int)
        poders = np.zeros(len(communities), dtype=float)
        for c in range(len(communities)):
            for i in communities[c]:
                comm_idx[i] = c
                poders[c] += popularities[i]

        mx_poder = max(poders)

        scaler = 1.3  # this is arbitary for now
        for i in range(num_players):
            if comm_idx[i] == comm_idx[player_idx]:
                group_cat[i] = -1
            elif poders[comm_idx[i]] > (scaler * poders[comm_idx[player_idx]]):
                group_cat[i] = 2
            elif ((scaler * poders[comm_idx[i]]) > poders[comm_idx[player_idx]]) and (
                    (poders[comm_idx[i]] == mx_poder) or (poders[comm_idx[player_idx]] == mx_poder)):
                group_cat[i] = 1
            elif popularities[i] > popularities[
                player_idx]:  # i'm in a bigger group, but they are more powerful than me (so we are rivals -- i use my group size to justify my attack)
                group_cat[i] = 1

        self.printT(player_idx, "\n  Compare the groups:")
        self.printT(player_idx, "        comm_idx: " + str(comm_idx))
        self.printT(player_idx, "        poders: " + str(poders))
        self.printT(player_idx, "        group_cat: " + str(group_cat) + "\n")

        return group_cat


    def defend_friend(self, player_idx, num_players, num_tokens, remaining_toks, popularities, influence,
                      selected_community, communities, group_cat):
        self.expected_defend_friend_damage = -99999

        # Change on May 5
        if (popularities[player_idx] <= 0) or (self.infl_pos_sumcol[player_idx] <= 0) or (
                self.genes["defendFriendPriority"] < 50):
            return (-1, 0)

        # self.printT(player_idx, "meImporta: " + str(self.me_importa))

        my_comm_vec = np.zeros(num_players, dtype=float)
        for i in selected_community:
            if (i == player_idx) or (self.me_importa[i] > 0.1):
                my_comm_vec[i] = 1.0

        # self.printT(player_idx, "\n  my_comm_vec: " + str(my_comm_vec))

        bad_marks = np.zeros(num_players, dtype=float)
        worst_ind = -1
        worst_val = 0
        for i in range(0, num_players):
            # Change on May 6
            # if (self.govPlayer[i] == 1) or (i == player_idx) or ((self.genes["attackGoodGuys"] < 50) and (self.bad_guys[i] < 0.2)) or (group_cat[i] == 2):
            # https://www.youtube.com/watch?v=MyvwacFNPxc
            if (i == player_idx) or ((self.genes["attackGoodGuys"] < 50) and (self.bad_guys[i] < 0.2)) or (
                    group_cat[i] == 2):
                continue

            # self.printT(player_idx, str(i))

            bad_marks[i] = np.dot(self.infl_neg[i], my_comm_vec)
            if bad_marks[i] > 0:
                bad_marks[i] -= np.dot(self.infl_neg[:, i], my_comm_vec)

            # Change on July 12
            if ((popularities[i] - self.gameParams["poverty_line"]) < bad_marks[i]):
                self.printT(player_idx, "   scaling back bad marks for " + str(i))
                bad_marks[i] = popularities[i] - self.gameParams["poverty_line"]

            # Change on June 16
            if (bad_marks[i] > worst_val) and (my_comm_vec[i] == 0):
                worst_ind = i
                worst_val = bad_marks[worst_ind]

        # self.printT(player_idx, "    bad_marks: " + str(bad_marks))
        # self.printT(player_idx, "    worst_ind: " + str(worst_ind))

        if (worst_ind >= 0):
            # see how many tokens I should use on this attack
            tokens_needed = num_tokens * bad_marks[worst_ind] / (
                        popularities[player_idx] * self.gameParams["steal"] * self.gameParams["alpha"])
            tokens_needed += self.keeping_strength[worst_ind] * (popularities[worst_ind] / popularities[player_idx])
            multiplicador = self.genes["defendFriendMultiplier"] / 33.0
            tokens_needed *= multiplicador
            attack_strength = np.dot(popularities, my_comm_vec) * self.inflicted_damage_ratio
            if attack_strength == 0:
                attack_strength = 1
            player_pop = popularities[player_idx]
            if player_pop == 0:
                player_pop = 1
            my_part = tokens_needed * (player_pop / attack_strength)
            # print("this is my part ", my_part)
            if my_part == float("inf"): # literally no clue where this is coming from
                my_part = 200
            cantidad = min(int(my_part + 0.5), int(((self.genes["defendFriendMax"] / 100.0) * num_tokens) + 0.5),
                           remaining_toks)
            # self.printT(player_idx, "    consider attacking player " + str(worst_ind) + " with " + str(my_part) + "; reduced = " + str(cantidad))
            # self.printT(player_idx, "    tokens_needed: " + str(tokens_needed))
            if (cantidad >= (my_part - 1)) and (tokens_needed > 0):
                # see if the attack is a good idea
                # Change on June 6
                gain = (tokens_needed * popularities[player_idx]) - (
                            popularities[worst_ind] * self.keeping_strength[worst_ind])
                steal_ROI = (gain * self.gameParams["steal"]) / (tokens_needed * popularities[player_idx])
                imm_gain_per_token = (steal_ROI - self.ROI) * popularities[player_idx] * self.gameParams["alpha"]
                # self.printT(player_idx, "    steal_ROI: " + str(steal_ROI))
                # self.printT(player_idx, "    gain: " + str(gain))

                # Change on May 12
                if (group_cat[worst_ind] == 0) and (self.genes["groupAware"] >= 50):
                    # defend more violently against weaker groups (if group aware)
                    vengence_advantage = imm_gain_per_token + 2.0 * ((gain * self.gameParams["alpha"]) / tokens_needed)
                else:
                    vengence_advantage = imm_gain_per_token + (gain * self.gameParams["alpha"]) / tokens_needed
                # self.printT(player_idx, "    imm_gain_per_token: " + str(imm_gain_per_token) + "; vengence_advantage = " + str(vengence_advantage))

                if vengence_advantage > 0.0:
                    self.expected_defend_friend_damage = gain * self.gameParams["alpha"] * self.gameParams[
                        "steal"] / num_tokens
                    return (worst_ind, cantidad)

        return (-1, 0)


    def take_vengence(self, round_num, player_idx, num_players, selected_community, num_tokens, tokens_remaining,
                      popularities, influence):
        # Change on May 5
        if (popularities[player_idx] <= 0.0) or (self.genes["vengencePriority"] < 50):
            return (-1, 0)

        multiplicador = self.genes["vengenceMultiplier"] / 33.0

        # Change on June 21
        vengence_max = min(num_tokens * self.genes["vengenceMax"] / 100.0, tokens_remaining)

        ratio_predicted_steals = 1.0
        predicted_steals = sum(np.negative(self.attacks_with_me).clip(0))
        if self.attacks_with_me[player_idx] < 0:
            ratio_predicted_steals = predicted_steals / (-self.attacks_with_me[player_idx])

        vengence_possibilities = []
        for i in range(0, num_players):
            if (i == player_idx):
                continue

            if (influence[i][player_idx] < 0.0) and (-influence[i][player_idx] > (0.05 * popularities[player_idx])) and (
                    influence[i][player_idx] < influence[player_idx][i]) and (popularities[i] > 0.01):
                keeping_strength_w = self.keeping_strength[i] * (popularities[i] / popularities[player_idx])
                theScore = num_tokens * ((influence[i][player_idx] - influence[player_idx][i]) / (
                            popularities[player_idx] * self.gameParams["steal"] * self.gameParams["alpha"]))
                cantidad = int(min(-1.0 * (theScore - keeping_strength_w) * multiplicador, vengence_max) + 0.5)

                # Change on July 12
                if cantidad == 0:
                    continue

                my_weight = popularities[player_idx] * cantidad
                ratio = ratio_predicted_steals
                ratio2 = (my_weight + ((self.others_attacks_on[i] / self.gameParams["alpha"]) * num_tokens)) / my_weight
                if ratio2 > ratio_predicted_steals:
                    ratio = ratio2
                gain = my_weight - (popularities[i] * self.keeping_strength[i] / ratio)
                while ((((gain * ratio) / num_tokens) * self.gameParams["alpha"] * self.gameParams["steal"]) > (
                        popularities[i] - self.gameParams["poverty_line"])) and (cantidad > 0):
                    cantidad -= 1
                    if cantidad == 0:
                        break

                    my_weight = popularities[player_idx] * cantidad
                    ratio = ratio_predicted_steals
                    ratio2 = (my_weight + ((self.others_attacks_on[i] / self.gameParams["alpha"]) * num_tokens)) / my_weight
                    if ratio2 > ratio_predicted_steals:
                        ratio = ratio2
                    gain = my_weight - (popularities[i] * self.keeping_strength[i] / ratio)
                if cantidad == 0:
                    continue

                steal_ROI = (gain * self.gameParams["steal"]) / (cantidad * popularities[player_idx])
                damage = (gain / num_tokens) * self.gameParams["steal"] * self.gameParams["alpha"]

                imm_gain_per_token = (steal_ROI - self.ROI) * ((cantidad / num_tokens) * popularities[player_idx]) * \
                                     self.gameParams["alpha"]
                imm_gain_per_token /= cantidad

                vengence_advantage = imm_gain_per_token + damage / cantidad

                if vengence_advantage > 0.0:
                    vengence_possibilities.append((i, vengence_advantage, cantidad))

        # random selection
        if len(vengence_possibilities) > 0:
            mag = 0.0
            for i in range(0, len(vengence_possibilities)):
                mag += vengence_possibilities[i][1]

            # REMOVING RANDOM
            # num = np.random.uniform(0, 1.0)
            if self.forced_random:
                num = self.getRand() / 1000.0
            else:
                num = np.random.randint(0, 1001) / 1000.0

            sumr = 0.0
            for i in range(0, len(vengence_possibilities)):
                sumr += (vengence_possibilities[i][1] / mag)

                if (num <= sumr):
                    # self.printT(player_idx, "plan to attack player " + str(attackPossibility[i][0]) + " with " + str(numAttackTokens))
                    return (vengence_possibilities[i][0], vengence_possibilities[i][2])

        return (-1, 0)


    # Change on May 5-6
    def pillage_the_village(self, round_num, player_idx, num_players, selected_community, num_tokens, tokens_remaining,
                            popularities, influence, group_cat):
        if (popularities[player_idx] <= 0.0) or (round_num < (self.genes["pillageDelay"] / 10.0)) or (
                self.genes["pillagePriority"] < 50):
            return (-1, 0)

        num_attack_tokens = min(tokens_remaining, int(num_tokens * (self.genes["pillageFury"] / 100.0) + 0.5))
        if num_attack_tokens <= 0:
            return (-1, 0)

        self.printT(player_idx, "\n Pillage info (" + str(num_attack_tokens) + "):")

        ratio_predicted_steals = 1.0
        predicted_steals = sum(np.negative(self.attacks_with_me).clip(0))
        if self.attacks_with_me[player_idx] < 0:
            ratio_predicted_steals = predicted_steals / (-self.attacks_with_me[player_idx])

        if round_num < 5:
            ratio_predicted_steals *= (self.genes["pillageCompanionship"] + 100.0) / 100.0

        self.printT(player_idx, "    ratio_predicted_steals: " + str(ratio_predicted_steals))

        pillage_possibilities = []
        for i in range(0, num_players):
            # Changes on May 6
            # if (self.govPlayer[i] == 1) or (i == player_idx):
            if (i == player_idx):
                continue

            # Change on May 6
            if (group_cat[i] < 2) and ((i not in selected_community) or (self.genes[
                                                                             "pillageFriends"] >= 50)):  # player_idx is not fearful of the group player i is in and player_idx is willing to pillage friends (if i is a friend)
                cantidad = num_attack_tokens
                my_weight = popularities[player_idx] * cantidad
                ratio = ratio_predicted_steals
                ratio2 = (my_weight + ((self.others_attacks_on[i] / self.gameParams["alpha"]) * num_tokens)) / my_weight
                if ratio2 > ratio_predicted_steals:
                    ratio = ratio2
                gain = my_weight - (popularities[i] * self.keeping_strength[i] / ratio)

                # Change on July 12
                while ((((gain * ratio) / num_tokens) * self.gameParams["alpha"] * self.gameParams["steal"]) > (
                        popularities[i] - self.gameParams["poverty_line"])) and (cantidad > 0):
                    cantidad -= 1
                    if cantidad == 0:
                        break

                    my_weight = popularities[player_idx] * cantidad
                    ratio = ratio_predicted_steals
                    ratio2 = (my_weight + ((self.others_attacks_on[i] / self.gameParams["alpha"]) * num_tokens)) / my_weight
                    if ratio2 > ratio_predicted_steals:
                        ratio = ratio2
                    gain = my_weight - (popularities[i] * self.keeping_strength[i] / ratio)

                if cantidad == 0:
                    continue

                steal_ROI = (gain * self.gameParams["steal"]) / (cantidad * popularities[player_idx])
                damage = (gain / num_tokens) * self.gameParams["steal"] * self.gameParams["alpha"]

                # self.printT(player_idx, "    steal_ROI " + str(i) + ": " + str(steal_ROI))

                imm_gain_per_token = steal_ROI * ((cantidad / num_tokens) * popularities[player_idx]) * self.gameParams[
                    "alpha"]
                friend_penalty = (1.0 - self.gameParams["beta"]) * (damage / popularities[i]) * influence[i][player_idx]
                imm_gain_per_token -= friend_penalty
                imm_gain_per_token -= self.ROI * ((cantidad / num_tokens) * popularities[player_idx]) * self.gameParams[
                    "alpha"]
                imm_gain_per_token /= cantidad

                self.printT(player_idx, "    " + str(i) + " imm_gain_per_token: " + str(imm_gain_per_token))

                # identify security threats
                security_threat_advantage = imm_gain_per_token + damage / cantidad
                if round_num > 3:
                    my_growth = (self.pop_history[round_num][player_idx] - self.pop_history[round_num - 4][
                        player_idx]) / 4.0
                    their_growth = (self.pop_history[round_num][i] - self.pop_history[round_num - 4][i]) / 4.0
                else:
                    my_growth = 0
                    their_growth = 0

                # Change on May 6
                if ((their_growth > (1.5 * my_growth)) and (popularities[i] > popularities[player_idx]) and (
                not i in selected_community)) or (group_cat[i] == 1):
                    imm_gain_per_token += security_threat_advantage

                # Change on May 11
                margin = self.genes["pillageMargin"] / 100.0
                if imm_gain_per_token > margin:
                    pillage_possibilities.append((i, imm_gain_per_token, cantidad))

        self.printT(player_idx, "")

        # random selection
        if len(pillage_possibilities) > 0:
            self.printT(player_idx, "***** gonna pillage")
            mag = 0.0
            for i in range(0, len(pillage_possibilities)):
                mag += pillage_possibilities[i][1]
            # REMOVING RANDOM
            # num = np.random.uniform(0, 1.0)
            if self.forced_random:
                num = self.getRand() / 1000.0
            else:
                num = np.random.randint(0, 1001) / 1000.0

            sumr = 0.0
            for i in range(0, len(pillage_possibilities)):
                sumr += (pillage_possibilities[i][1] / mag)

                if (num <= sumr):
                    # self.printT(player_idx, "plan to attack player " + str(attackPossibility[i][0]) + " with " + str(numAttackTokens))
                    return (pillage_possibilities[i][0], pillage_possibilities[i][2])

        return (-1, 0)


    def find_community_vec(self, num_players, communities, plyr):
        my_comm_vec = np.zeros(num_players, dtype=int)
        for s in communities:
            if plyr in s:
                for i in s:
                    my_comm_vec[i] = 1

                break

        return my_comm_vec


    def is_keeping(self, other_idx, num_players):
        meAmount = 0.0
        totalAmount = 0.0
        for i in range(0, num_players):
            # if self.govPlayer[i] == 1: # no government :(
            #     continue

            if i != other_idx:
                if self.infl_neg[other_idx][i] > 0.0:
                    totalAmount += self.infl_neg[other_idx][i] / self.gameParams["steal"]
                    meAmount -= self.infl_neg[other_idx][i]
                else:
                    totalAmount += self.infl_pos[other_idx][i] / self.gameParams["give"]

        meAmount = (meAmount + self.infl_pos[other_idx][other_idx] - self.infl_neg[other_idx][other_idx]) / self.gameParams[
            "keep"]
        totalAmount += meAmount

        # return meAmount
        if totalAmount > 0:
            return meAmount / totalAmount
        else:
            return 1.0


    def fear_keeping(self, num_players, player_idx, communities, agent_idx):
        amigos = self.find_community_vec(num_players, communities, agent_idx)
        enemigos = 1.0 - amigos
        sm = 0.0
        for i in range(num_players):
            if amigos[i]:
                sm = max(np.dot(enemigos, self.infl_neg[:, i]), sm)

        denom = sum(self.infl_pos[:, agent_idx])
        if denom > 0:
            fear_tokens = (sm / sum(self.infl_pos[:, agent_idx]))
        else:
            fear_tokens = 0.0
        fear_tokens = min(1.0,
                          fear_tokens * (self.genes["fearDefense"] / 50.0))  # assume everyone else has the same fear I do

        return fear_tokens


    def group_analysis(self, round_num, num_players, player_idx, popularities, influence):
        if round_num == 0:
            A_pos = self.compute_adjacency(num_players)
            A_neg = self.compute_neg_adjacency(num_players)

            communities, modularity = self.louvain_c_method_phase1(num_players, A_pos, A_neg)

            self.coalition_target = self.compute_coalition_target(round_num, popularities, communities, player_idx)
            elijo = self.random_selections(num_players, player_idx, popularities)

        else:

            A_pos = self.compute_adjacency(num_players)
            A_neg = self.compute_neg_adjacency(num_players)
            communities_ph1, modularity_ph1 = self.louvain_c_method_phase1(num_players, A_pos, A_neg)

            self.printT(player_idx, " communities_ph1: " + str(communities_ph1))
            self.printT(player_idx, " modularity_ph1: " + str(modularity_ph1))

            communities_mega, modularity = self.louvain_method_phase2(communities_ph1, A_pos, A_neg)

            communities = self.enumerate_community(modularity_ph1, communities_ph1, modularity, communities_mega)

            self.coalition_target = self.compute_coalition_target(round_num, popularities, communities, player_idx)

            elijo = self.envision_communities(num_players, player_idx, popularities, influence, A_pos, A_neg,
                                              communities_ph1, communities, modularity)

            self.printT(player_idx, "\nchosen community: " + str(elijo.s))
            if player_idx == self.theTracked:
                elijo.print()

        return communities, elijo


    def random_selections(self, num_players, player_idx, popularities):
        s = set()
        s.add(player_idx)
        pop = popularities[player_idx]
        total_pop = sum(popularities)
        while ((pop / total_pop) < self.coalition_target):

            if self.forced_random:
                num = (self.getRand() + player_idx) % num_players
            else:
                num = np.random.randint(0, 1001) % num_players

            if (num not in s):
                s.add(num)
                pop += popularities[num]

        s = sorted(s)

        return CommunityEvaluation(s, 0.0, 0.0, 0.0, 0.0, 0.0)


    def remove_mostly_dead(self, s, player_idx, popularities):
        d = set()
        s_n = set()
        if popularities[player_idx] < 10.0:
            return s, d

        for i in s:
            if i == player_idx:
                s_n.add(i)
            elif popularities[i] < (0.1 * popularities[player_idx]):
                d.add(i)
            else:
                s_n.add(i)

        return s_n, d


    def envision_communities(self, num_players, player_idx, popularities, influence, A_pos, A_neg, communities_ph1,
                             communities, modularity):
        potential_communities = []
        s_idx = self.find_community(player_idx, communities)

        # Change on June 2
        cur_comm_size = 0.0
        # for i in range(len(communities[s_idx])):
        for i in communities[s_idx]:
            # self.printT(player_idx, str(popularities[i]))
            cur_comm_size += popularities[i]

        if cur_comm_size == 0:
            cur_comm_size = 1

        sum_pops = sum(popularities)

        if sum_pops == 0:
            sum_pops = 1

        cur_comm_size /= sum_pops

        c = self.make_deep_copy(communities)

        s, c_prime, m = self.determine_communities(num_players, player_idx, popularities, influence, c, s_idx, A_pos, A_neg)

        s, d = self.remove_mostly_dead(s, player_idx, popularities)

        potential_communities.append(CommunityEvaluation(s, m, self.get_centrality(s, player_idx, popularities),
                                                         self.get_collective_strength(popularities, s, cur_comm_size),
                                                         self.get_familiarity(s, player_idx, num_players, influence),
                                                         self.get_ingroup_antisocial(s, player_idx)))

        # combine with any other group
        for i in range(len(communities)):
            if i != s_idx:
                c = self.make_deep_copy(communities)
                c[s_idx] = c[s_idx].union(c[i])
                if not self.already_in(c[s_idx], potential_communities):
                    c.pop(i)
                    # self.printT(player_idx, str(c))
                    s, c_prime, m = self.determine_communities(num_players, player_idx, popularities, influence, c,
                                                               self.find_community(player_idx, c), A_pos, A_neg)
                    s, d = self.remove_mostly_dead(s, player_idx, popularities)
                    potential_communities.append(CommunityEvaluation(s, m, self.get_centrality(s, player_idx, popularities),
                                                                     self.get_collective_strength(popularities, s,
                                                                                                  cur_comm_size),
                                                                     self.get_familiarity(s, player_idx, num_players,
                                                                                          influence),
                                                                     self.get_ingroup_antisocial(s, player_idx)))

        # move to a different group
        for i in range(len(communities)):
            if i != s_idx:
                c = self.make_deep_copy(communities)
                c[i].add(player_idx)
                if not self.already_in(c[i], potential_communities):
                    c[s_idx].remove(player_idx)
                    s, c_prime, m = self.determine_communities(num_players, player_idx, popularities, influence, c, i,
                                                               A_pos, A_neg)
                    s, d = self.remove_mostly_dead(s, player_idx, popularities)
                    potential_communities.append(CommunityEvaluation(s, m, self.get_centrality(s, player_idx, popularities),
                                                                     self.get_collective_strength(popularities, s,
                                                                                                  cur_comm_size),
                                                                     self.get_familiarity(s, player_idx, num_players,
                                                                                          influence),
                                                                     self.get_ingroup_antisocial(s, player_idx)))

        # add a member from another group
        for i in range(num_players):
            if i not in communities[s_idx]:
                c = self.make_deep_copy(communities)
                for s in c:
                    if i in s:
                        s.remove(i)
                        break
                c[s_idx].add(i)
                if not self.already_in(c[s_idx], potential_communities):
                    s, c_prime, m = self.determine_communities(num_players, player_idx, popularities, influence, c, s_idx,
                                                               A_pos, A_neg)
                    s, d = self.remove_mostly_dead(s, player_idx, popularities)
                    potential_communities.append(CommunityEvaluation(s, m, self.get_centrality(s, player_idx, popularities),
                                                                     self.get_collective_strength(popularities, s,
                                                                                                  cur_comm_size),
                                                                     self.get_familiarity(s, player_idx, num_players,
                                                                                          influence),
                                                                     self.get_ingroup_antisocial(s, player_idx)))

        # subtract a member from the group (that isn't player_idx)
        for i in communities[s_idx]:
            if i != player_idx:
                c = self.make_deep_copy(communities)
                c[s_idx].remove(i)
                if not self.already_in(c[s_idx], potential_communities):
                    c.append({i})
                    s, c_prime, m = self.determine_communities(num_players, player_idx, popularities, influence, c, s_idx,
                                                               A_pos, A_neg)
                    # self.printT(player_idx, str(s) + ": " + str(m))
                    s, d = self.remove_mostly_dead(s, player_idx, popularities)
                    potential_communities.append(CommunityEvaluation(s, m, self.get_centrality(s, player_idx, popularities),
                                                                     self.get_collective_strength(popularities, s,
                                                                                                  cur_comm_size),
                                                                     self.get_familiarity(s, player_idx, num_players,
                                                                                          influence),
                                                                     self.get_ingroup_antisocial(s, player_idx)))

        s2_idx = self.find_community(player_idx, communities_ph1)
        # if (s_idx != s2_idx):       # I believe that this is wrong; should be: if (communities[s_idx] != communities_ph1[s2_idx]):
        if (communities[s_idx] != communities_ph1[s2_idx]):
            s_idx = s2_idx
            # put in the original with combined other groups
            c = self.make_deep_copy(communities_ph1)
            s, c_prime, m = self.determine_communities(num_players, player_idx, popularities, influence, c, s_idx, A_pos,
                                                       A_neg)
            s, d = self.remove_mostly_dead(s, player_idx, popularities)
            potential_communities.append(CommunityEvaluation(s, m, self.get_centrality(s, player_idx, popularities),
                                                             self.get_collective_strength(popularities, s, cur_comm_size),
                                                             self.get_familiarity(s, player_idx, num_players, influence),
                                                             self.get_ingroup_antisocial(s, player_idx)))

            # combine with any other group
            for i in range(len(communities_ph1)):
                if i != s_idx:
                    c = self.make_deep_copy(communities_ph1)
                    c[s_idx] = c[s_idx].union(c[i])
                    # print("considering " + str(c[s_idx]) + "(" + str(c[s_idx]) + " union " + str(c[i]) + ")")
                    if not self.already_in(c[s_idx], potential_communities):
                        c.pop(i)
                        s, c_prime, m = self.determine_communities(num_players, player_idx, popularities, influence, c,
                                                                   self.find_community(player_idx, c), A_pos, A_neg)
                        s, d = self.remove_mostly_dead(s, player_idx, popularities)
                        potential_communities.append(
                            CommunityEvaluation(s, m, self.get_centrality(s, player_idx, popularities),
                                                self.get_collective_strength(popularities, s, cur_comm_size),
                                                self.get_familiarity(s, player_idx, num_players, influence),
                                                self.get_ingroup_antisocial(s, player_idx)))

            # move to a different group
            for i in range(len(communities_ph1)):
                if i != s_idx:
                    c = self.make_deep_copy(communities_ph1)
                    c[i].add(player_idx)
                    if not self.already_in(c[i], potential_communities):
                        c[s_idx].remove(player_idx)
                        s, c_prime, m = self.determine_communities(num_players, player_idx, popularities, influence, c, i,
                                                                   A_pos, A_neg)
                        s, d = self.remove_mostly_dead(s, player_idx, popularities)
                        potential_communities.append(
                            CommunityEvaluation(s, m, self.get_centrality(s, player_idx, popularities),
                                                self.get_collective_strength(popularities, s, cur_comm_size),
                                                self.get_familiarity(s, player_idx, num_players, influence),
                                                self.get_ingroup_antisocial(s, player_idx)))

            # add a member from another group
            for i in range(num_players):
                if i not in communities_ph1[s_idx]:
                    c = self.make_deep_copy(communities_ph1)
                    for s in c:
                        if i in s:
                            s.remove(i)
                            break
                    c[s_idx].add(i)
                    if not self.already_in(c[s_idx], potential_communities):
                        s, c_prime, m = self.determine_communities(num_players, player_idx, popularities, influence, c,
                                                                   s_idx, A_pos, A_neg)
                        # self.printT(player_idx, str(c_prime))
                        s, d = self.remove_mostly_dead(s, player_idx, popularities)
                        potential_communities.append(
                            CommunityEvaluation(s, m, self.get_centrality(s, player_idx, popularities),
                                                self.get_collective_strength(popularities, s, cur_comm_size),
                                                self.get_familiarity(s, player_idx, num_players, influence),
                                                self.get_ingroup_antisocial(s, player_idx)))

            # subtract a member from the group (that isn't player_idx)
            for i in communities_ph1[s_idx]:
                if i != player_idx:
                    c = self.make_deep_copy(communities_ph1)
                    c[s_idx].remove(i)
                    if not self.already_in(c[s_idx], potential_communities):
                        c.append({i})
                        s, c_prime, m = self.determine_communities(num_players, player_idx, popularities, influence, c,
                                                                   s_idx, A_pos, A_neg)
                        s, d = self.remove_mostly_dead(s, player_idx, popularities)
                        potential_communities.append(
                            CommunityEvaluation(s, m, self.get_centrality(s, player_idx, popularities),
                                                self.get_collective_strength(popularities, s, cur_comm_size),
                                                self.get_familiarity(s, player_idx, num_players, influence),
                                                self.get_ingroup_antisocial(s, player_idx)))

        min_mod = modularity
        for c in potential_communities:
            if c.modularity < min_mod:
                min_mod = c.modularity

        elegir = potential_communities[0]
        mx = -99999
        for c in potential_communities:
            if modularity == min_mod:
                c.modularity = 1.0
            else:
                c.modularity = (c.modularity - min_mod) / (modularity - min_mod)

            c.compute_score(self.genes)
            if c.score > mx:
                elegir = c
                mx = c.score

        self.me_importa = np.zeros(num_players, dtype=float)
        for i in elegir.s:
            mejor = 1.0
            if i != player_idx:
                for c in potential_communities:
                    if i not in c.s:
                        mejor = min(mejor, (elegir.score - c.score) / elegir.score)
            self.me_importa[i] = mejor

        return elegir


    def already_in(self, s, potential_communities):
        for c in potential_communities:
            if s == c.s:
                return True

        return False


    def determine_communities(self, num_players, player_idx, popularities, influence, c, s_idx, A_pos, A_neg):
        s = c.pop(s_idx)
        c_mega, m = self.louvain_method_phase2(c, A_pos, A_neg)

        c_prime = self.enumerate_community(0, c, 1, c_mega)
        c_prime.append(s)
        cur_comms = np.zeros(num_players, dtype=int)
        for j in range(0, len(c_prime)):
            for i in c_prime[j]:
                # print(str(j) + " has " + str(i))
                cur_comms[i] = j
        # print(cur_comms)
        m = self.compute_signed_modularity(num_players, cur_comms, A_pos, A_neg)

        return s, c_prime, m


    def compute_signed_modularity(self, num_players, cur_comms, A_pos, A_neg):
        modu = self.alpha * self.compute_modularity(num_players, cur_comms, A_pos)
        modu -= (1.0 - self.alpha) * self.compute_modularity(num_players, cur_comms, A_neg)

        return modu


    def make_deep_copy(self, comm):
        c = []
        for s in comm:
            c.append(s.copy())

        return c


    def find_community(self, player_idx, communities):
        for i in range(len(communities)):
            if player_idx in communities[i]:
                return i

        print("Problem: Didn't find a community")
        sys.exit()

        return -1


    def louvain_c_method_phase1(self, num_players, A_pos, A_neg):
        current_communities = list(range(num_players))

        if num_players == 0:
            communities = []
            return communities, 0.0

        the_groups = set(range(num_players))
        com_matrix = np.identity(num_players)
        # print(len(A_pos))
        m_pos = sum(sum(A_pos))
        K_pos = sum(A_pos)
        m_neg = sum(sum(A_neg))
        K_neg = sum(A_neg)
        com_counts = np.ones(num_players, dtype=int)
        hay_cambio = True

        while hay_cambio:
            hay_cambio = False
            for i in range(num_players):
                mx_com = current_communities[i]
                best_dQ = 0.0
                for j in the_groups:
                    if current_communities[i] == j:
                        continue

                    dQ_pos = self.move_i_to_j(num_players, com_matrix, m_pos, K_pos, A_pos, i, j, current_communities[i])
                    dQ_neg = self.move_i_to_j(num_players, com_matrix, m_neg, K_neg, A_neg, i, j, current_communities[i])
                    # print("   dQ_pos: " + str(dQ_pos) + "; dQ_neg: " + str(dQ_neg))

                    dQ = self.alpha * dQ_pos - (1 - self.alpha) * dQ_neg
                    if dQ > best_dQ:
                        mx_com = j
                        best_dQ = dQ

                if best_dQ > 0.0:
                    com_matrix[current_communities[i]][i] = 0
                    com_counts[current_communities[i]] -= 1
                    if (com_counts[current_communities[i]] <= 0):
                        the_groups.remove(current_communities[i])
                    com_matrix[mx_com][i] = 1
                    com_counts[mx_com] += 1
                    current_communities[i] = mx_com
                    hay_cambio = True

        communities = []
        for i in range(num_players):
            if com_counts[i] > 0:
                s = set()
                for j in range(num_players):
                    if com_matrix[i][j] == 1:
                        s.add(j)
                communities.append(s)

        the_modularity = self.alpha * self.compute_modularity(num_players, current_communities, A_pos)
        the_modularity -= (1 - self.alpha) * self.compute_modularity(num_players, current_communities, A_neg)

        return communities, the_modularity


    def move_i_to_j(self, num_players, com_matrix, m, K, A, i, com_j, com_i):
        # first, what is the change in modularity from putting i into j's community
        sigma_in = 0.0
        for k in range(num_players):
            if com_matrix[com_j][k] == 1:
                sigma_in += np.dot(com_matrix[com_j], A[k])

        sigma_tot = np.dot(com_matrix[com_j], K)
        k_iin = np.dot(com_matrix[com_j], A[i])
        twoM = 2.0 * m

        if twoM == 0:
            return 0.0

        a = (sigma_in + 2 * k_iin) / twoM
        b = (sigma_tot + K[i]) / twoM
        c = sigma_in / twoM
        d = sigma_tot / twoM
        e = K[i] / twoM
        dQ_in = (a - (b * b)) - (c - d * d - e * e)

        # second, what is the change in modularity from removing i from its community
        com = com_matrix[com_i].copy()
        com[i] = 0
        sigma_in = 0.0
        for k in range(num_players):
            if com[k] == 1:
                sigma_in += np.dot(com, A[k])

        sigma_tot = np.dot(com, K)

        k_iin = np.dot(com, A[i])

        a = (sigma_in + 2 * k_iin) / twoM
        b = (sigma_tot + K[i]) / twoM
        c = sigma_in / twoM
        d = sigma_tot / twoM
        e = K[i] / twoM
        dQ_out = (a - (b * b)) - (c - d * d - e * e)

        return dQ_in - dQ_out


    def compute_modularity(self, num_players, current_communities, A):
        k = sum(A)
        m = sum(k)

        if m == 0:
            return 0.0

        Q = 0
        for i in range(num_players):
            for j in range(num_players):
                Q += self.deltar(current_communities, i, j) * (A[i][j] - ((k[i] * k[j]) / (2 * m)))
        Q /= 2 * m

        return Q


    def deltar(self, current_communities, i, j):
        if current_communities[i] == current_communities[j]:
            return 1
        else:
            return 0


    def compute_modularity2(self, num_players, communities, A):
        k = sum(A)
        m = sum(k)

        if m == 0:
            return 0.0

        Q = 0
        for i in range(num_players):
            for j in range(num_players):
                Q += self.deltar2(communities, i, j) * (A[i][j] - ((k[i] * k[j]) / (2 * m)))
        Q /= 2 * m

        return Q


    def deltar2(self, communities, i, j):
        for s in communities:
            if (i in s) and (j in s):
                return 1

        return 0


    def louvain_method_phase2(self, communities_ph1, A_pos, A_neg):
        num_communities = len(communities_ph1)
        # print("    num_communities: " + str(num_communities))

        # Lump individuals into communities: compute B_pos and B_neg
        B_pos = np.zeros((num_communities, num_communities), dtype=float)
        B_neg = np.zeros((num_communities, num_communities), dtype=float)

        for i in range(num_communities):
            for j in range(num_communities):
                for k in communities_ph1[i]:
                    for m in communities_ph1[j]:
                        B_pos[i][j] += A_pos[k][m]
                        B_neg[i][j] += A_neg[k][m]

        # print(B_pos)

        return self.louvain_c_method_phase1(num_communities, B_pos, B_neg)


    def enumerate_community(self, modularity_ph1, communities_ph1, modularity, communities_mega):
        if modularity > modularity_ph1:
            communities = []
            for m in communities_mega:
                communities.append(set())
                for i in m:
                    for j in communities_ph1[i]:
                        communities[len(communities) - 1].add(j)

        else:
            communities = communities_ph1

        return communities


    # Change on May 9
    def get_collective_strength(self, popularities, s, cur_comm_size):
        proposed = 0.0
        for i in s:
            proposed += popularities[i]
        if proposed == 0:
            proposed = 1

        pop_sum = sum(popularities)
        if pop_sum == 0:
            pop_sum = 1

        proposed /= pop_sum

        if self.genes["coalitionTarget"] == 0:
            target = 0.01
        else:
            target = self.genes["coalitionTarget"] / 100.0

        base = 1.0 - (abs(target - cur_comm_size) / target)
        if base < 0.01:
            base = 0.01
        base *= base

        # print(str(s) + ": " + str(proposed) + "; " + str(target) + "; " + str(cur_comm_size) + "; " + str(base))
        if abs(proposed - cur_comm_size) <= 0.03:
            return base
        elif abs(cur_comm_size - target) < abs(proposed - target):
            nbase = 1.0 - (abs(target - proposed) / target)
            if nbase < 0.01:
                nbase = 0.01
            return nbase * nbase
        else:
            baseline = (1.0 + base) / 2.0
            w = abs(proposed - target) / abs(cur_comm_size - target)
            return ((1.0 - w) * 1.0) + (baseline * w)


    # comparison to average, rank, comparison to top
    def get_centrality(self, s, player_idx, popularities):
        group_sum = 0
        mx = 0.0
        num_greater = 0
        for i in s:
            group_sum += popularities[i]
            if popularities[i] > mx:
                mx = popularities[i]
            if popularities[i] > popularities[player_idx]:
                num_greater += 1

        if (group_sum > 0.0) and (len(s) > 1):
            ave_sum = group_sum / len(s)
            aveVal = popularities[player_idx] / ave_sum
            mxVal = popularities[player_idx] / mx
            rankVal = 1 - (num_greater / (len(s) - 1.0))

            return (aveVal + mxVal + rankVal) / 3.0
        else:
            return 1.0


    def get_familiarity(self, s, player_idx, num_players, influence):
        mag = sum(self.infl_pos[:, player_idx])
        if mag > 0.0:
            randval = mag / num_players
            ind_loyalty = 0.0
            scaler = 1.0
            for i in s:
                if (self.scaled_back_nums[i] < 0.05) and (i != player_idx):
                    scaler *= ((len(s) - 1) / len(s))

                if (influence[i][player_idx] * self.scaled_back_nums[i]) > randval:
                    ind_loyalty += influence[i][player_idx] * self.scaled_back_nums[i]  # self.scale_back(player_idx, i)
                else:
                    ind_loyalty += (influence[i][player_idx] * self.scaled_back_nums[i]) - randval
            familiarity = max(0.01, scaler * (ind_loyalty / mag))
        else:
            familiarity = 1.0

        if familiarity < 0.0:
            familiarity = 0.0

        return familiarity


    def get_ingroup_antisocial(self, s, player_idx):
        # if i isn't giving much compared to what they receive
        # if i is keeping a lot more than is normal
        # if i isn't reciprocating with me
        # if i is stealing from people in s
        # if i is stealing from people in other groups without cause

        # then maybe i'm less inclined to have i in my group
        scl = 1.0
        piece = 1.0 / len(s)
        remain = 1.0 - piece
        for i in s:
            if i != player_idx:
                the_investment = 0.0
                the_return = 0.0
                for j in s:
                    if i != j:
                        the_investment += self.sum_infl_pos[j][i]
                        the_return += self.sum_infl_pos[i][j]

                if the_investment > 0.0:
                    val = the_return / the_investment
                    if val > 1.0:
                        val = 1.0
                    scl *= piece * val + remain

        # self.printT(player_idx, str(s) + ": " + str(scl))
        return scl
