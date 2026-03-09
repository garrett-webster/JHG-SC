# from Server.SC_Bots.transVecTranslator import translateVecToIndex
from stagHare.transVecTranslatorStagHare import translateVecToIndexStagHare
import numpy as np
from stagHare.utils.a_star import AStar


from stagHare.utils.pathfindingTime import findPathGreedy, findPathTeamAware


def staghunt_to_jhg(state, action_map, old_agent_positions, old_state, hare_captured):
    allocations = []

    for name, action in action_map.items():

        if name == "stag" or name == "hare":
            continue # we don't actually care about these guys

        # [hare_move, hare_take, stag_move, stag_take]
        allocations_list = create_allocations(name) # take just the number off of this thing.

        # separating them and then we will weigh them by relative position for resonance.
        new_hare_allocation = np.array([0 for _ in range(3)])
        new_stag_allocation = np.array([0 for _ in range(3)])

        old_row, old_col = old_agent_positions[name]

        hare_x, hare_y = state.agent_positions["hare"]
        stag_x, stag_y = state.agent_positions["stag"]

        num_steps_hare = state.n_movements(action[0], action[1], hare_x, hare_y)
        num_steps_stag = state.n_movements(action[0], action[1], stag_x, stag_y)


        # reworked some stuff on the backend. Now, we only use greedy and team aware generators to generate paths
        # and then check just those two paths. should simplify generator checking and allow for move spatial potitioning
        # checking in larger projects.

        # need to try both generators.
        # first, hare stuff
        hare_row, hare_col = old_state.agent_positions["hare"][0], old_state.agent_positions["hare"][1]
        path1 = list(findPathGreedy(old_state, old_row, old_col, hare_row, hare_col))


        # then, stag stuff
        stag_row, stag_col = old_state.agent_positions["stag"][0], old_state.agent_positions["stag"][1]
        path2 = list(findPathTeamAware(name, old_state, old_row, old_col, stag_row, stag_col))

        # if name == "H1":
        #     print("Here was our action ", action, " and here was path 1 ", path1, " and here was path 2 ", path2)

        # allocations are in the following order:
        # [hare, stag, hare_move]
        # action likes being a tuple
        if list(action) == path1:
            # we can now run a VERY rudimentary filter based on close they are to specific things.
            if num_steps_hare <= 1: # if they are right next to or close to the hair
                new_hare_allocation = np.add(new_hare_allocation, allocations_list[1])
                # allocations.append(allocations_list[0])
            else: # hare movement allocation
                new_hare_allocation = np.add(new_hare_allocation, allocations_list[0])
                # allocations.append(allocations_list[2])

        # we actually shouldn't do this, as path2 and path3 are likely to be the same. only add this once.
        # pretty sure we should only do this once, because either way stag is declared.
        # action likes being a tuple for some inane reason.
        if list(action) == path2:
            if num_steps_stag <= 1:
                new_stag_allocation = np.add(new_stag_allocation, allocations_list[2])
            else:
                new_stag_allocation = np.add(new_stag_allocation, allocations_list[3])

        # we will refine these based on a distance metric in the future. keep them here for now though.
        # prevent the np.inf from 0 stesp and add 1 to it.
        # stag_weight =  5 / (num_steps_stag + 1)
        # hare_weight = 5 / (num_steps_hare + 1)

        # experiment with this later.
        num_steps_hare += 1
        num_steps_stag += 1

        total_steps = num_steps_hare + num_steps_stag
        stag_weight = (total_steps / num_steps_stag) # num_steps can be 0.
        hare_weight = (total_steps / num_steps_hare) # num steps can be 0

        if stag_weight == np.inf or hare_weight == np.inf:
            print("EYAH")

        ##TODO: finish debugging this later. 
        # print("here is the new_stag_allocation:")


        # print("here is the stag weight ", stag_weight)
        # print("here is the hare weight ", hare_weight)

        new_allocation = (new_stag_allocation * stag_weight) + (new_hare_allocation * hare_weight)
        # print("here be the new allocaction ", new_allocation)



        # this is to check if we didn't move, make sure that we were locked in place
        # and then create a new allocation for the non movers.
        if list(new_allocation) == [0 for _ in range(3)]:
            # print("yeah we have no idea what they did or why they did what they did, sire. Printing...")
            # means that we haven't really moved in a way that makes sense,
            # so we are going to try and just give ourselves the in between allocation bc I don't know
            # how to handle this edge case.
            # print("We haven't moved. Rerouting...")
            keys = list(action_map.keys())
            actionable_moves = []
            for key in keys:
                if key == "stag" or key == "hare":
                    keys.remove(key)
                else:
                    actionable_moves.append(action_map[key])

            # so if we haven't moved, lets see if that move was cau
            if action in actionable_moves: # we basically just want to check if we stayed in place.
                id = int(name[-1])
                                        # stored as a tuple, not a list.
                if action_map[name] == list(old_agent_positions[name]): # if our action doesn't take us anywhere new, create complex combination.
                    # create 2, 2, 8 or whatever from our thingy
                    # best to use this instead of the 0, 0, 4 becuase of normalization purposes. more distinct vector direction.
                    new_allocation = [2 for _ in range(3)]
                    new_allocation[id] = 8


            if list(new_allocation) == [0,0,0]: # if that DIDN"t work

                # print("we did NOT stay in place, so now we have different issues ")
                new_allocation = interpret_uncertain_move_to_allocation(state, action_map, old_agent_positions, old_state, action,
                                                                        state.agent_positions["hare"], state.agent_positions["stag"], name,
                                                                        allocations_list)


        # literally no clue whats happenign here.
        if list(new_allocation) == [10 for _ in range(3)]:
            print("Somethign is wrong stack trace this fetcher")



        # make sure that the split moves make sense and it really does have no idea where they are going.
        # unfortunately the difference between hare move and hare take still isn't as well defined as I would like
        # so thats prolly next on the docket
        # the real problem is I just want to keep working on my website.

        if list(new_allocation) not in [l.tolist() for l in allocations_list]:
            pass # yeah there was a lot of debugging going on here. we shall see.
            # print("\n WOMBO COMBO! HAPPY FEET!")
            # print("this is the new allocation: ", new_allocation)
            # print("round num ", (old_state.round_num + 1))
            # print("here is the name and action ", name, " ", action, " and here was the movement: from ", old_agent_positions[name][0], old_agent_positions[name][1],
            #       " to ", action_map[name][0], " ", action_map[name][1])
            # print("here was the final allocation: ", new_allocation)
            # print("did that make sense?")

        allocations.append(new_allocation)

    allocations = np.array(allocations)
    row_sums = allocations.sum(axis=1, keepdims=True)
    normalized = allocations / row_sums
    allocations = list(normalized)
    # print("Here are the allocations they are returning ", allocations)
    return allocations


