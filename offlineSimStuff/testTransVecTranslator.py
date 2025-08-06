from Server.SC_Bots.transVecTranslator import translateVecToIndex



if __name__ == "__main__":
    transVec = [ 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0]
    old_vote = -1
    current_options_matrix = [[2.0, -10.0, 2.0], [2.0, -10.0, 2.0], [2.0, -10.0, 2.0], [3.0, -10.0, 0.0], [0.0, -10.0, 10.0], [0.0, -10.0, 6.0], [3.0, -10.0, 0.0], [10.0, -10.0, 0.0], [0.0, 10.0, 0.0], [0.0, 10.0, 0.0], [0.0, 10.0, 0.0]]
    enforce_majority = False
    new_vote = translateVecToIndex(transVec, current_options_matrix, enforce_majority)
    print("This is the new vote ", new_vote)
