from Server.SC_Bots.transVecTranslator import translateVecToIndex
import numpy as np

def allocation_to_movement(new_allocation, id, state):
    pass
    hare = [-2.5, -2.5, 1]
    stag = [2, 2, 2]
    nothing = [0, 0, 0]
    new_current_options_matrix = [nothing, hare, stag]
    new_index = translateVecToIndex(new_allocation, new_current_options_matrix, False)
    if new_index == -1:
        return [0, 0] # don't move anywhere.

    if new_index == 0:
        move_to_hare(state, id)

    if new_index == 1:
        move_to_stag(state, id)


def move_to_hare(state, id):
    hare_position = [0, 0]
    # hare_position = state.hare
    # modify these as you go
    possible_hare_positions = [[[hare_position[0], hare_position[1]], [hare_position[0], hare_position[1]], [hare_position[0], hare_position[1]], [hare_position[0], hare_position[1]]]]
    player_position = state.player


def move_to_stag(state, id):
    stag_position = state.stag
    possible_stag_posiitons = state.stag # fix the rest of this to suybtract other occupied spaces
    player_position = state.player



# this is going to SUCK.

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
