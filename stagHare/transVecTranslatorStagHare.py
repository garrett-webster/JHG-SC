# updated translator for our OTHER THING. No clue if this will affect the JHG functionality.
import numpy as np
import copy

from stagHare.utils.create_options_matrix import create_options_matrix


# def translateVecToIndexStagHare(transVec, currentOptionsMatrix, enforce_majority):
#     total_distances = []
#
#     # NORMALIZE EVERYTHING PLEASE.
#     currentOptionsMatrix = [row / sum(row) for row in currentOptionsMatrix]
#     total = sum(abs(transVec)) # we can have negative and positive allocations. should be scaling by abs, not by the whole thing.
#     # transVec = [num / sum(transVec) for num in transVec]
#     # total = sum(abs(transVec)) # we can have negative and positive allocations. should be scaling by abs, not by the whole thing.
#     # make sure to keep track of him when possible.
#     transVec = [num / total for num in transVec]
#
#     # Add abstention as a new row (all zeros)
#     new_options_matrix = copy.deepcopy(currentOptionsMatrix)
#     new_options_matrix = [[0, 0, 0]] + new_options_matrix  # Add abstention as first option
#
#     transposed_matrix = list(zip(*new_options_matrix))  # Now each item is a column
#     transVec = np.array(transVec)
#
#     for column in new_options_matrix:
#         distance = np.linalg.norm(transVec - np.array(column))
#         total_distances.append(distance)
#
#     index_to_return = total_distances.index(min(total_distances))
#     #  print("this be the index we are returning ", index_to_return)
#     return index_to_return - 1 # account for abstention as an option.

# ID doesn't ever actually get used, but I want it here for debugging purposes.
# assume that transVec and currentOptionsMatrix are already normalized.
def translateVecToIndexStagHare(transVec, id):
    transVec = np.array(transVec.copy())
    normalizedTransVec = [element / sum(abs(transVec)) for element in transVec]

    # in case you want to make this as unreadable as possible, here you have it.
    non_personal_allocations = np.delete(normalizedTransVec, id)
    dist = np.sqrt(np.sum(np.square(non_personal_allocations)))

    all_non_negative = np.all([x >= 0 for x in normalizedTransVec])

    if all_non_negative:
        if dist >= 0.55:
            index_to_return = 3
        elif dist >= 0.25:
            index_to_return = 2
        else:
            index_to_return = 0
    else:
        if dist < 0.25:
            index_to_return = 0
        else:
            index_to_return = 1


    return index_to_return




def noisifyJHGVectorsWithStagHareNoise(transVec, id):
    transVec = np.array(transVec.copy())
    normalizedTransVec = [element / sum(abs(transVec)) for element in transVec]

    # in case you want to make this as unreadable as possible, here you have it.
    non_personal_allocations = np.delete(normalizedTransVec, id)
    dist = np.sqrt(np.sum(np.square(non_personal_allocations)))

    all_non_negative = np.all([x >= 0 for x in normalizedTransVec])


    options = create_options_matrix(id)

    if all_non_negative:
        if dist >= 0.55:
            allocation_to_return = options[3]
        elif dist >= 0.25:
            allocation_to_return = options[2]
        else:
            allocation_to_return = options[0]
    else:
        if dist < 0.25:
            allocation_to_return = options[0]
        else:
            allocation_to_return = options[1]


    return allocation_to_return