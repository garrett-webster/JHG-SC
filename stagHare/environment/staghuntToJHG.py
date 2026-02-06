# from Server.SC_Bots.transVecTranslator import translateVecToIndex
from stagHare.transVecTranslatorStagHare import translateVecToIndexStagHare
import numpy as np
from stagHare.utils.a_star import AStar


from stagHare.utils.pathfindingTime import findPathGreedy, findPathTeamAware


def staghunt_to_jhg(action_map, old_agent_positions, old_state, hare_captured):
    allocations = []

    for name, action in action_map.items():

        if name == "stag" or name == "hare":
            continue # we don't actually care about these guys

        # the ID will brick here if not continued correctly.
        allocations_list = create_allocations(name) # take just the number off of this thing.

        new_allocation = [0 for _ in range(3)]  # make a vector of zero's trust.


        old_row, old_col = old_agent_positions[name]

        # need to try both generatros
        # first, hare stuff
        hare_row, hare_col = old_state.agent_positions["hare"][0], old_state.agent_positions["hare"][1]
        path1 = list(findPathGreedy(old_state, old_row, old_col, hare_row, hare_col))



        # then, both forms of stag
        stag_row, stag_col = old_state.agent_positions["stag"][0], old_state.agent_positions["stag"][1]
        path2 = list(findPathGreedy(old_state, old_row, old_col, stag_row, stag_col))
        # then stagTeamAware
        path3 = list(findPathTeamAware(name, old_state, old_row, old_col, stag_row, stag_col))

        # we do also have to check if
        # you know
        # the hare has been gobbled
        # becuase that is a DIFFERENT allocation.

        # so this is goign to be weird
        # but we have a vector of 0's , and every time a path matches up, we are just going to ADD it ot the new allocation.
        # by doing that, we don't need to manually check if the paths line up at all, it will proceed through them.
        # just make sure to normalize it at the end or whatever.


        # allocations are in the following order:
        # [hare, stag, hare_move]
        if action == path1:
            if hare_captured: # hare bad allocation
                new_allocation = np.add(new_allocation, allocations_list[0])
                # allocations.append(allocations_list[0])
            else: # hare movement allocation
                new_allocation = np.add(new_allocation, allocations_list[2])
                # allocations.append(allocations_list[2])

        # we actually shouldn't do this, as path2 and path3 are likely to be the same. only add this once.
        if action == path2: # stag from the team aware
            new_allocation = np.add(new_allocation, allocations_list[1])
            # allocations.append(allocations_list[1])
        # pretty sure we should only do this once, because either way stag is declared.
        elif action == path3: # stag from greedy # this could serve as another allocation, like double-dipping as opposed to whatever else.
            new_allocation = np.add(new_allocation, allocations_list[1])
            # allocations.append([allocations_list[1]])

        if list(new_allocation) == [0 for _ in range(3)]:
            print("SOMETHING WENT TERRIBLY WRONG HERE SIRE")

        # make sure that the split moves make sense and it really does have no idea where they are going.
        # unfortunately the difference between hare move and hare take still isn't as well defined as I would like
        # so thats prolly next on the docket
        # the real problem is I just want to keep working on my website.

        if list(new_allocation) not in [l.tolist() for l in allocations_list]:
            print("\n WOMBO COMBO! HAPPY FEET!")
            print("round num ", (old_state.round_num + 1))
            print("here is the name and action ", name, " ", action, " and here was the movement: from ", old_agent_positions[name][0], old_agent_positions[name][1],
                  " to ", action_map[name][0], " ", action_map[name][1])
            print("here was the final allocation: ", new_allocation)
            print("did that make sense?")

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


def create_allocations(name):
    id = int(name[-1])
    hare_move = np.zeros(3)
    hare_move.fill(-2)
    hare_move[id] = 2

    # way less altruistic version we got going on here.
    hare = np.zeros(3)
    hare.fill(0)
    hare[id] = 6


    stag = np.zeros(3)
    stag.fill(2)

    return [hare, stag, hare_move]