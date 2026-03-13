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

from stagHare.utils.pathfindingTime import findPathGreedy, findPathTeamAware # maybe





# so at a high level
# what I need is

# take in an allocation, and then return a tuple, which is the new movement.
def jhg_to_staghunt(agents, state, reward, round_num):

    # first, lets grab all the allocations and separate the wheat from the chaff
    new_moves = {}
    new_allocations = {}
    new_intents = {}
    indices = list(range(len(agents)))
    random.shuffle(indices) # this should do the trick.
    hunting_hare_map = {}
    for i in indices:
        agent = agents[i]
        if not isinstance(agent, CabAgent) and not isinstance(agent, FetcherBot) and not isinstance(agent, HareAgent) and not isinstance(agent, StagAgent) and not isinstance(agent, HumanAgent):
            new_moves[agent.name] = agent.act(state, reward, round_num) # should be noted that these are just prey moves. they are essentialy random.
            hunting_hare_map[agent.name] = agent.is_hunting_hare()
        else:
            allocation = agent.act(state, reward, round_num)
            new_allocations[agent.name] = allocation

    # allocation to generators (for which we have the translator)
    keys = new_allocations.keys()
    # print("here are hte new allocations ", new_allocations)

    for key in keys:
        id = int(key[-1])
        new_row, new_col, movement_type = allocation_to_movement(new_allocations[key], id, state)
        new_move = [new_row, new_col]
        new_moves[key] = new_move # bars??
        new_intents[key] = movement_type

    new_allocations = dict(sorted(new_allocations.items(), key=lambda item: item[0]))
    # print("The initial allocations are as follows : ", new_allocations)
    # need TO PASS IT IN to account for discrepancies.
    hunting_hare_map = create_map_from_intents(new_intents, hunting_hare_map)
    print_hare_hunting_map(hunting_hare_map)
    return new_moves, hunting_hare_map, new_allocations # then just give the moves back.
    # note that these are in a dictionary, I'll have to do weird things to randomize the order that this happens in.

    # I really should preseve the dictionary aspect of this huh
    # that way I cna do things ot keep track and randomize things and keep track of who moved where.

# new_current_options_matrix = [hare, stag, hare_move]
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
def allocation_to_movement(new_allocation, id, state):
    pass
    # hare = [-2, -2, 2] # just for simplicity sake. # This is just as easy as it gets.
    # stag = [2, 2, 2]
    id -= 1
    # hare move represents moving towards the hare
    hare_move = np.zeros(3)
    hare_move.fill(0)
    hare_move[id] = 6

    # trying to take the hare
    hare_take = np.zeros(3)
    hare_take.fill(-2)
    hare_take[id] = 2


    stag_move = np.zeros(3)
    stag_move.fill(1.5)
    stag_move[id] = 3

    stag_take = np.zeros(3)
    stag_take.fill(2)

    id += 1
    # 1 is hare move, 2 is hare take, 3 is stag move, 4 is stag take
    new_current_options_matrix = [hare_move, hare_take, stag_move, stag_take]
    normalized = [row / sum(row) for row in new_current_options_matrix]
    # return this so we have a means with which we can specify the bots current eating desire.

    # so maybe normalizing this will help us out.
    new_index = translateVecToIndexStagHare(new_allocation, normalized, False)
    new_movement = generate_movement(state, id, new_index)

    if new_index == 0 or new_index == 1:
        type = "hare"
    elif new_index == 2 or new_index == 3:
        type = "stag"


    # print('this is the new movement ', new_movement)
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
