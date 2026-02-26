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


        # allocations are in the following order:
        # [hare, stag, hare_move]
        if action == path1:
            # we can now run a VERY rudimentary filter based on close they are to specific things.
            if num_steps_hare <= 1: # if they are right next to or close to the hair
                new_hare_allocation = np.add(new_hare_allocation, allocations_list[1])
                # allocations.append(allocations_list[0])
            else: # hare movement allocation
                new_hare_allocation = np.add(new_hare_allocation, allocations_list[0])
                # allocations.append(allocations_list[2])

        # we actually shouldn't do this, as path2 and path3 are likely to be the same. only add this once.
        # pretty sure we should only do this once, because either way stag is declared.
        if action == path2:
            if num_steps_stag <= 1:
                new_stag_allocation = np.add(new_stag_allocation, allocations_list[3])
            else:
                new_stag_allocation = np.add(new_stag_allocation, allocations_list[2])

        # we will refine these based on a distance metric in the future. keep them here for now though.
        # prevent the np.inf from 0 stesp and add 1 to it.
        stag_weight = 5 / (num_steps_stag + 1)
        hare_weight = 5 / (num_steps_hare + 1)

        if stag_weight == np.inf or hare_weight == np.inf:
            print("EYAH")

        ##TODO: finish debugging this later. 
        # print("here is the new_stag_allocation:")


        # print("here is the stag weight ", stag_weight)
        # print("here is the hare weight ", hare_weight)

        new_allocation = (new_stag_allocation * stag_weight) + (new_hare_allocation * hare_weight)
        # print("here be the new allocaction ", new_allocation)



        # means we didn't move, so this is where stuff gets tricky.
        if list(new_allocation) == [0 for _ in range(3)]:
            print("yeah we have no idea what they did or why they did what they did, sire. Printing...")
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

    return allocations











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

    #
    hare_take = np.zeros(3)
    hare_take[id] = 6

    hare_move = np.zeros(3)
    hare_move.fill(-2)
    hare_move[id] = 2

    stag_take = np.zeros(3)
    stag_take.fill(2)

    stag_move = np.zeros(3)
    stag_move.fill(1.5)
    stag_move[id] = 3


    return [hare_move, hare_take, stag_move, stag_take]