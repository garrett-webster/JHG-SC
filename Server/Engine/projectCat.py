# purpose is to make these cats like
# actually viable within the SC thing.
# should be easier than trying to adapt the gene3 bot.
# lets find out.

from Server.Engine.baseagent import AbstractAgent
import numpy as np
from Server.SC_Bots.transVecTranslator import translateVecToIndex


class ProjectCat(AbstractAgent):

    def __init__(self):
        super().__init__()
        self.whoami = 'jake cat'
        self.is_initialized = False
        self.the_assassins = {}
        self.attacks_by = None
        self.gives_by = None
        self.did_no_no = None
        self.attacks_on_me = 0.0
        self.gameParams = {}

    def _init_vars(self, num_players):
        self.attacks_by = np.zeros(num_players)
        self.gives_by = np.zeros(num_players)
        self.did_no_no = np.array([False for _ in range(num_players)])
        self.the_assassins = {i for i in range(num_players)}
        self.attacks_on_me = 0.0

    def _update_vars(self, num_players, player_idx, influence):
        # print("here are the assassins going into this ", self.the_assassins)
        for i in range(num_players):
            self.attacks_by[i] = 0.0
            self.gives_by[i] = 0.0
            self.did_no_no[i] = False
            if i in self.the_assassins:
                for j in range(num_players):
                    if i == j:
                        continue

                    if influence[i][j] < 0.0:
                        self.attacks_by[i] -= influence[i][j]
                        if j in self.the_assassins:
                            self.did_no_no[i] = True

                    # lets make it so that they can in fact give to other assassins.
                    elif influence[i][j] > 5 and i not in self.the_assassins: # this is just trying to control for the small positive influence doing nothing can generate.
                        self.gives_by[i] += influence[i][j]
                        self.did_no_no[i] = True

        for i in range(num_players):
            if i in self.the_assassins and (
                    self.did_no_no[i] or ((self.attacks_by[player_idx] > 0.0) and (self.attacks_by[i] == 0.0))):
                # print("this is who we are removing ", i, " and this is why ", self.did_no_no[i], " ", (self.attacks_by[player_idx] > 0.0 and self.attacks_by[i] == 0))
                self.the_assassins.remove(i)

    def _attacks_on_self(self, numPlayers, received, popularities):
        amount = 0.0
        for i in range(numPlayers):
            if received[i] < 0:
                amount += received[i] * popularities[i]

        return -amount

    def _get_my_proportion(self, player_idx):
        assassin_damage = 0.0
        for i in self.the_assassins:
            assassin_damage += self.attacks_by[i]

        return ((self.attacks_by[player_idx] + 0.000001) / (assassin_damage + 0.000001))

    def play_round(self, player_idx, round_num, recieved, popularities, influence, extra_data, extra_flag=False):
        # the extra flag does not matter to him, but it matters to teh other bots.

        if not extra_flag: # normal stuff
            allocations = self.jhg_kitty_behavior(player_idx, round_num, recieved, popularities, influence, extra_data)

        else:
            if player_idx == 10:
                pass # wanna see whats goign on here.
            allocations = self.sc_kitty_behavior(player_idx, round_num, recieved, popularities, influence, extra_data)
            if player_idx == 10: # guranteed to be a cat.
                print("this is the allocation we are returning from the SC kitty ", allocations)
                print("these are who we think are the other cats btw ", self.the_assassins)

        return allocations


    def sc_kitty_behavior(self, player_idx, round_num, recieved, popularities, influence, extra_data):
        allocations = np.zeros_like(popularities)
        num_players = len(popularities)
        num_tokens = 2 * num_players

        if round_num == 0:  # save ALL ya tokens. simple as.
            self._init_vars(num_players)
            allocations[player_idx] = min(10, num_tokens)
            return allocations
        else:  # now we ahve to do like, actual math. bleh.
            alpha = self.gameParams.get('alpha', 0.15)
            steal_coef = self.gameParams.get('steal', 1.6)
            keep_coef = self.gameParams.get('keep', 0.95)

            self._update_vars(num_players, player_idx, influence)  # try to figure out who the other kitties are.

            keep_tokens = 0

            if popularities[player_idx] >= 0.5:  # if they have more than half a popularity point, nuke em.
                attacked = self._attacks_on_self(num_players, recieved, popularities)
                w = 0.65
                self.attacks_on_me = w * attacked + (1 - w) * self.attacks_on_me
                keep_tokens = min((int)((self.attacks_on_me / popularities[player_idx]) + 0.5),
                                  num_tokens)  # figure out how many people attacked me last round and try to plan accordinly

                prey_idx = None  # Changed from -1 cause python (This was weird)
                prey_pop = 99999.0
                attack_proportion = 0.0
                prop_assassin_attack = self._get_my_proportion(player_idx)
                attack_power = (popularities[
                                    player_idx] / prop_assassin_attack) * steal_coef * alpha  # figure out how much power I am actually weilding

                for i in range(num_players):
                    if i not in self.the_assassins:  # check all the non friends
                        if (popularities[i] < prey_pop) and (popularities[i] >= (
                                attack_power / 2.0)):  # can I actually take them out? Do I have the attack power and do they have low enough popularity?
                            prey_idx = i  # pop them in my sights
                            prey_pop = popularities[i]
                            attack_proportion = min(popularities[i] / attack_power,
                                                    1.0)  # calculate just how badly we will destroy them

                if prey_idx is not None:  # just how bad can we mash them up
                    # we can't take more than 10 from a person
                    steal_tokens = min(10, (int)((attack_proportion * 0.9) * (num_tokens - keep_tokens)))
                    allocations[prey_idx] = -steal_tokens
                    available_tokens = num_tokens + steal_tokens # utility works different here
                    num_friends = max (len(self.the_assassins), 1)
                    friend_allocation = int(min(10, (available_tokens / num_friends)))
                    for player in self.the_assassins:
                        allocations[player] = friend_allocation

                else:  # this is what we need to change, her and here.
                    allocations[player_idx] = num_tokens  # here we have no prey, so there is no one to attack
                    num_tokens_to_allocate = num_tokens / (len(self.the_assassins))
                    for i in self.the_assassins:
                        allocations[i] = num_tokens_to_allocate

            else:
                allocations[player_idx] = num_tokens  # here there is no one WORTH attacking. big difference. # lets make social welfare here.
                num_tokens_to_allocate = num_tokens / (len(self.the_assassins))
                for i in self.the_assassins:
                    allocations[i] = num_tokens_to_allocate


            # allocations = (allocations / np.linalg.norm(allocations, ord=1)) * 2 * len(allocations)
            #allocations = self.adjust_for_sc(allocations, num_tokens)
            return allocations  # return it to a more normal magnitude. # the engine doesn't care if its normalized or not, but the SC sim does care. deeply.

    # def adjust_for_sc(self, allocations, num_tokens):
    #     max_pos_sum = sum(x for x in allocations if x > 0)
    #     max_neg = min((x for x in allocations if x < 0), default=-1)  # most negative (smallest)
    #
    #     result = []
    #     for x in allocations:
    #         if x > 0:
    #             result.append(x / max_pos_sum)
    #         elif x < 0:
    #             result.append(-x / abs(max_neg) * -1)  # keep sign, scale between -1 and 0
    #         else:
    #             result.append(0)
    #
    #     # aight we do negatives first
    #     for i, x in enumerate(result):
    #         if x < 0:
    #             result[i] = x * 10 # max negative we can have is -10 and having it be the range should solve that
    #
    #     neg_sum = sum(x for x in allocations if x < 0) # get to the total negatives
    #     num_tokens -= neg_sum # increase the num tokens by that much
    #     # this is where stuff gets weird.
    #     # so we need to find the max allocation and scale that to 10, and then go from there
    #     for i, x in enumerate(result):
    #         if x > 0:
    #             result[i] = min(10, x * num_tokens)
    #     print("these are the results we are returning from the kitties ", result)
    #     return result

    def jhg_kitty_behavior(self, player_idx, round_num, recieved, popularities, influence, extra_data):

        allocations = np.zeros_like(popularities)
        num_players = len(popularities)
        num_tokens = 2 * num_players

        if round_num == 0: # save ALL ya tokens. simple as.
            self._init_vars(num_players)
            allocations[player_idx] = num_tokens
            return allocations
        else: # now we ahve to do like, actual math. bleh.
            alpha = self.gameParams.get('alpha', 0.15)
            steal_coef = self.gameParams.get('steal', 1.6)
            keep_coef = self.gameParams.get('keep', 0.95)

            self._update_vars(num_players, player_idx, influence) # try to figure out who the other kitties are.

            keep_tokens = 0

            if popularities[player_idx] >= 0.5: # if they have more than half a popularity point, nuke em.
                attacked = self._attacks_on_self(num_players, recieved, popularities)
                w = 0.65
                self.attacks_on_me = w * attacked + (1 - w) * self.attacks_on_me
                keep_tokens = min((int)((self.attacks_on_me / popularities[player_idx]) + 0.5), num_tokens) # figure out how many people attacked me last round and try to plan accordinly

                prey_idx = None  # Changed from -1 cause python (This was weird)
                prey_pop = 99999.0
                attack_proportion = 0.0
                prop_assassin_attack = self._get_my_proportion(player_idx)
                attack_power = (popularities[player_idx] / prop_assassin_attack) * steal_coef * alpha # figure out how much power I am actually weilding

                for i in range(num_players):
                    if i not in self.the_assassins: # check all the non friends
                        if (popularities[i] < prey_pop) and (popularities[i] >= (attack_power / 2.0)): # can I actually take them out? Do I have the attack power and do they have low enough popularity?
                            prey_idx = i # pop them in my sights
                            prey_pop = popularities[i]
                            attack_proportion = min(popularities[i] / attack_power, 1.0) # calculate just how badly we will destroy them

                if prey_idx is not None: # just how bad can we mash them up
                    steal_tokens = (int)((attack_proportion * 0.9) * (num_tokens - keep_tokens))
                    allocations[prey_idx] = -steal_tokens
                    allocations[player_idx] = num_tokens - steal_tokens
                else: # this is what we need to change, her and here.
                    allocations[player_idx] = num_tokens # here we have no prey, so there is no one to attack

            else:
                allocations[player_idx] = num_tokens # here there is no one WORTH attacking. big difference. # lets make social welfare here.
                num_friends = len(self.the_assassins)

            # allocations = (allocations / np.linalg.norm(allocations, ord=1)) * 2 * len(allocations)
            return allocations # return it to a more normal magnitude. # the engine doesn't care if its normalized or not, but the SC sim does care. deeply.

    def setGameParams(self, gameParams, _forcedRandom):
        self.gameParams = gameParams
        self.forced_random = _forcedRandom

    def getType(self):
        return self.whoami

    def get_vote(self, player_idx, round_num, received, popularities, influence, extra_data, current_options_matrix, enforce_majority):
        transaction_vector = self.play_round(player_idx, round_num, received, popularities, influence, extra_data, True)
        final_vote = translateVecToIndex(transaction_vector, current_options_matrix, enforce_majority)
        return final_vote  # please let this work

