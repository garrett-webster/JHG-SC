import os

from Server.Engine.completeBots.baseagent import AbstractAgent
import numpy as np
import sys
import copy
from pathlib import Path
from Server.SC_Bots.transVecTranslator import translateVecToIndex
from Server.Engine.completeBots.geneAgent3Supplement import GeneAgentMixin

# make sure to put the GeneAgentMixin first, then the abstractAgent. Base class goes last, mixin classes go on top.
class GeneAgent3(GeneAgentMixin, AbstractAgent):

    def __init__(self, geneStr, _num_gene_copies):  # Change on Sep 21
        super().__init__()
        self.num_gene_copies = _num_gene_copies     # Change on Sep 21
        self.whoami = "gene"
        self.count = 0
        self.relativeFitness = 0.0
        self.absoluteFitness = 0.0
        self.relativePopularity = 0.0
        self.absolutePopularity = 0.0
        self.gameParams = {}
        self.tokens_per_player = 2
        self.pop_history = [] # just slap this up here.
        self.selected_community = {-1} # sign that nothing has changed

        # Changes in May
        if geneStr == "":
            # Change on May 12
            # Change on Sep 21
            self.genes_long = []
            for i in range(0, self.num_gene_copies):
                gene_set = {
                    "visualTrait": np.random.randint(0,101),        # not used
                    "homophily": np.random.randint(0,101),          # not used
                    "alpha": np.random.randint(0,101),
                    "otherishDebtLimits": np.random.randint(0,101),
                    "coalitionTarget": np.random.randint(0,101),
                    "fixedUsage": np.random.randint(0,101),     # proportion of tokens to give out evenly in group_allocate
                    "w_modularity": np.random.randint(0,101),
                    "w_centrality": np.random.randint(0,101),
                    "w_collective_strength": np.random.randint(0,101),
                    "w_familiarity": np.random.randint(0,101),
                    "w_prosocial": np.random.randint(0,101),
                    "initialDefense": np.random.randint(0,101),
                    "minKeep": np.random.randint(0,101),
                    "defenseUpdate": np.random.randint(0,101),
                    "defensePropensity": np.random.randint(0,101),
                    "fearDefense": np.random.randint(0,101),
                    "safetyFirst": np.random.randint(0,101),
                    "pillageFury": np.random.randint(0,101),
                    "pillageDelay": np.random.randint(0,101),
                    "pillagePriority": np.random.randint(0,101),
                    "pillageMargin": np.random.randint(0,101),
                    "pillageCompanionship": np.random.randint(0,101),
                    "pillageFriends": np.random.randint(0,101),
                    "vengenceMultiplier": np.random.randint(0,101),
                    "vengenceMax": np.random.randint(0,101),
                    "vengencePriority": np.random.randint(0,101),
                    "defendFriendMultiplier": np.random.randint(0,101),
                    "defendFriendMax": np.random.randint(0,101),
                    "defendFriendPriority": np.random.randint(0,101),
                    "attackGoodGuys": np.random.randint(0,101),
                    "limitingGive": np.random.randint(0,101),
                    "groupAware": np.random.randint(0,101),
                    "joinCoop": np.random.randint(0,101),
                }
                self.genes_long.append(gene_set)
        else:
            # read geneStr to set up the genotype
            # print("this is the geneStr we are passing in ", geneStr)
            words = geneStr.split("_")
            # Change on May 12
            # Change on Sep 21
            self.genes_long = []
            count = 0
            for i in range(0, self.num_gene_copies):
                gene_set = {
                    "visualTrait": int(words[1+count]),             # not used
                    "homophily": int(words[2+count]),               # not used
                    "alpha": int(words[3+count]),
                    "otherishDebtLimits": int(words[4+count]),
                    "coalitionTarget": int(words[5+count]),
                    "fixedUsage": int(words[6+count]),
                    "w_modularity": int(words[7+count]),
                    "w_centrality": int(words[8+count]),
                    "w_collective_strength": int(words[9+count]),
                    "w_familiarity": int(words[10+count]),
                    "w_prosocial": int(words[11+count]),
                    "initialDefense": int(words[12+count]),
                    "minKeep": int(words[13+count]),
                    "defenseUpdate": int(words[14+count]),
                    "defensePropensity": int(words[15+count]),
                    "fearDefense": int(words[16+count]),
                    "safetyFirst": int(words[17+count]),
                    "pillageFury": int(words[18+count]),
                    "pillageDelay": int(words[19+count]),
                    "pillagePriority": int(words[20+count]),
                    "pillageMargin": int(words[21+count]),
                    "pillageCompanionship": int(words[22+count]),
                    "pillageFriends": int(words[23+count]),
                    "vengenceMultiplier": int(words[24+count]),
                    "vengenceMax": int(words[25+count]),
                    "vengencePriority": int(words[26+count]),
                    "defendFriendMultiplier": int(words[27+count]),
                    "defendFriendMax": int(words[28+count]),
                    "defendFriendPriority": int(words[29+count]),
                    "attackGoodGuys": int(words[30+count]),
                    "limitingGive": int(words[31+count]),
                    "groupAware": int(words[32+count]),
                    "joinCoop": int(words[33+count]),
                }
                self.genes_long.append(gene_set)
                count = count + 33

        self.theTracked = self.getTracked() # do we really need this???
        self.played_genes = True

        # try:
        #     fp = open("Server/Engine/rnums.txt", "r")
        # except FileNotFoundError:
        #     try:
        #         fp = open("../Server/Engine/rnums.txt")
        #     except FileNotFoundError:
        #         return "man you stupid"

        rnums_path = self.get_rnums_path()
        if not rnums_path:
            print("Hey thats wrong")
        else:
            fp = open(rnums_path)

        self.randNums = []
        for i in range(0,10000):
            self.randNums.append(int(fp.readline()))
        self.randCount = 0

        fp.close()

    def get_number_type(self):
        return 11 # IDEK just pick a number


    def getRand(self):
        num = self.randNums[self.randCount]
        self.randCount = self.randCount + 1
        if self.randCount >= 10000:
            self.randCount = 0
        return num


    def get_rnums_path(self):
        base_path = Path(__file__).resolve().parent
        possible_paths = [
            base_path / "rnums.txt",
            base_path.parent / "rnums.txt",
        ]
        for path in possible_paths:
            if path.exists():
                return path

        print("well fetch, that did't go well ")
        return None


    def getTracked(self):
        base_path = Path(__file__).resolve().parent
        possible_paths = [
            base_path / "theTracked.txt"
        ]
        actual_path = None
        for path in possible_paths:
            if path.exists():
                actual_path = path
        f = open(actual_path, "r")


        val = int(f.readline())
        f.close()

        return val


    def assassinGenes(self):
        self.played_genes = False

        self.genes["visualTrait"] = 50
        self.genes["alpha"] = 1
        self.genes["homophily"] = 50
        self.genes["otherishDebtLimits"] = 25
        self.genes["coalitionTarget"] = 0
        self.genes["fixedUsage"] = 50
        self.genes["w_modularity"] = 100
        self.genes["w_centrality"] = 0
        self.genes["w_collective_strength"] = 0
        self.genes["w_familiarity"] = 0
        self.genes["w_prosocial"] = 0
        self.genes["initialDefense"] = 100
        self.genes["minKeep"] = 100
        self.genes["defenseUpdate"] = 50
        self.genes["defensePropensity"] = 50
        self.genes["fearDefense"] = 50
        self.genes["safetyFirst"] = 0
        self.genes["pillageFury"] = 100
        self.genes["pillageDelay"] = 10
        self.genes["pillagePriority"] = 80
        self.genes["pillageMargin"] = 0
        self.genes["pillageFriends"] = 0
        self.genes["pillageCompanionship"] = 50
        self.genes["vengenceMultiplier"] = 100
        self.genes["veng.enceMax"] = 100
        self.genes["vengencePriority"] = 100
        self.genes["defendFriendMultiplier"] = 100
        self.genes["defendFriendMax"] = 100
        self.genes["defendFriendPriority"] = 90
        self.genes["attackGoodGuys"] = 100
        self.genes["limitingGive"] = 100
        self.genes["groupAware"] = 0


    def setGameParams(self, gameParams, _forcedRandom):
        self.gameParams = gameParams
        self.forced_random = _forcedRandom

    def getType(self):
        return self.whoami

    def getVote(self, options_matrix, index):
        # I want them to be able to look at the whole options and matrix and understand what they can do.
        current_options = options_matrix[index]
        current_max = -11 # not a real value, unrealistic min
        current_index = -1
        for index in range(len(current_options)):
            if current_options[index] > current_max:
                current_max = current_options[index]
                current_index = index

        return current_index



    def getString(self):
        theStr = "genes"
        # Change on Sep 21
        for i in range(0, len(self.genes_long)):
            for key in self.genes_long[i]:
                theStr = theStr + "_" + str(self.genes_long[i][key])

        return theStr

    def get_vote(self, player_idx, round_num, received, popularities, influence, extra_data, current_options_matrix, enforce_majority):
        transaction_vector = self.play_round(player_idx, round_num, received, popularities, influence, extra_data, True)
        final_vote = translateVecToIndex(transaction_vector, current_options_matrix, enforce_majority)
        return final_vote # please let this work


    def play_round(self, player_idx, round_num, received, popularities, influence, extra_data, extra_flag=False):
        # don't worry about the current options matrix, he gest used in the cat thing.y
        if np.isnan(popularities).all():
            print("Stack trace this fetcher please and thank you!")
        # if round_num == 1:
        #     print("bot params: plyr_idx ", player_idx, " round_num ", round_num, " received \n", received, "popularities \n", popularities, " influence \n", influence, " extra data \n", extra_data)

        self.printT(player_idx, str(received))

        if self.theTracked != 99999:
            self.theTracked = self.getTracked()

        if round_num == 0:
            self.pop_history = []
        self.pop_history.append(popularities)

        num_players = len(popularities)
        num_tokens = num_players * self.tokens_per_player

        if player_idx == self.theTracked:
            print()
            print("\n\nRound " + str(round_num) + " (Player " + str(self.theTracked) + ")")

        if round_num == 0:
            self.initVars(player_idx, extra_data, num_players, popularities)
            self.alpha = self.genes["alpha"] / 100.0
            self.printT(player_idx, self.getString())
        else:
            self.alpha = self.genes["alpha"] / 100.0
            self.updateVars(received, popularities, num_tokens, num_players, player_idx, extra_flag)



        # none of this seems to have the bad assumption plugged into it.
        self.computeUsefulQuantities(round_num, num_players, influence, player_idx, num_tokens)

        if player_idx == self.theTracked:
            print(" Punishable debt: " + str(self.punishable_debt))
            # if round_num > 0:
            #     self.compute_homophily(num_players)

        # analyzes all the communities. no reason to touch it. (yes I double checked it)
        communities, selected_community = self.group_analysis(round_num, num_players, player_idx, popularities, influence)

        # if not extra_flag: # first notable difference between the bots
        self.selected_community = selected_community.s
        # else: # we don't consider ourselves to be part of our community within the SC thing. I think.
        #     selected_community.s.remove(player_idx)
        #     self.selected_community = selected_community.s

        # figure out how many tokens to keep
        # this estimates how much we think eveyrone else will keep. currently checking for negatives.
        self.estimate_keeping(player_idx, num_players, num_tokens, communities)
        self.printT(player_idx, "\n estimated keeping: " + str(np.round( [float(i) for i in self.keeping_strength], 1)))

        if self.genes["safetyFirst"] < 50: # literally 0 clue wha tthis does.
            safety_first = False
        else:
            safety_first = True

        guardo_toks = self.cuanto_guardo(round_num, player_idx, num_players, num_tokens, popularities, received, selected_community.s, extra_flag)
        if extra_flag: # in the sc test bed, we can give a max of 10 tokens to any person, including ourselves.
            if guardo_toks > 10: # positive cap
                guardo_toks = 10
            if guardo_toks < -10: # negative cap
                guardo_toks = -10

        self.printT(player_idx, "   guardo_toks: " + str(guardo_toks))

        # # determine who to attack (if any)
        if (round_num > 0):# and (player_idx == 0):
            # output += ("Here is the num tokens as of right now ", num_tokens, " \n")
            remaining_toks = num_tokens
            if safety_first:
                # self.printT(player_idx, "    safety first!!")
                remaining_toks -= guardo_toks # I think this just actually forces us to keep a certain amount of tokens, I don't think I need to change this line.
                #output += ("safety first ! True, here are the new remaining tokens " + str(remaining_toks), " \n")

            attack_alloc, num_attack_toks = self.quien_ataco(round_num, player_idx, num_players, num_tokens, remaining_toks, popularities, influence, selected_community.s, communities)
            # print("this is the attack alloc ", attack_alloc, " and this is the num_attack_toks ", num_attack_toks)

        else: # no reason to attack on the first round.
            attack_alloc = np.zeros(num_players, dtype=int)
            remaining_toks = num_tokens - guardo_toks
            num_attack_toks = 0

        # figure out who to give tokens to
        if not extra_flag: # change on 7/24/2025 - extra flag is only true within the SC environment.
            groups_alloc, num_group_gives = self.group_givings(round_num, num_players, num_tokens, num_tokens-num_attack_toks-guardo_toks, player_idx, influence, popularities, selected_community, attack_alloc, extra_flag)
            #output += ("here is the groups alloc ", groups_alloc, " and here is the num_group_gives ", num_group_gives, " \n")
        else: # we are in the sc one.
            giving_tokens = (num_tokens + num_attack_toks) - guardo_toks
            groups_alloc, num_group_gives = self.group_givings(round_num, num_players, num_tokens, giving_tokens, player_idx, influence, popularities, selected_community, attack_alloc, extra_flag)
            #output += ("here is the groups alloc ", groups_alloc, " and here is the num_group_gives ", num_group_gives, " \n")

        # update some variables
        transaction_vec = groups_alloc - attack_alloc

        # output += ("Here is the transaction_vec ", transaction_vec, " \n")

        # Change made on 6/16
        guardo_toks = num_tokens - sum(np.absolute(transaction_vec))
        if extra_flag:
            if guardo_toks > 10:
                guardo_toks = 10 # cap it out at 10
            if guardo_toks < -10:
                guardo_toks = -10
        # output += ("here is the guardo toks ", guardo_toks, " \n")
        transaction_vec[player_idx] += guardo_toks
        # output += ("Here is the new transaction vector ", transaction_vec, " \n")

        self.prev_popularities = popularities
        self.prev_allocations = transaction_vec
        self.prev_influence = influence
        self.updateIndebtedness(round_num, player_idx, transaction_vec, popularities)

        if player_idx == self.theTracked:
            print(str(player_idx) + " transaction_vec: " + str(transaction_vec) + " (" + str(num_group_gives) + ")")

        # if transaction_vec[player_idx] < 0:
        #     print(str(player_idx) + " is stealing from self!!!")
        # if printTransactionVector:
        #     print(transaction_vec)


        if extra_flag: # not sure how to redistribute these in a way that makes sense.
            for i in range(len(transaction_vec)):
                if transaction_vec[i] > 10:
                    excess = transaction_vec[i] - 10
                    transaction_vec[i] = 10
                    # num_allocated -= excess

        # if extra_flag: # Not entirelyt sure whats going on here but I have broked it broked it
        #     self.selected_community.add(player_idx) # just go ahead and stick that back in there.

        if sum(transaction_vec) < -50:
            print("hey something si wrong ", player_idx, " has an allocatino of ", transaction_vec, " . and here is the flag ", extra_flag)
            print("This is the group allocatinos ", groups_alloc, " and here is the attack alloc ", attack_alloc)

        return transaction_vec

    def get_selected_community(self):
        return self.selected_community

    def initVars(self, player_idx, extra_data, num_players, popularities):
        # Change on Sep 21
        the_pool = self.determine_gene_pool(player_idx, popularities, False)
        self.genes = copy.deepcopy(self.genes_long[the_pool]) 

        self.played_genes = True
        if player_idx == -1:# and (np.random.randint(0,2) == 1):
            self.assassinGenes()
        self.govPlayer = self.determineGovment(num_players, extra_data)
        self.tally = np.zeros(num_players, dtype=float)
        self.unpaid_debt = np.zeros(num_players)
        self.punishable_debt = np.zeros(num_players, dtype=float)
        self.expectedReturn = np.zeros(num_players, dtype=float)
        self.ave_return = 0.0
        self.scaled_back_nums = np.ones(num_players, dtype=float)
        self.received_value = 0.0
        self.invested_value = 0.0
        self.ROI = self.gameParams["keep"]

    def updateVars(self, received, popularities, num_tokens, num_players, player_idx, extra_flag):
        # Change on Sep 21
        the_pool = self.determine_gene_pool(player_idx, popularities, extra_flag)
        self.printT(player_idx, "gene pool: " + str(the_pool))
        self.genes = copy.deepcopy(self.genes_long[the_pool])

        self.printT(player_idx, "\nupdateVars:")
                    # nd array * int *             ndarray
        self.tally += (received * num_tokens) * self.prev_popularities
        self.tally[player_idx] = 0

        # self.printT(player_idx, "prev_popularities: " + str(self.prev_popularities))
        # self.printT(player_idx, "received: " + str(received))
        # self.printT(player_idx, "tally: " + str(self.tally))

        self.punishable_debt = np.zeros(num_players, dtype=float)
        for i in range(num_players):
            if (self.tally[i] < 0.0) and (self.unpaid_debt[i] < 0.0):
                self.punishable_debt[i] = -max(self.unpaid_debt[i], self.tally[i])

        self.unpaid_debt = self.tally.copy()

        for i in range(num_players):
            if i != player_idx:
                self.scaled_back_nums[i] = self.scale_back(player_idx, i)

        self.printT(player_idx, " scale_back: " + str(self.scaled_back_nums))

        self.received_value *= 1.0 - self.gameParams["alpha"]
        for i in range(num_players):
            if i == player_idx:
                self.received_value += received[i] * num_tokens * self.prev_popularities[i] * self.gameParams["keep"]
            elif received[i] < 0:
                self.received_value += received[i] * num_tokens * self.prev_popularities[i] * self.gameParams["steal"]
            elif received[i] > 0:
                self.received_value += received[i] * num_tokens * self.prev_popularities[i] * self.gameParams["give"]
        self.invested_value *= 1.0 - self.gameParams["alpha"]
        self.invested_value += sum(self.prev_allocations.clip(0)) * self.prev_popularities[player_idx]
        if self.invested_value > 0.0:
            self.ROI = self.received_value / self.invested_value
        else:
            self.ROI = self.gameParams["keep"]
        if self.ROI < self.gameParams["keep"]:
            self.ROI = self.gameParams["keep"]
        self.printT(player_idx, " invested " + str(self.invested_value) + "; got " + str(self.received_value))
        self.printT(player_idx, " received: " + str(received * num_tokens))
        self.printT(player_idx, " ROI: " + str(self.ROI))
        self.printT(player_idx, "")


    # Change on Sep 21
    def determine_gene_pool(self, player_idx, popularities, extra_flag):
        if self.num_gene_copies == 1:
            return 0

        if self.num_gene_copies != 3:
            print('geneagent not configured for ' + str(self.num_gene_copies) + ' gene copies')
            os.exit()


        if not extra_flag:
        # compute the mean
            m = sum(popularities) / len(popularities)
            ratio = popularities[player_idx] / m

        else:
            min = np.min(popularities)
            new_popularities = [pop + min for pop in popularities]
            m = sum(new_popularities) / len(popularities)
            ratio = popularities[player_idx] / m

        self.printT(player_idx, "ratio: " + str(ratio))

        if ratio > 1.25:
            return 2
        elif ratio < 0.75:
            return 0
        else:
            return 1


    def determineGovment(self, num_players, extra_data):
        is_govment = np.zeros(num_players, dtype=int)
        taxes = {}
        for p_id, data in extra_data.items():
            if data is not None and data.get('is_government', False):
                is_govment[int(p_id)] = 1

        return is_govment


    def estimate_keeping(self, player_idx, num_players, num_tokens, communities):
        self.keeping_strength = []
        for i in range(0, num_players):
            keeping_strength_i = max(self.is_keeping(i, num_players), self.fear_keeping(num_players, player_idx, communities, i))
            # self.printT(player_idx, str(i) + " is keeping " + str(self.is_keeping(i, num_players)))
            # self.printT(player_idx, str(i) + " fear keeping " + str(self.fear_keeping(num_players, communities, i)))
            self.keeping_strength.append(keeping_strength_i * num_tokens)


    def computeUsefulQuantities(self, round_num, num_players, influence, player_idx, num_tokens):
        if influence.all() == None:
            print("Stop here")

        if round_num > 0:
            self.infl_neg_prev = np.copy(self.infl_neg)
        else:
            self.infl_neg_prev = np.negative(influence).clip(0)

        self.infl_pos = np.positive(influence).clip(0)
        self.infl_neg = np.negative(influence).clip(0)

        self.infl_pos_sumcol = self.infl_pos.sum(axis=0)
        self.infl_pos_sumrow = self.infl_pos.sum(axis=1)

        if round_num == 0:
            self.sum_infl_pos = np.zeros((num_players, num_players), dtype=float)
            self.attacks_with_me = np.zeros(num_players, dtype=float)
            self.others_attacks_on = np.zeros(num_players, dtype=float)

            # Change on May 4-5
            self.inflicted_damage_ratio = 1.0
            self.bad_guys = np.zeros(num_players, dtype=float)
        else:
            self.sum_infl_pos += self.infl_pos

            w = 0.2
            for i in range(0, num_players):
                val = sum(np.negative(influence[:,i] - ((self.prev_influence[:,i] * (1.0 - self.gameParams["alpha"])))).clip(0))
                val -= np.negative(influence[player_idx][i] - ((self.prev_influence[player_idx][i] * (1.0 - self.gameParams["alpha"])))).clip(0)
                self.others_attacks_on[i] = (self.others_attacks_on[i] * w) + ((1.0-w) * val)
                if i != player_idx:
                    if self.prev_allocations[i] < 0:
                        # Change on May 4
                        amount = (np.negative(influence[:,i] - (self.prev_influence[:,i] * (1.0 - self.gameParams["alpha"]))).clip(0))
                        self.attacks_with_me -= amount
                        if self.expected_defend_friend_damage != -99999:
                            new_ratio = sum(amount) / self.expected_defend_friend_damage
                            self.inflicted_damage_ratio = 0.5 * self.inflicted_damage_ratio + 0.5 * new_ratio
                            # self.printT(player_idx, "******* inflicted " + str(sum(amount)) + " vs " + str(self.expected_defend_friend_damage))
                            # self.printT(player_idx, "******* inflicted_damage_ratio: " + str(self.inflicted_damage_ratio))

            # Change on May 5
            # see if player i is a bad guy
            self.bad_guys *= (1.0 - self.gameParams["alpha"])
            bad_guys_copy = self.bad_guys.copy()
            new_steals = self.infl_neg - (np.negative(self.prev_influence).clip(0) * (1.0 - self.gameParams["alpha"]))
            for i in range(num_players):
                for j in range(num_players):
                    if (new_steals[i][j] > 5.0):
                        if (bad_guys_copy[j] < 0.2):
                            if self.bad_guys[i] < 0.2:
                                self.printT(player_idx, ">>>>>> me thinks " + str(i) + " is a new bad guy")
                            self.bad_guys[i] += new_steals[i][j] / 1.0
                            if self.bad_guys[i] > 1.0:
                                self.bad_guys[i] = 1.0
                        elif (sum(self.infl_neg[j]) * 0.9) < sum(self.infl_neg[:,j]):
                            self.printT(player_idx, ">>>>>> bad guy " + str(j) + " has paid for its crimes")
                            self.bad_guys[j] = 0.0

            self.printT(player_idx, "   que mala onda: " + str(self.bad_guys))
            # if new_steals_by_i > 0.1:
            #     self.printT(player_idx, "player " + str(i) + " stole " + str(new_steals_by_i))

            self.printT(player_idx, " attacks_with_me: " + str(self.attacks_with_me))
            self.printT(player_idx, " others_attacks_on: " + str(self.others_attacks_on))
            self.printT(player_idx, "")
            # self.printT(player_idx, "infl_neg:")
            # self.printT(player_idx, str(self.infl_neg))


    # determines the proportion of total popularity player_idx would like to have in its selected group
    def compute_coalition_target(self, round_num, popularities, communities, player_idx):
        # compute self.coalition_target
        if self.genes["coalitionTarget"] < 80:
            if self.genes["coalitionTarget"] < 5:
                return 0.05
            else:
                return self.genes["coalitionTarget"] / 100.0
        elif round_num < 3:
            return 0.51
        else:
            in_mx = False
            mx_ind = -1
            fuerza = []
            tot_pop = sum(popularities)
            if tot_pop == 0:
                tot_pop = 1
            for s in communities:
                tot = 0.0
                for i in s:
                    tot += popularities[i]

                fuerza.append(tot / tot_pop)
                if mx_ind == -1:
                    mx_ind = 0
                elif tot > fuerza[mx_ind]:
                    mx_ind = len(fuerza)-1
                    if player_idx in s:
                        in_mx = True
                    else:
                        in_mx = False

            fuerza.sort(reverse=True)
            self.printT(player_idx, "   fuerza: " + str(fuerza))
            if in_mx:
                return min(fuerza[1] + 0.05, 55)
            else:
                return min(fuerza[0] + 0.05, 55)


    # determines how much each player owes player_idx
    def updateIndebtedness(self, round_num, player_idx, transaction_vec, popularities):
        # update the tally of indebtedness
        self.tally -= np.positive(transaction_vec).clip(0) * popularities[player_idx]
        self.tally[player_idx] = 0

        lmbda = 1.0 / (round_num + 1.0)
        if lmbda < self.gameParams["alpha"]:
            lmbda = self.gameParams["alpha"]
        self.expectedReturn = ((1-lmbda) * self.expectedReturn) + (lmbda * (transaction_vec * popularities[player_idx]))
        # self.printT(player_idx, "   expectedReturn: " + str(self.expectedReturn))
        self.ave_return = sum(self.expectedReturn) / len(self.expectedReturn)


    # literally 0 clue on how to correctly cap this to 10 tokens tops.
    def group_givings(self, round_num, num_players, num_tokens, num_giving_tokens, player_idx, influence, popularities,
                      selected_community, attack_alloc, extra_flag):
        # Change on 6/16
        if (num_giving_tokens <= 0):
            self.printT(player_idx, "              nothing left to give")
            group_alloc = np.zeros(num_players, dtype=int)
            return group_alloc, 0

        self.printT(player_idx, "\n Group Givings (" + str(num_tokens) + ", " + str(num_giving_tokens) + ")")

        # allocate tokens based on homophily
        # homophily_vec = self.get_homophily_vec(num_players, player_idx)
        # homophily_alloc, num_tokens_h = self.homophily_allocate_tokens(round_num, num_players, num_giving_tokens, player_idx, homophily_vec, popularities, attack_alloc)
        # self.printT(player_idx, "homophily_tokens: " + str(num_tokens_h))





        homophily_alloc = np.zeros(num_players, dtype=float)
        num_tokens_h = 0

        # group_alloc, num_tokens_g = self.group_allocate_tokens(player_idx, num_players,
        #                                                        num_giving_tokens - num_tokens_h, round_num, influence,
        #                                                        popularities, selected_community, attack_alloc)


        group_alloc, num_tokens_g = self.group_allocate_tokens(player_idx, num_players, num_giving_tokens - num_tokens_h, round_num, influence, popularities, selected_community, attack_alloc, extra_flag)

        if not extra_flag: # standard JHG behavior, play it safe.
            # # for now, just keep tokens that you don't know what to do with
            group_alloc[player_idx] += (num_giving_tokens - (num_tokens_h + num_tokens_g))
        # lets distribute these to our friends instead. power of friendship and all that.
        else: # non standard behavior, play it SC safe.
            extra_tokens = num_giving_tokens - (num_tokens_h + num_tokens_g)
            if len(selected_community.s) != 0:
                giving_tokens = extra_tokens // len(selected_community.s)
                for friend in selected_community.s:
                    group_alloc[friend] += giving_tokens




        # for now, just keep tokens that you don't know what to do with
        self.printT(player_idx,
                    "  tokens initially kept in give: " + str((num_giving_tokens - (num_tokens_h + num_tokens_g))))
        # group_alloc[player_idx] += (num_giving_tokens - (num_tokens_h + num_tokens_g))
        # self.printT(player_idx, "   homophily allocations: " + str(homophily_alloc) + " (" + str(num_tokens_h) + ")")
        self.printT(player_idx, "   initial group_alloc: " + str(group_alloc))

        # Change on June 21 and July 12
        if popularities[player_idx] > 0.0001:
            group_alloc, shave = self.dial_back(num_players, num_tokens, player_idx, homophily_alloc + group_alloc,
                                                popularities)
            # self.printT(player_idx, "     shave " + str(shave) + " tokens")
            self.printT(player_idx, "   group_alloc: " + str(group_alloc))
        self.printT(player_idx, "")

        # return homophily_alloc + group_alloc, num_tokens_h + num_tokens_g
        return group_alloc, sum(group_alloc)


    # so turns out that when the players have a very low popularity, sometimes this does NOT behave as inteded. 
    def dial_back(self, num_players, num_tokens, player_idx, give_alloc, popularities):
        perc_lmt = self.genes["limitingGive"] / 100.0

        shave = 0
        for i in range(num_players):
            if i == player_idx:
                continue

            if give_alloc[i] > 0:
                if popularities[i] <= 0 or popularities[player_idx] <= 0: # if others pops are negative WEIRD stuff happens.
                    continue
                lmt = int(((popularities[i] / popularities[player_idx]) * num_tokens * perc_lmt) + 0.5)
                if lmt < give_alloc[i]:
                    shave += give_alloc[i] - lmt
                    give_alloc[i] = lmt

        give_alloc[player_idx] += shave

        return give_alloc, shave


    def get_visualhomophily_similarity(self, player_idx, other):
        diff = abs(self.visualTraits[player_idx] - self.visualTraits[other])
        if diff < 20:
            return 1.0
        else:
            return 0.0
        

    def printT(self, player_idx, s):
        if player_idx == self.theTracked:
            print(s)
        

    def compute_adjacency(self, num_players):
        A = self.infl_pos.copy()
        for i in range(num_players):
            A[i][i] = self.infl_pos[i][i]
            for j in range(i+1, num_players):
                theAve = (self.infl_pos[i][j] + self.infl_pos[j][i]) / 2.0 
                theMin = min(self.infl_pos[i][j], self.infl_pos[j][i])
                A[i][j] = (theAve + theMin) / 2.0
                A[j][i] = A[i][j]

        return A


    def compute_neg_adjacency(self, num_players):
        A = self.infl_neg.copy()
        for i in range(num_players):
            A[i][i] = self.infl_neg[i][i]
            for j in range(i+1, num_players):
                theAve = (self.infl_neg[i][j] + self.infl_neg[j][i]) / 2.0 
                theMax = max(self.infl_neg[i][j], self.infl_neg[j][i])
                A[i][j] = theMax #(theAve + theMax) / 2.0
                A[j][i] = A[i][j]

        return A

    def group_allocate_tokens(self, player_idx, num_players, num_tokens, round_num, influence, popularities,
                              the_community, attack_alloc, extra_flag):
        # if player_idx == self.theTracked:
        #     print()
        #     print("This is my community:")
        #     the_community.print()
        # s_modified = the_community.s.copy()
        s_modified = sorted(the_community.s)
        for i in range(num_players):
            if attack_alloc[i] != 0:
                if i in s_modified:
                    # print("remove " + str(i) + " from " + str(s_modified))
                    s_modified.remove(i)

        # self.printT(player_idx, str(s_modified))

        toks = np.zeros(num_players, dtype=float)
        num_allocated = num_tokens
        if round_num == 0:
            if len(s_modified) == 1:
                toks[player_idx] = num_tokens
            else:
                for i in range(num_tokens):
                    # REMOVING RANDOM
                    # sel = random.sample(s_modified, 1)[0]
                    # while sel == player_idx:
                    #     sel = random.sample(s_modified, 1)[0]
                    # toks[sel] += 1
                    if self.forced_random:
                        v = self.getRand()
                        num = (v + (player_idx + 1)) % (len(s_modified) - 1)
                        # self.printT(player_idx, "num: " + str(v))
                    else:
                        num = np.random.randint(0, 1001) % (len(s_modified) - 1)

                    # self.printT(player_idx, str(num))
                    c = 0
                    sel = -1
                    for s in s_modified:
                        if s != player_idx:
                            if c == num:
                                sel = s
                                break
                            c += 1

                    if sel == -1:
                        print(str(num) + "; " + str(c) + "; " + str(s_modified))
                        sys.exit()

                    # self.printT(player_idx, "sel: " + str(sel))

                    toks[sel] += 1
        else:
            comm_size = len(s_modified)
            if comm_size <= 1:
                toks[player_idx] = num_tokens
            else:
                profile = []
                mag = 0.0
                for i in s_modified:
                    if (i != player_idx):  # and (self.punishable_debt[i] < limite):
                        sb = self.scaled_back_nums[i]  # self.scale_back(player_idx, i)
                        if sb > 0.0:
                            val = (self.infl_pos[i][player_idx] + 0.01) * sb
                            # if self.punishable_debt[i] > 0:
                            #     val *= 1.0 - (self.punishable_debt[i] / limite)
                            profile.append((i, val))
                            mag += val
                    # elif i != player_idx:
                    #     self.printT(player_idx, "player " + str(i) + " excluded")

                if mag > 0.0:
                    profile.sort(key=lambda a: a[1], reverse=True)

                    # print("profile " + str(player_idx) + ": " + str(profile))

                    remaining_toks = num_tokens
                    comm_size = len(profile)
                    fixed_usage = ((self.genes["fixedUsage"] / 100.0) * num_tokens) / comm_size
                    # self.printT(player_idx, "fixed_usage = " + str(fixed_usage))
                    flex_tokens = num_tokens - (fixed_usage * comm_size)
                    # flex_tokens = num_tokens - comm_size
                    for i in range(comm_size):
                        # give_em = int(1 + flex_tokens * (profile[i][1] / mag) + 0.5)
                        give_em = int(fixed_usage + flex_tokens * (profile[i][1] / mag) + 0.5)
                        if remaining_toks >= give_em:
                            toks[profile[i][0]] += give_em
                            remaining_toks -= give_em
                        else:
                            toks[profile[i][0]] += remaining_toks
                            remaining_toks = 0

                    while remaining_toks > 0:
                        for i in range(comm_size):
                            toks[profile[i][0]] += 1
                            remaining_toks -= 1
                            if remaining_toks == 0:
                                break

                else:
                    # need to make a new friend
                    self.printT(player_idx, "    can't figure out who to give my tokens to")

                    num_allocated = 0
                #     for i in range(num_players):
                #         toks[np.random.randint(0,num_players)] += 1

        return toks, num_allocated

    def scale_back(self, player_idx, quien):
        if self.govPlayer[quien] == 1:  # for now, don't scale back payments to the gov'ment
            return 1

        # consider scaling back if the other person is in debt to me
        if self.punishable_debt[quien] > 0:
            debtLimit = self.genes["otherishDebtLimits"] / 25.0
            self.printT(player_idx, debtLimit)
            if debtLimit > 0:
                denom = max(self.expectedReturn[quien], self.ave_return) * debtLimit
                # self.printT(player_idx, "   denom for " + str(quien) + ": " + str(denom))
                if denom == 0:
                    return 0.0
                else:
                    perc = 1.0 - (self.punishable_debt[quien] / denom)  # (self.expectedReturn[quien] * debtLimit))
                    if perc > 0.0:
                        # self.printT(player_idx, "backoff " + str(quien) + " by " + str(perc) + "(debtLimit = " + str(debtLimit) + ")")
                        return perc
                    else:
                        # self.printT(player_idx, "exclude " + str(quien) + " completely (debtLimit = " + str(debtLimit) + "; perc = " + str(perc) + ")")
                        return 0.0

        return 1.0


    # decide how many tokens to keep
    def cuanto_guardo(self, round_num, player_idx, num_players, num_tokens, popularities, received, selected_community, extra_flag):
        self_pop = popularities[player_idx]
        if np.isnan(self_pop):
            print("Here is our pop ", self_pop)

        if extra_flag:
            self_pop *= 10

        # Change on July 12
        self_pop = popularities[player_idx]
        # if extra_flag:
        #     self_pop *= 10

        if popularities[player_idx] <= self.gameParams["poverty_line"]:
            return 0

        if round_num == 0:
            self.underAttack = (self.genes["initialDefense"] / 100.0) * self_pop
        else:
            totalAttack = np.dot(np.negative(received[0:num_players]).clip(0), popularities[0:num_players])
            dUpdate = self.genes["defenseUpdate"] / 100.0
            self.underAttack = (self.underAttack * (1.0 - dUpdate)) + (totalAttack * dUpdate)
            if np.isnan(self.underAttack):
                print("here ar ethe values ", self.underAttack, " and ", dUpdate, " and ", totalAttack, " and ", totalAttack * dUpdate, ".")

        caution = self.genes["defensePropensity"] / 50.0
        try:
            self_defense_tokens = min(num_tokens, int(((self.underAttack * caution) / self_pop) * num_tokens + 0.5))
        except ValueError:                                                  # getting a nan here                        # and here
            print("Here is the value of everything ", num_tokens, " and ", self.underAttack, " and ", caution, " and ", self_pop, " and ", num_tokens)
            self_defense_tokens = num_tokens # just so it does SOMETHING.

        # are there attacks on my friends by outsiders?  if so, consider keeping more tokens
        # this can be compared to the self.fear_keeping function
        amigos = np.ones(num_players, dtype=int)
        enemigos = np.ones(num_players, dtype=int)
        for i in range(num_players):
            if i in selected_community:
                enemigos[i] = 0
            else:
                amigos[i] = 0

        sm = 0.0
        for i in range(num_players):
            if amigos[i]:
                sm = max(np.dot(enemigos, self.infl_neg[:,i]), sm)

        denom = sum(self.infl_pos[:,player_idx])
        if denom > 0:
            fear_tokens = int((sm / sum(self.infl_pos[:,player_idx]) * num_tokens) + 0.5)
        else:
            fear_tokens = 0
        fear_tokens = int(fear_tokens * (self.genes["fearDefense"] / 50.0) + 0.5)

        tokens_guardado = min(max(self_defense_tokens, fear_tokens), num_tokens)

        min_guardado = int((self.genes["minKeep"] / 100.0) * num_tokens + 0.5)
        tokens_guardado = max(tokens_guardado, min_guardado)

        return tokens_guardado


    # Changes in May
    def quien_ataco(self, round_num, player_idx, num_players, num_tokens, remaining_toks, popularities, influence, selected_community, communities):
        # my_community = set()
        # for s in communities:
        #     if player_idx in s:
        #         my_community = s
        #         break
        # self.printT(player_idx, "   attacks with me prior: " + str(self.attacks_with_me_prior(num_players, player_idx, my_community, popularities, self.genes["warFury"] / 100.0)))

        group_cat = self.groupCompare(num_players, player_idx, popularities, communities)

        pillage_choice = self.pillage_the_village(round_num, player_idx, num_players, selected_community, num_tokens, remaining_toks, popularities, influence, group_cat)
        vengence_choice = self.take_vengence(round_num, player_idx, num_players, selected_community, num_tokens, remaining_toks, popularities, influence)
        defend_friend_choice = self.defend_friend(player_idx, num_players, num_tokens, remaining_toks, popularities, influence, selected_community, communities, group_cat)
        # # startwar_choice = self.start_guerra(round_num, player_idx, num_players, num_tokens, remaining_toks, popularities, influence, selected_community, communities)
        # # joinwar_choice = self.join_guerra(round_num, player_idx, num_players, num_tokens, remaining_toks, popularities, influence, selected_community, communities)

        self.printT(player_idx, "   pillage_choice: " + str(pillage_choice))
        self.printT(player_idx, "   vengence_choice: " + str(vengence_choice))
        self.printT(player_idx, "   defend_friend_choice: " + str(defend_friend_choice))
        # # self.printT(player_idx, "   startwar_choice: " + str(startwar_choice))
        # # self.printT(player_idx, "   joinwar_choice: " + str(joinwar_choice))

        attack_toks = np.zeros(num_players, dtype=int)
        # # if pillage_choice[0] >= 0:
        # #     attack_toks[pillage_choice[0]] = pillage_choice[1]

        attack_possibilities = []
        if (pillage_choice[0] >= 0):
            attack_possibilities.append((self.genes["pillagePriority"], pillage_choice[0], pillage_choice[1]))
        if (vengence_choice[0] >= 0):
            attack_possibilities.append((self.genes["vengencePriority"], vengence_choice[0], vengence_choice[1]))
        if (defend_friend_choice[0] >= 0):
            attack_possibilities.append((self.genes["defendFriendPriority"], defend_friend_choice[0], defend_friend_choice[1]))

        # # decide which attack to do
        if len(attack_possibilities) > 0:
            attack_possibilities.sort(key=lambda a: a[0], reverse=True)
            self.printT(player_idx, "  Sorted attack: " + str(attack_possibilities))
            if (attack_possibilities[0][1] != defend_friend_choice[0]) or (attack_possibilities[0][2] != defend_friend_choice[1]):
                self.expected_defend_friend_damage = -99999
            attack_toks[attack_possibilities[0][1]] = attack_possibilities[0][2]
        else:
            self.expected_defend_friend_damage = -99999

        # # self.printT(player_idx, "        expected_defend_friend_damage: " + str(self.expected_defend_friend_damage))

        return attack_toks, sum(attack_toks)


