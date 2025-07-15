import random
import numpy as np

class Random():
    def __init__(self, new_id, utility_per_player=6):
        self.number_type = 0  # used for logging purposes.
        self.self_id = new_id
        self.utility_per_player = utility_per_player

    def get_number_type(self):  # used for logging.
        return self.number_type

    def create_column(self, total_players):
        n = total_players
        alpha = [1] * n  # Symmetric Dirichlet distribution parameters
        alpha[1] = 0.1  # not sure why or even if this matters.
        alpha = np.ones(n)  # np.random.uniform(0, 10, size=n)
        c = 1  # Constant for the L1 norm

        # Generate a number of samples
        num_samples = 1
        samples = (np.random.dirichlet(alpha, size=num_samples) * np.hstack
        ([np.ones((num_samples, 1)), np.random.choice([-1, 1], p=[0.5, 0.5], size=(num_samples, n - 1))]))
        transaction_vector = samples[0]

        # we need to do a little swap er roo bc the first value is never negative.
        temp_var = transaction_vector[self.self_id]
        transaction_vector[self.self_id] = transaction_vector[0]
        transaction_vector[0] = temp_var

        if transaction_vector[self.self_id] < 0:
            transaction_vector[self.self_id] = transaction_vector[self.self_id] * -1

        return transaction_vector * self.utility_per_player