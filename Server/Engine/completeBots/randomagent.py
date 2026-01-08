from Server.Engine.completeBots.baseagent import AbstractAgent
import numpy as np

class RandomAgent(AbstractAgent):

    def __init__(self, tokens_per_player):
        super().__init__()
        self.whoami = "Random"
        self.tokens_per_player = tokens_per_player
        self.pop_history = []  # just slap this up here.
        self.gameParams = {}


    def setGameParams(self, gameParams, _forcedRandom):
        self.gameParams = gameParams


    def getType(self):
        return self.whoami


    def play_round(self, player_idx, round_num, received, popularities, influence, extra_data, flag=False):
        numPlayers = len(received)
        n = numPlayers
        alpha = [1] * n  # Symmetric Dirichlet distribution parameters
        alpha[1] = 0.1 # not sure why or even if this matters.
        alpha = np.ones(n)  # np.random.uniform(0, 10, size=n)
        c = 1  # Constant for the L1 norm

        # Generate a number of samples
        num_samples = 1
        samples = (np.random.dirichlet(alpha, size=num_samples) * np.hstack
            ([np.ones((num_samples, 1)), np.random.choice([-1, 1], p=[0.5, 0.5], size=(num_samples, n - 1))]))
        transaction_vector = samples[0]

        # we need to do a little swap er roo bc the first value is never negative.
        temp_var = transaction_vector[player_idx]
        transaction_vector[player_idx] = transaction_vector[0]
        transaction_vector[0] = temp_var



        if transaction_vector[player_idx] < 0:
            transaction_vector[player_idx] = transaction_vector[player_idx] * -1


        if flag: # if true, we are in an SC conundrum. scale appropriately.
            transaction_vector *= numPlayers

            # print("here is the transaction_vector: \n", transaction_vector)
        # print("Here is the sum of the transaction_vector: \n", np.sum(transaction_vector))
        return transaction_vector



    def get_vote(self, current_options_matrix, previous_votes, cycle, max_cycle):
        num_options = [-1, 0, 1, 2]
        return np.random.choice(num_options)
