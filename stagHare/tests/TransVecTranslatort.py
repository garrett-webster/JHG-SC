import numpy as np

from stagHare.transVecTranslatorStagHare import translateVecToIndexStagHare
from stagHare.utils.create_options_matrix import create_options_matrix

if __name__ == "__main__":
    # new_allocation = np.array([1.,  1., -1.])
    new_allocation = np.array([0.75, 0.125, 0.125,])
    # go ahead and normalize that fetcher.
    new_allocation = [element / np.sum(np.abs(new_allocation)) for element in new_allocation]
    print("this is the normalized ", new_allocation)

    id = 0
    # hare move represents moving towards the hare
    normalized = create_options_matrix(id)
    new_index = translateVecToIndexStagHare(new_allocation, normalized, False)

    print("this is the new index we are working with ", new_index)