import numpy as np

from stagHare.transVecTranslatorStagHare import translateVecToIndexStagHare

new_allocation = [ 1.,  1., -1.]

id = 0
# hare move represents moving towards the hare
hare_move = np.zeros(3)
hare_move.fill(0)
hare_move[id] = 6

# trying to take the hare
hare_take = np.zeros(3)
hare_take.fill(-2)
hare_take[id] = 2

# moving towards stag
stag_move = np.zeros(3)
stag_move.fill(1.5)
stag_move[id] = 3

# taking stag.
stag_take = np.zeros(3)
stag_take.fill(2)

new_current_options_matrix = [hare_move, hare_take, stag_move, stag_take]

normalized = [row / sum(row) for row in new_current_options_matrix]

new_index = translateVecToIndexStagHare(new_allocation, normalized, False)

print("this is the new index we are working with ", new_index)