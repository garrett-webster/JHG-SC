# from Server.SC_Bots.transVecTranslator import translateVecToIndex
from stagHare.transVecTranslatorStagHare import translateVecToIndexStagHare
import numpy as np
from stagHare.utils.a_star import AStar


from stagHare.utils.pathfindingTime import findPathGreedy, findPathTeamAware


def staghunt_to_jhg(state, action_map, old_agent_positions, old_state, hare_captured):
    allocations = []
    allocations_dict = {}

    for name, action in action_map.items():

        if name == "stag" or name == "hare":
            continue # we don't actually care about these guys

        # [hare_move, hare_take, stag_move, stag_take]
        allocations_list = create_allocations(name) # take just the number off of this thing.


        new_allocation = interpret_uncertain_move_to_allocation(state, action_map, old_agent_positions, old_state, action,
                                                                        state.agent_positions["hare"], state.agent_positions["stag"], name,
                                                                        allocations_list)

        # if name == "H1":
        #     print("this was the human allocation ", new_allocation)
        new_allocation = new_allocation / sum(new_allocation)
        allocations.append(new_allocation)
        allocations_dict[name] = new_allocation

    allocations = np.array(allocations)
    row_sums = allocations.sum(axis=1, keepdims=True)
    normalized = allocations / row_sums
    allocations = list(normalized)
    allocations_dict = dict(sorted(allocations_dict.items()))
    # print("Here are the allocations they are returning ", allocations_dict)
    # print("            ")
    return allocations


def interpret_uncertain_move_to_allocation(state, action_map, old_agent_positions, old_state,
                                           action, hare_position, stag_position, name, allocations_list):

    # GAME OVER CHECK, EASY CHECKS.
    if state.hare_captured() or state.stag_captured():
        if state.hare_captured():
            new_allocation = allocations_list[1]
        else:
            new_allocation = allocations_list[3]
        return new_allocation

    # less easy checks, game is still running.


    # grab the current number of steps
    hare_x, hare_y = hare_position
    stag_x, stag_y = stag_position

    # if a step value is 0, it screws with the math. add a 1 to make sure its always positive.
    num_steps_hare_new = state.n_movements(action[0], action[1], hare_x, hare_y) + 1
    num_steps_stag_new = state.n_movements(action[0], action[1], stag_x, stag_y) + 1

    old_action = old_agent_positions[name] # moving here WAS the old action.

    # grab the old number of steps (in reference to the OLD positions)
    old_hare_x, old_hare_y = old_state.agent_positions["hare"][0], old_state.agent_positions["hare"][1]
    old_stag_x, old_stag_y = old_state.agent_positions["stag"][0], old_state.agent_positions["stag"][1]

    num_steps_hare_old = state.n_movements(old_action[0], old_action[1], old_hare_x, old_hare_y) + 1
    num_steps_stag_old = state.n_movements(old_action[0], old_action[1], old_stag_x, old_stag_y) + 1


    # now calculate weights
    total_steps = num_steps_stag_new + 1 + num_steps_hare_new + 1
    # YES THESE NEED TO BE FLIPPED! If stag steps are low, then stag weight is high. simple as.
    stag_weight =  (num_steps_hare_new + 1) / total_steps
    hare_weight = (num_steps_stag_new + 1) / total_steps

    # for the 3x3 grid that determines the correct weighting function.
    stag_move_neg = (num_steps_stag_new - num_steps_stag_old > 0) # make sure strict greater.
    stag_move_pos = (num_steps_stag_new - num_steps_stag_old < 0)

    hare_moves_pos = (num_steps_hare_new - num_steps_hare_old < 0)
    hare_moves_neg = (num_steps_hare_new - num_steps_hare_old > 0)

    hare_moves_zero = (num_steps_hare_new - num_steps_hare_old == 0)
    stag_moves_zero = (num_steps_stag_new - num_steps_stag_old == 0)

    # column 1
    if stag_move_pos and hare_moves_pos:
        new_allocation = weight(stag_weight, hare_weight, allocations_list)
    elif stag_move_pos and hare_moves_zero:
        new_allocation = allocations_list[2]
    elif stag_move_pos and hare_moves_neg:
        new_allocation = allocations_list[2]

    # column 2
    elif stag_moves_zero and hare_moves_pos:
        new_allocation = allocations_list[0]
    elif stag_moves_zero and hare_moves_zero:
        new_allocation = weight(stag_weight, hare_weight, allocations_list)
    elif stag_moves_zero and hare_moves_neg:
        new_allocation = allocations_list[2]

    # column 3
    elif stag_move_neg and hare_moves_pos:
        new_allocation = allocations_list[0]
    elif stag_move_neg and hare_moves_zero:
        new_allocation = allocations_list[0]
    elif stag_move_neg and hare_moves_neg:
        new_allocation = weight(stag_weight, hare_weight, allocations_list)

    else:
        print("SOMETHING SI VERTY VEYR WORNG SIRE")
        new_allocation = [9, 0, 0]

    weighted_allocation = weight(stag_weight, hare_weight, allocations_list) * abs((stag_weight - hare_weight) * 2) # make it a number
                                                                            # in the middle? very low number
                                                                            # right next to them? very high.
    # print("New allocation: ", new_allocation)
    # print("Weight allocation ", weighted_allocation)
    return_allocation = new_allocation + weighted_allocation

    return return_allocation


def weight(stag_weight, hare_weight, allocations_list): # new allocation that sits right in the middle of the fetcher.
    # print("Doing a weighted allocation")
    # print("Here is the hare wieght ", hare_weight, " and here is the stag weight ", stag_weight)
    new_array = (stag_weight * allocations_list[2]) + (hare_weight * allocations_list[0])
    return new_array

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