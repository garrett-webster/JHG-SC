# updated translator for our OTHER THING. No clue if this will affect the JHG functionality.
import numpy as np
import copy

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