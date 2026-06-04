# from Server.SC_Bots.transVecTranslator import translateVecToIndex
from stagHare.transVecTranslatorStagHare import translateVecToIndexStagHare
import numpy as np
from stagHare.utils.a_star import AStar
from stagHare.utils.create_options_matrix import create_options_matrix

from stagHare.utils.pathfindingTime import findPathGreedy, findPathTeamAware

# this function
# takes in the state, the action map, the old agent
def get_allocations_from_movements(state, action_map, old_agent_positions, old_state, influence):
    current_intents = [[] for _ in range(3)] # we will make this dynamic later.
    intents_dict = {}
    for name, action in action_map.items():
        if name == "stag" or name == "hare":
            continue # action is irrelevant; not part of the JHG paradigm.

        id = int(name[-1]) # rip the number of the back.

        new_intent = moves_to_intents(state, old_agent_positions, old_state, action, name)
        current_intents[id] = new_intent # this should add it to the list without the need for a dict.
        intents_dict[name] = new_intent

    allocations_dict = translate_intents_to_movements(current_intents, intents_dict, influence) # for player count and names.

    return allocations_dict

def translate_intents_to_movements(current_intents, intents_dict, influence):
    # hear me out
    # what if we don't go by players, but instead arrange it as necessary
    # that could be a lot cooler actually, and it would make more sense.
    # so just grab the actual matrix, and then break it down from there.

    current_possible_lists = {}

    if current_intents.all(2):
        pass # all stags
        # this pattern has the fastest possible growth, there is a test for it under offlineSimStuffTests.
        current_possible_lists = {
            2: {
                2: 2
            }
        }

    if current_intents.all(1):
        current_possible_lists = {
            1: {

            }
        }

    # if current_intents.all(0):
    #     current_possible_lists = {
    #         0: [0, 0, 0] # literally have no clue what to do here, I'm praying it never happens otherwise I will flip
    #     }


    # SINGLE DEFECTOR
    if sum(current_intents) == 5: # defectors are last; cooperators first.
        matrix_dict = {
            1: [2, -2, -2],
            2: [2, 2, 2],
        }

    if sum(current_intents) == 4 and 0 not in current_intents:
        pass # 1 stag, 2 (known) defectors
        matrix_dict = {
            2: [2, 2, 2],
            1: [3, 0, -3], # how do I explain this bc this LOSES its symmetry.
            # need to tell it that the 0 goes to the other defector, and the
        }

    # if sum(current_intents) == 4 and 0 in current_intents:
    #     pass # 2 stag, 1 ambigous (find the zero)

    if sum(current_intents) == 3 and current_intents.all(1):
        pass # all hare, known

    if sum(current_intents) == 3:
        pass # 1 stag, 1 hare, 1 ambg.

    if sum(current_intents) == 2 and 2 in current_intents:
        pass # 1 stag, 2 ambigous

    if sum(current_intents) == 2 and 1 in current_intents:
        pass # 2 hare, 1 ambg

    if sum(current_intents) == 1:
        pass # 1 hare, 2 ambg.

    if current_intents.all(0):
        pass # if we get here I think we just have to kill ourselves.

    # here we need to do the ordering
    for player in intents_dict:
        pass # find the id, and the other guys and rearrange as necessary.l


def moves_to_intents(state, old_agent_positions, old_state,
                                           action, name):

    # for step performance, look exclusively at their old positions. THis should help get rid of jitters. kind of.
    old_hare_x, old_hare_y = old_state.agent_positions["hare"][0], old_state.agent_positions["hare"][1]
    old_stag_x, old_stag_y = old_state.agent_positions["stag"][0], old_state.agent_positions["stag"][1]


    # if a step value is 0, it screws with the math. add a 1 to make sure its always positive.
    num_steps_hare_new = state.n_movements(action[0], action[1], old_hare_x, old_hare_y) + 1
    num_steps_stag_new = state.n_movements(action[0], action[1], old_stag_x, old_stag_y) + 1

    old_action = old_agent_positions[name] # moving here WAS the old action. # this is a copy object too

    # eaiser to let the state handle wrap arounds and whatnot.
    num_steps_hare_old = state.n_movements(old_action[0], old_action[1], old_hare_x, old_hare_y) + 1
    num_steps_stag_old = state.n_movements(old_action[0], old_action[1], old_stag_x, old_stag_y) + 1

    # for the 3x3 grid that determines the correct weighting function.
    stag_move_neg = (num_steps_stag_new - num_steps_stag_old > 0) # make sure strict greater.
    stag_move_pos = (num_steps_stag_new - num_steps_stag_old < 0)

    hare_moves_pos = (num_steps_hare_new - num_steps_hare_old < 0)
    hare_moves_neg = (num_steps_hare_new - num_steps_hare_old > 0)

    hare_moves_zero = (num_steps_hare_new - num_steps_hare_old == 0)
    stag_moves_zero = (num_steps_stag_new - num_steps_stag_old == 0)

    new_move = -1 # unrealistic fall back just in case.

    # covers pos edge case
    if stag_move_pos and hare_moves_pos and True:
        return 0
    # covers neg edge case
    if stag_move_neg and hare_moves_neg and True:
        return 0
    # covers no movement edge case
    if hare_moves_zero and stag_moves_zero and True:
        return 0

    # if we haven't hit any of the edge cases, move into certain cases
    if stag_move_pos: # we are moving towards the thing
        return 2

    if hare_moves_pos: # moving towards the hares.
        return 1

    return new_move # just to make sure SOMMETHING gets returned.


