# from Server.SC_Bots.transVecTranslator import translateVecToIndex
from stagHare.transVecTranslatorStagHare import translateVecToIndexStagHare
import numpy as np
from stagHare.utils.a_star import AStar


from stagHare.utils.pathfindingTime import findPath

# Right now this doesn't actually DO anything, it just returns a random vector with no regard for the movement. I want to get the code actually RUNNING before we make it good
# can't edit a blank peice of paper, you feel?
def movement_to_allocation(new_movement, state, id):
    # we need to take in the new movement, decide what they are moving towards, if anything, and then create a new allocation based on that
    # for now, lets create a random transaction

    numPlayers = len(state.hunters)
    n = numPlayers
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
    temp_var = transaction_vector[id]
    transaction_vector[id] = transaction_vector[0]
    transaction_vector[0] = temp_var

    if transaction_vector[id] < 0:
        transaction_vector[id] = transaction_vector[id] * -1

        # print("here is the transaction_vector: \n", transaction_vector)
    # print("Here is the sum of the transaction_vector: \n", np.sum(transaction_vector))
    return transaction_vector