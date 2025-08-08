# purpose is to make these cats like
# actually viable within the SC thing.
# should be easier than trying to adapt the gene3 bot.
# lets find out.

from Server.Engine.completeBots.baseagent import AbstractAgent
import numpy as np
from Server.SC_Bots.transVecTranslator import translateVecToIndex



class SocialWelfare(AbstractAgent):


    def __init__(self):
        super().__init__()
        self.whoami = "SW"
        self.friends = set()
        self.enemies = set()
        self.gameParams = {}
        self.attacks_by = None
        self.gives_by = None
        self.did_no_no = None
        self.attacks_on_me = 0.0
        self.gameParams = {}

    def _init_vars(self, num_players):
        self.attacks_by = np.zeros(num_players)
        self.friends = {i for i in range(num_players)}
        # keep self.enemies blank for now
        self.gives_by = np.zeros(num_players)
        self.did_no_no = np.array([False for _ in range(num_players)])
        self.the_assassins = {i for i in range(num_players)}
        self.attacks_on_me = 0.0

    def _update_vars(self, num_players, player_idx, influence, round_num):
        for i in range(num_players):
            self.attacks_by[i] = 0.0
            self.gives_by[i] = 0.0
            self.did_no_no[i] = False
            if i in self.friends:
                for j in range(num_players):
                    if i == j: # don't check self references, just gets weird.
                        continue

                    if influence[i][j] < 0.0: # if there has been an attack
                        self.attacks_by[i] -= influence[i][j] # make sure we can guard ourselves
                        if j in self.friends: # if this was an attack on a fellow kitty
                            self.did_no_no[i] = True # he is no longer a brother.

                    # # lets make it so that they can in fact give to other assassins.
                    # elif influence[i][j] > 0.0: # if a "give" has taken place
                    #     self.gives_by[i] += influence[i][j]
                    #     if j not in self.friends: # if he has given to a non assassin
                    #         self.did_no_no[i] = True # he is no longer a brother.

        for i in range(num_players): # iterate through and throw out all of the no no squares
            if i in self.friends and self.did_no_no[i]:
                self.friends.remove(i)
                self.enemies.add(i)

    def play_round(self, player_idx, round_num, recieved, popularities, influence, extra_data, extra_flag=False):
        # the extra flag does not matter to him, but it matters to teh other bots.
        #print("This is if we are playing SC ", extra_flag, " and here are the assassins ", self.the_assassins)
        if round_num == 1:
            pass # un poco de investigacion
        num_players = len(popularities)
        if round_num == 0:
            self._init_vars(num_players) # we creative in this house
        else:
            self._update_vars(num_players, player_idx, influence, round_num)

        if not extra_flag:
            allocations = self.jhg_sw_behavior(player_idx, round_num, recieved, popularities, influence, extra_data)
            return allocations / np.linalg.norm(allocations, ord=1)


        else:
            allocations = self.sc_sw_behavior(player_idx, round_num, recieved, popularities, influence, extra_data)
            return allocations


    # need to check if we are in JHG or SC. start giving to eachtoerh more in SC
    def jhg_sw_behavior(self, player_idx, round_num, recieved, popularities, influence, extra_data):

        allocations = np.zeros_like(popularities)
        num_players = len(popularities)
        num_tokens = 2 * num_players
        toks_to_share = 0
        if len(self.friends) > 0:
            if len(self.enemies) > 0:
                for i in self.enemies:
                    if popularities[i] > 1: # only steal if there is something worth stealing
                        allocations[i] = -10
                        toks_to_share += 10

            token_allocation = (num_tokens + toks_to_share) // len(self.friends) # don't forget floor division!

            for i in self.friends:
                allocations[i] = token_allocation
        else:  # this is icky and I don't like it but here we go anyway.
            allocations[player_idx] = num_tokens

        return allocations  # return it to a more normal magnitude. # the engine doesn't care if its normalized or not, but the SC sim does care. deeply.

    def sc_sw_behavior(self, player_idx, round_num, recieved, popularities, influence, extra_data):
        # the steali

        allocations = np.zeros_like(popularities)
        num_players = len(popularities)
        num_tokens = 2 * num_players
        toks_to_share = 0
        if len(self.friends) > 0:
            if len(self.enemies) > 0:
                for i in self.enemies: #sc always steal, blow them to smithereens
                    allocations[i] = -10
                    toks_to_share += 10

            token_allocation = (num_tokens + toks_to_share) // len(self.friends) # don't forget floor division!

            for i in self.friends:
                allocations[i] = token_allocation
            for i in self.enemies:
                allocations[i] = -10
        else:  # this is icky and I don't like it but here we go anyway.
            allocations[player_idx] = num_tokens

        return allocations  # return it to a more normal magnitude. # the engine doesn't care if its normalized or not, but the SC sim does care. deeply.

    def setGameParams(self, gameParams, _forcedRandom):
        self.gameParams = gameParams
        self.forced_random = _forcedRandom

    def getType(self):
        return self.whoami

    def get_vote(self, player_idx, round_num, received, popularities, influence, extra_data, current_options_matrix, enforce_majority):
        transaction_vector = self.play_round(player_idx, round_num, received, popularities, influence, extra_data, True)
        final_vote = translateVecToIndex(transaction_vector, current_options_matrix, enforce_majority)
        return final_vote  # please let this work

