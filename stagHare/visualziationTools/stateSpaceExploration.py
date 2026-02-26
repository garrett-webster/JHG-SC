import numpy as np
import copy

# normally this would fit into a larger portion of things
# but it doesn't so we can jump certian hurdles.
def generate_random(numPlayers, player_idx):
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
    temp_var = transaction_vector[player_idx]
    transaction_vector[player_idx] = transaction_vector[0]
    transaction_vector[0] = temp_var

    if transaction_vector[player_idx] < 0:
        transaction_vector[player_idx] = transaction_vector[player_idx] * -1

        # print("here is the transaction_vector: \n", transaction_vector)
    # print("Here is the sum of the transaction_vector: \n", np.sum(transaction_vector))
    return transaction_vector

# copied very closely from jhgToStaghunt
def allocation_to_movement(new_allocation, id):
    pass
    # hare = [-2, -2, 2] # just for simplicity sake. # This is just as easy as it gets.
    # stag = [2, 2, 2]

    # this SHOULD be better.
    # this was the old version want
    hare_move = np.zeros(3)
    hare_move.fill(-2)
    hare_move[id] = 2

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
    new_current_options_matrix = [hare, stag, hare_move]
    # return this so we have a means with which we can specify the bots current eating desire.
    new_index = translateVecToIndexStagHare(new_allocation, new_current_options_matrix, False)

    type = "Stag"
    if new_index == 0:
        type = "Hare"
    # print("Here is teh agent ", id, " and here is the movement type ", type)

    # print('this is the new movement ', new_movement)
    return new_index # pull out the raw index we will do stuff with him.


def translateVecToIndexStagHare(transVec, currentOptionsMatrix, enforce_majority):
    total_distances = []

    # Add abstention as a new row (all zeros)
    new_options_matrix = copy.deepcopy(currentOptionsMatrix)
    new_options_matrix = [[0, 0, 0]] + new_options_matrix  # Add abstention as first option

    transposed_matrix = list(zip(*new_options_matrix))  # Now each item is a column
    transVec = np.array(transVec)

    for column in new_options_matrix:
        distance = np.linalg.norm(transVec - np.array(column))
        total_distances.append(distance)

    index_to_return = total_distances.index(min(total_distances))
    return index_to_return - 1  # Adjust for abstention being at inde


if __name__ == '__main__':
    pass
    # ok so what is the most appopriate way to do this
    # generate a vector, track if its a stag vector or a hare vector
    # add it to a counts thing
    # do this like 10,000 times
    # not having to store the arrays in memory will save time / space

    # making IID assumption so we can just keep tallies instead of lists.
    new_intents = [0, 0]


    num_vectors = 100000
    for i in range(num_vectors):
        # doing thi sspecifically for stag hare will always result in the same vars here.
        new_vector = generate_random(3, 0)
        new_intent = allocation_to_movement(new_vector, 0)
        new_intents[new_intent] += 1

    print("here are hte final results ", new_intents)




