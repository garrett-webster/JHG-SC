from Server.Engine.completeBots.baseagent import AbstractAgent
import numpy as np
from Server.SC_Bots.transVecTranslator import translateVecToIndex


class CantisFirst(AbstractAgent):

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
        self.the_assassins = {i for i in range(num_players)} # assume everyone is a plyer until proven otherwise.
        self.attacks_on_me = 0.0

    def subtract_cat(self, player_idx):
        if player_idx in self.the_assassins:
            self.the_assassins.pop(player_idx, None) # boom shakalacka


    def play_round(self, player_idx, round_num, recieved, popularities, influence, extra_data, current_options_matrix, peeps, extra_flag=False):
        # this is what we will always need
        allocations = np.zeros_like(popularities)
        num_players = len(popularities)
        num_tokens = 2 * num_players

        if extra_flag == True:
            pass # we are voting, not creating allocations.
            if round_num == 0:
                self._init_vars(num_players)
                # look for someone saving all they tokens
                for i, allocation in enumerate(current_options_matrix):
                    pass # need to actually chekc to make sure htye are all in the same spot
                    if num_tokens not in allocation:
                        self.subtract_cat(player_idx) # didn't asave all they tokens on the first round


            else: # the round number is greater than 1 for votes
                # look for the FIRST vote that attacks a non cat
                for allocation in current_options_matrix:
                    if -num_tokens in allocation:
                        if allocation.index[-num_tokens] not in self.the_assassins:
                            allocations = allocation # just return that vote
                            return allocations # early return so we do the first possible one
                        else:
                            pass
                # if we get all the way here and its NOTHING, we still just look for the first possible victim.
                for player_idx in range(num_players):
                    if player_idx not in self.the_assassins:
                        allocations[player_idx] = -num_tokens
                        return allocations


        if extra_flag == False:
            pass # we are either playing JHG or creating allocations. for the purpose of this bot, creating allocations.
            if round_num == 0:
                self._init_vars(num_players)
                allocations[player_idx] = num_tokens # just save everything
            else:
                for player_idx in range(num_players):
                    if player_idx not in self.the_assassins:
                        allocations[player_idx] = -num_tokens
                        return allocations
                    else:
                        return allocations # just all zero's, I don't really knwow ath to do if this doesn't work out.

        # the extra flag does not matter to him, but it matters to teh other bots.




            # allocations = (allocations / np.linalg.norm(allocations, ord=1)) * 2 * len(allocations)
            return allocations # return it to a more normal magnitude. # the engine doesn't care if its normalized or not, but the SC sim does care. deeply.

    def setGameParams(self, gameParams, _forcedRandom):
        self.gameParams = gameParams
        self.forced_random = _forcedRandom

    def getType(self):
        return self.whoami

    def get_vote(self, player_idx, round_num, received, popularities, influence, extra_data, current_options_matrix, enforce_majority, peeps):
        transaction_vector = self.play_round(player_idx, round_num, received, popularities, influence, extra_data, current_options_matrix, peeps, True, )
        final_vote = translateVecToIndex(transaction_vector, current_options_matrix, enforce_majority)
        return final_vote  # please let this work