def interpret_uncertain_move_to_allocation(state, action_map, old_agent_positions, old_state,
                                           action, hare_position, stag_position, name, allocations_list):
    hare_x, hare_y = hare_position
    stag_x, stag_y = stag_position

    num_steps_hare_new = state.n_movements(action[0], action[1], hare_x, hare_y)
    num_steps_stag_new = state.n_movements(action[0], action[1], stag_x, stag_y)

    old_action = old_agent_positions[name] # moving here WAS the old action.

    num_steps_hare_old = state.n_movements(old_action[0], old_action[1], hare_x, hare_y)
    num_steps_stag_old = state.n_movements(old_action[0], old_action[1], stag_x, stag_y)

    new_hare_allocation = np.array([0 for _ in range(3)])
    new_stag_allocation = np.array([0 for _ in range(3)])

    # check comparative stag steps and whatnot here.
    if num_steps_stag_new < num_steps_stag_old: # they have moved closer
        if num_steps_stag_new <= 1:
            new_stag_allocation = np.add(new_stag_allocation, allocations_list[3])
        else:
            new_stag_allocation = np.add(new_stag_allocation, allocations_list[2])

    if num_steps_hare_new < num_steps_hare_old:
        if num_steps_hare_new <= 1:  # if they are right next to or close to the hair
            new_hare_allocation = np.add(new_hare_allocation, allocations_list[1])
            # allocations.append(allocations_list[0])
        else:  # hare movement allocation
            new_hare_allocation = np.add(new_hare_allocation, allocations_list[0])
            # allocations.append(allocations_list[2])

    new_allocation = (new_stag_allocation * (num_steps_stag_new + 1)) + (new_hare_allocation * (num_steps_hare_new + 1))
    # print("UNCERTAIN ALLOCATION IN BOUND ", new_allocation)
    if list(new_allocation) == [0 for _ in range(3)]:
        # print("THAT WAS A RANDOM MOVE. RANDOM ALLOCATION?")
        new_allocation = create_random_allocation(3, int(name[-1]))

    return new_allocation




def create_random_allocation(numPlayers, player_idx):
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




    # so at a high level, we take in the movements, and return allocations based on those movement.
    # my written down pesudocode says
    # take in previous states (pre move execution)
    # compare those to our other moves
    # take every generator, and ask, "what is the probablity the generator would have generated this move?"
    # it should be pretty much one or the other,
    # but if not use a convex combination of the probabilities and then normalize it

    # so convert previous moves and moves to generatros
    # convert generator to alloctaions
    # return allocations and then update the engine based on those allocations.
    # bars.


# def create_allocations(name):
#     id = int(name[-1])
#     hare_move = np.zeros(3)
#     hare_move.fill(-2)
#     hare_move[id] = 2
#
#     # way less altruistic version we got going on here.
#     hare = np.zeros(3)
#     hare.fill(0)
#     hare[id] = 6
#
#
#     stag = np.zeros(3)
#     stag.fill(2)
#
#     stag_move = np.zeros(1)
#     stag_move[id] = 3
#
#
#     return [hare, stag, hare_move]

def create_allocations(name):
    id = int(name[-1])
    id -= 1

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


    return [hare_move, hare_take, stag_move, stag_take]