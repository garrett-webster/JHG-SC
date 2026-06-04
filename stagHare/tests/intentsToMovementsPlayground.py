from stagHare.environment.staghuntToJHG import translate_intents_to_movements
# small test suite to make sure that this thing works the way that I want it to.
# now, if this actually will BEHAVE the way that I want it to, that is an ENTIRELY different question.



if __name__ == '__main__':
    # we need to make sure this works the way that I want it to ig.

    # lets set up one for every scenario, just to make sure everything works the way that I want it to.

    current_intents = [1, 2, 2]
    intents_dict = {'R0': 0, 'R1': 2, 'R2': 2}
    influence = [[0 for _ in range(3)] for _ in range(3)] # make a little 3x3 grid that shows all the influences.

    new_allocations_list, new_allocations_dict = translate_intents_to_movements(current_intents, intents_dict, influence)
    # print("here are the new allocations \n", new_allocations_list)

    # we are expecting a single defector w/ the defector in spot 1
    # we are then expecting a thing that looks like:
    expected_array = [
        [2, -2, -2],
        [2, 2, 2],
        [2, 2, 2],
    ]

    current_intents = [1, 1, 2]
    intents_dict = {'R0': 1, 'R1': 1, 'R2': 2}
    influence = [[0 for _ in range(3)] for _ in range(3)]

    new_allocations_list, new_allocations_dict = translate_intents_to_movements(current_intents, intents_dict, influence)

    expected_array = [
        [3, 0, -3],
        [0, 3, -3],
        [2, 2, 2],
    ]

    assert new_allocations_list == expected_array


    current_intents = [1, 2, 1]
    intents_dict = {'R0': 1, 'R1': 1, 'R2': 2}
    influence = [[0 for _ in range(3)] for _ in range(3)]

    new_allocations_list, new_allocations_dict = translate_intents_to_movements(current_intents, intents_dict, influence)

    expected_array = [
        [3, -3, -0],
        [2, 2, 2],
        [0, -3, 3],
    ]

    assert new_allocations_list == expected_array

    current_intents = [2, 2, 2]
    intents_dict = {'R0': 2, 'R1': 2, 'R2': 2}
    influence = [[0 for _ in range(3)] for _ in range(3)]

    new_allocations_list, new_allocations_dict = translate_intents_to_movements(current_intents, intents_dict, influence)

    expected_array = [
        [0, 3, 3],
        [3, 0, 3],
        [3, 3, 0],
    ]

    current_intents = [1, 1, 1]
    intents_dict = {'R0': 1, 'R1': 1, 'R2': 1}
    influence = [[0 for _ in range(3)] for _ in range(3)]

    new_allocations_list, new_allocations_dict = translate_intents_to_movements(current_intents, intents_dict, influence)

    expected_array = [
        [6, 0, 0],
        [0, 6, 0],
        [0, 0, 6],
    ]

    assert new_allocations_list == expected_array
