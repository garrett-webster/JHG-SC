from Server.SC_Bots.transVecTranslator import translateVecToIndex
import numpy as np


if __name__ == "__main__":

    transVec = [ 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0]
    current_options_matrix = [
        [2.0, -10.0, 2.0],
        [2.0, -10.0, 2.0],
        [2.0, -10.0, 2.0],
        [3.0, -10.0, 0.0],
        [0.0, -10.0, 10.0],
        [0.0, -10.0, 6.0],
        [3.0, -10.0, 0.0],
        [10.0, -10.0, 0.0],
        [0.0, 10.0, 0.0],
        [0.0, 10.0, 0.0],
        [0.0, 10.0, 0.0]
    ]


    old_vote = -1 # this is the anticipated outcome


    enforce_majority = False
    new_vote = translateVecToIndex(transVec, current_options_matrix, enforce_majority)
    assert new_vote == old_vote

    transVec = [2.0, 2.0, 2.0, 3.0, 0.0, 0.0, 3.0, 10.0, 0.0, 0.0, 0.0]
    current_options_matrix = [
        [2.0, -10.0, 2.0],
        [2.0, -10.0, 2.0],
        [2.0, -10.0, 2.0],
        [3.0, -10.0, 0.0],
        [0.0, -10.0, 10.0],
        [0.0, -10.0, 6.0],
        [3.0, -10.0, 0.0],
        [10.0, -10.0, 0.0],
        [0.0, 10.0, 0.0],
        [0.0, 10.0, 0.0],
        [0.0, 10.0, 0.0]
    ]

    old_vote = 0
    enforce_majority = False
    new_vote = translateVecToIndex(transVec, current_options_matrix, enforce_majority)
    assert new_vote == old_vote


    transVec = [-10.0, -10.0, -10.0, -10.0, -10.0, -10.0, -10.0, -10.0, 10.0, 10.0, 10.0]
    current_options_matrix = [
        [2.0, -10.0, 2.0],
        [2.0, -10.0, 2.0],
        [2.0, -10.0, 2.0],
        [3.0, -10.0, 0.0],
        [0.0, -10.0, 10.0],
        [0.0, -10.0, 6.0],
        [3.0, -10.0, 0.0],
        [10.0, -10.0, 0.0],
        [0.0, 10.0, 0.0],
        [0.0, 10.0, 0.0],
        [0.0, 10.0, 0.0]
    ]

    old_vote = 1
    enforce_majority = False
    new_vote = translateVecToIndex(transVec, current_options_matrix, enforce_majority)
    assert new_vote == old_vote

    transVec = [2.0, 2.0, 2.0, 0.0, 10.0, 6.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    current_options_matrix = [
        [2.0, -10.0, 2.0],
        [2.0, -10.0, 2.0],
        [2.0, -10.0, 2.0],
        [3.0, -10.0, 0.0],
        [0.0, -10.0, 10.0],
        [0.0, -10.0, 6.0],
        [3.0, -10.0, 0.0],
        [10.0, -10.0, 0.0],
        [0.0, 10.0, 0.0],
        [0.0, 10.0, 0.0],
        [0.0, 10.0, 0.0]
    ]

    old_vote = 2
    enforce_majority = False
    new_vote = translateVecToIndex(transVec, current_options_matrix, enforce_majority)
    assert new_vote == old_vote


    transVec = [2.0, 2.0, 2.0, 2.0, 2.0, 1.5, 0.0, 0.0, 0.0, 0.0, 0.0]
    current_options_matrix = [
        [2.0, -10.0, 2.0],
        [2.0, -10.0, 2.0],
        [2.0, -10.0, 2.0],
        [2.0, -10.0, 0.0],
        [2.0, -10.0, 10.0],
        [2.0, -10.0, 6.0],
        [2.0, -10.0, 0.0],
        [2.0, -10.0, 0.0],
        [2.0, 10.0, 0.0],
        [2.0, 10.0, 0.0],
        [2.0, 10.0, 0.0]
    ]

    old_vote = 0
    enforce_majority = False
    new_vote = translateVecToIndex(transVec, current_options_matrix, enforce_majority)
    assert new_vote == old_vote





