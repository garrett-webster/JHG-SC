from Server.Engine.completeBots.baseagent import AbstractAgent
import numpy as np
from Server.SC_Bots.transVecTranslator import translateVecToIndex


class CantisFirst(AbstractAgent):

    def __init__(self):
        super().__init__()
        self.whoami = 'jake cat'
        self.the_assassins = {}
        self.did_no_no = None

    def _init_vars(self, num_players):
        self.the_assassins = {i for i in range(num_players)} # assume everyone is an assassin until proven otherwise.
        self.did_no_no = np.array([False for _ in range(num_players)]) # helps us keep track of who to kick out as we go.


    def update_vars(self, num_players, player_idx, influence): # use the influence matrix to figure out how has been giving to other people. cross them off if they have.

        for i in range(num_players):
            self.did_no_no[i] = False

            if i in self.the_assassins:
               for j in range(num_players):

                   if influence[i][j] < 0.0:
                       if j in self.the_assassins:
                           self.did_no_no[i] = True

                   elif influence[i][j] > 5: # sometimes doing nothing can generate small amounts of positive ifnluence
                       self.did_no_no[i] = True # no giving! bad.

        for i in range(num_players):
            if i in self.the_assassins and self.did_no_no[i]:
                self.the_assassins.remove(i) # get that kitty out of here.


    def subtract_cat(self, player_idx): # main method of getting people off the list
        if player_idx in self.the_assassins:
            self.the_assassins.pop(player_idx, None) # boom shakalacka
        else:
            print("just for funzies, we tried to delete and already deleted cat.")


    def play_round(self, player_idx, round_num, recieved, popularities, influence, extra_data, current_options_matrix, extra_flag=False):
        # this is what we will always need
        current_options_matrix = list(zip(*current_options_matrix)) # just transpose the fetcher just in case.
        allocations = list(np.zeros_like(popularities)) # give us a place to start
        num_players = len(popularities) # get the num players
        num_tokens = 2 * num_players # get the total utility for the allocation

        if extra_flag == False: # WE ARE CREATING ALLOCATIONS. No awy to remove cats here, so don't try too hard to make that happen.
            pass # we are either playing JHG or creating allocations. for the purpose of this bot, creating allocations.
            if round_num == 0:
                self._init_vars(num_players) # init assassins list
                allocations[player_idx] = num_tokens # just save everything
            else: # we are in rounds 1+, so vote for anyone who saved all tokens.
                for plyr in range(num_players):
                    if plyr not in self.the_assassins:
                        allocations[plyr] = -num_tokens
                        return allocations
                    else:
                        allocations[player_idx] = num_tokens
                        return allocations # just keep everything IG.


        # this section can't have an early returns, otherwise that will ruin things. so make sure to return everything at the end, we can handle edge cases better that way.
        if extra_flag == True: # this is where we can see things and start trying to remove cats.
            pass # we are voting, not creating allocations.
            if round_num == 0:
                self._init_vars(num_players)
                # look for someone saving all they tokens
                for i, allocation in enumerate(current_options_matrix):
                    pass # need to actually chekc to make sure htye are all in the same spot
                    if num_tokens in allocation:
                        allocations = allocation



            else: # the round number is greater than 1 for votes
                self.update_vars(num_players, player_idx, influence)
                # look for the FIRST vote that attacks a non cat
                for allocation in current_options_matrix: # these ARE Tuples, for whatever reason.
                    if -(num_tokens) in allocation:
                        if allocation.index(-num_tokens) not in self.the_assassins:
                            allocations = list(allocation) # just return that vote # and make sure to make it a list rather than a tuples.
                # if we get all the way here and its NOTHING, we still just look for the first possible victim.
                for plyr in range(num_players):
                    if plyr not in self.the_assassins:
                        allocations[plyr] = -num_tokens

            if np.all(allocations == 0):
                print("Unexepcted behavior. think about this later. ")
                for i in range(num_players):
                    if i not in self.the_assassins:
                        allocations[i] = -num_tokens



            # allocations = (allocations / np.linalg.norm(allocations, ord=1)) * 2 * len(allocations)

        allocations = [max(min(x, 10), -10) for x in allocations] # clamp those fetchers to be between -10 and 10

        return allocations # return it to a more normal magnitude. # the engine doesn't care if its normalized or not, but the SC sim does care. deeply.

    def setGameParams(self, gameParams, _forcedRandom):
        self.gameParams = gameParams
        self.forced_random = _forcedRandom

    def getType(self):
        return self.whoami

    def get_vote(self, player_idx, round_num, received, popularities, influence, extra_data, current_options_matrix, enforce_majority):
        transaction_vector = self.play_round(player_idx, round_num, received, popularities, influence, extra_data, current_options_matrix, True)
        final_vote = translateVecToIndex(transaction_vector, current_options_matrix, enforce_majority)
        return final_vote  # please let this work

