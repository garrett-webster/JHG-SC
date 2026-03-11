# from Server.SC_Bots.transVecTranslator import translateVecToIndex
from stagHare.transVecTranslatorStagHare import translateVecToIndexStagHare
import numpy as np
from stagHare.utils.a_star import AStar


from stagHare.utils.pathfindingTime import findPathGreedy
from stagHare.utils.pathfindingTime import findPathTeamAware


# old allcation to movement. needs work. tank needs fuel.
def allocation_to_movement(new_allocation, id, state):
    pass
    # hare = [-2, -2, 2] # just for simplicity sake. # This is just as easy as it gets.
    # stag = [2, 2, 2]

    # this SHOULD be better.
    # this was the old version want
    # hare = np.zeros(3)
    # hare.fill(-2)
    # hare[id] = 2

    # way less altruistic version we got going on here.
    hare = np.zeros(3)
    hare.fill(0)
    hare[id] = 6


    stag = np.zeros(3)
    stag.fill(2)

    # print("we are working with id ", id)
    # print("this is the new allocation ", new_allocation)
    # print("this is the corresponding hare thing ", hare)
    # nothing should be created automatically.
    new_current_options_matrix = [hare, stag]
    # return this so we have a means with which we can specify the bots current eating desire.
    new_index = translateVecToIndexStagHare(new_allocation, new_current_options_matrix, False)
    new_movement = generate_movement(state, id, new_index)

    type = "Stag"
    if new_index == 0:
        type = "Hare"
    print("Here is teh agent ", id, " and here is the movement type ", type)

    # print('this is the new movement ', new_movement)
    return new_movement[0], new_movement[1], new_index==0

def generate_movement(state, id, new_index):
    player_name = "R" + str(id) # zero index, then 2 agetns in front of them.
    player_position = state.agent_positions[player_name]
    curr_row, curr_col = player_position[0], player_position[1]

    if new_index == 0:
        goal_row, goal_col = state.agent_positions["hare"][0], state.agent_positions["hare"][1]

    elif new_index == 1:
        goal_row, goal_col = state.agent_positions["stag"][0], state.agent_positions["stag"][1]

    else:
        return curr_row, curr_col

    path =  findPath(state, curr_row, curr_col, goal_row, goal_col)
    return path






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
