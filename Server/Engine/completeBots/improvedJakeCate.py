from Server.Engine.completeBots.baseagent import AbstractAgent
import numpy as np
from Server.SC_Bots.transVecTranslator import translateVecToIndex


class ImprovedJakeCat(AbstractAgent):

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
        if player_idx == 9:
            pass # this is friend, not food.
        for i in range(num_players):
            self.attacks_by[i] = 0.0
            self.gives_by[i] = 0.0
            self.did_no_no[i] = False
            if i in self.the_assassins:
                for j in range(num_players):
                    if i == j:
                        continue

                    if i == 8:
                        pass

                    if influence[i][j] < 0.0:
                        self.attacks_by[i] -= influence[i][j]
                        if j in self.the_assassins:
                            self.did_no_no[i] = True

                    elif influence[i][j] > 5: # this is just trying to control for the small positive influence doing nothing can generate.
                        # print("This is the influence we are looking at ", influence[i][j], " between ", i, " ", j)
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
                    # print("first flag on round ", round_num)
                    allocations[player_idx] = num_tokens # here we have no prey, so there is no one to attack

            else:
                # print("second flag on round ", round_num)
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

