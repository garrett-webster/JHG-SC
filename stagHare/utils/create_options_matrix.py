import numpy as np

"""
Takes in an id; the int that represents a players location in the transactions matrix. 
Return a matrix that contains all possible mapping options up and down, normalized. 
"""
def create_options_matrix(id):
    # id = int(name[-1])
    # # id -= 1 # what. what. what. what. what.

    hare_move = np.zeros(3)
    hare_move[id] = 6

    hare_take = np.zeros(3)
    hare_take.fill(-2)
    hare_take[id] = 2

    stag_move = np.zeros(3)
    stag_move.fill(1.5)
    stag_move[id] = 3

    stag_take = np.zeros(3)
    stag_take.fill(2)

    current_options_matrix = [hare_move, hare_take, stag_move, stag_take]
    normalized_current_options_matrix = [row / np.sum(np.abs(row)) for row in current_options_matrix]
    return normalized_current_options_matrix