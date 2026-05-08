# from Server.SC_Bots.transVecTranslator import translateVecToIndex
from operator import itemgetter

from Server.Engine.completeBots.humanagent import HumanAgent
from stagHare.agents.cabAgentThing import CabAgent
from stagHare.agents.fetcherBot import FetcherBot
from stagHare.agents.human import humanAgent
from stagHare.agents.hareAgent import HareAgent
from stagHare.agents.stagAgent import StagAgent
from stagHare.transVecTranslatorStagHare import translateVecToIndexStagHare
import numpy as np
from stagHare.utils.a_star import AStar
import random

from stagHare.utils.create_options_matrix import create_options_matrix
from stagHare.utils.pathfindingTime import findPathGreedy, findPathTeamAware # maybe





# so at a high level
# what I need is


# TODO: separate this into get allocations and get hare hunting map -- two functions. a function pointer might be necesary.




# TODO: separate this into get moves and hunting hare mmaps
def get_movements_from_allocations(new_allocations, hunting_hare_map, state):
    # lets get some dictionaries set up to put stuff in
    new_moves = {}
    keys = new_allocations.keys()
    for key in keys:
        id = int(key[-1])  # might be a desync here?
        new_row, new_col, movement_type = allocation_to_movement(new_allocations[key], id, state)
        new_move = [new_row, new_col]
        new_moves[key] = new_move  # bars??

    new_allocations = dict(sorted(new_allocations.items(), key=lambda item: item[0]))

    print("Here are the allocatinos \n ", new_allocations)
    return new_moves


def create_map_from_intents(intents, hunting_hare_map):
    for name, intent in intents.items():
        if intent == 0 or intent == 1: # hare move, hare take
            hunting_hare_map[name] = True
        else:
            hunting_hare_map[name] = False # stag move, stag take.
    return hunting_hare_map






        # htis is sort of a p --> np problem, as this direction is pretty easy.

    # then we return a move from the generators, taking the most likely one
    # then we return the move.




# old allcation to movement. needs work. tank needs fuel.
# this returns just the intent -- used primarily for debugging.
def allocation_to_intent(new_allocation, id, num_players):

    normalized = create_options_matrix(id)

    new_allocation = [element / np.sum(np.abs(new_allocation)) for element in new_allocation]
    # return this so we have a means with which we can specify the bots current eating desire.

    # so maybe normalizing this will help us out.
    new_index = translateVecToIndexStagHare(new_allocation, normalized, id)


    if new_index == 0 or new_index == 1:
        return 1 # hare
    elif new_index == 2 or new_index == 3:
        return 0 # stag
    else:
        return None



def allocation_to_movement(new_allocation, id, state):
    new_current_options_matrix = create_options_matrix(id)
    # make sure to use the ABS when you are summing! otherwise negative breaks everything!
    new_allocation = [element / np.sum(np.abs(new_allocation)) for element in new_allocation]
    normalized_current_options_matrix = [row / np.sum(np.abs(row)) for row in new_current_options_matrix]
    # then translate that new allocation into the closest possible option and return that movement.
    new_index = translateVecToIndexStagHare(new_allocation, normalized_current_options_matrix, id)
    new_movement = generate_movement(state, id, new_index)

    if new_index == 0 or new_index == 1:
        type = "hare"
    elif new_index == 2 or new_index == 3:
        type = "stag"

    # print('this is the new movement ', new_movement)
    #  print(f"Agent {id}, alloc={new_allocation}, index={new_index}")

    return new_movement[0], new_movement[1], new_index # pull out the raw index we will do stuff with him.

def generate_movement(state, id, new_index):
    player_name = "R" + str(id) # zero index, then 2 agetns in front of them.
    player_position = state.agent_positions[player_name]
    curr_row, curr_col = player_position[0], player_position[1]

    if new_index == 0: # hare move
        goal_row, goal_col = state.agent_positions["hare"][0], state.agent_positions["hare"][1]
        path = findPathGreedy(state, curr_row, curr_col, goal_row, goal_col)

    elif new_index == 1:# hare take
        goal_row, goal_col = state.agent_positions["hare"][0], state.agent_positions["hare"][1]
        path = findPathGreedy(state, curr_row, curr_col, goal_row, goal_col)

    elif new_index == 2: # stag move
        goal_row, goal_col = state.agent_positions["stag"][0], state.agent_positions["stag"][1]
        path = findPathTeamAware(player_name, state, curr_row, curr_col, goal_row, goal_col)

    elif new_index == 3:
        goal_row, goal_col = state.agent_positions["stag"][0], state.agent_positions["stag"][1]
        path = findPathTeamAware(player_name, state, curr_row, curr_col, goal_row, goal_col)


    else:
        return curr_row, curr_col


    return path



def print_hare_hunting_map(hunting_hare_map):
    new_hunting_map = []
    for key in hunting_hare_map:
        if key == "stag" or key == "hare":
            continue
        new_hunting_map.append([key, hunting_hare_map[key]])
    new_hunting_map.sort(key=itemgetter(0))
    # print("This is the new hunting hare map ", new_hunting_map)
