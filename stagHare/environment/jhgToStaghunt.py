# from Server.SC_Bots.transVecTranslator import translateVecToIndex
from Server.Engine.completeBots.humanagent import HumanAgent
from stagHare.agents.cabAgentThing import CabAgent
from stagHare.agents.fetcherBot import FetcherBot
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

    print("this is what new intents looks like ", new_intents)

    # need TO PASS IT IN to account for discrepancies.
    hunting_hare_map = create_map_from_intents(new_intents, hunting_hare_map)
    return new_moves, hunting_hare_map, new_allocations # then just give the moves back.
    # note that these are in a dictionary, I'll have to do weird things to randomize the order that this happens in.

    # I really should preseve the dictionary aspect of this huh
    # that way I cna do things ot keep track and randomize things and keep track of who moved where.

# new_current_options_matrix = [hare, stag, hare_move]
def create_map_from_intents(intents, hunting_hare_map):
    for name, intent in intents.items():
        if intent == 0 or intent == 2:
            hunting_hare_map[name] = True
        else:
            hunting_hare_map[name] = False
    return hunting_hare_map






        # htis is sort of a p --> np problem, as this direction is pretty easy.

    # then we return a move from the generators, taking the most likely one
    # then we return the move.




# old allcation to movement. needs work. tank needs fuel.
def allocation_to_movement(new_allocation, id, state):
    pass
    # hare = [-2, -2, 2] # just for simplicity sake. # This is just as easy as it gets.
    # stag = [2, 2, 2]

    # this SHOULD be better.
    # this was the old version want
    hare_move = np.zeros(3)
    hare_move.fill(-2)
    hare_move[id] = 2

    # way less altruistic version we got going on here.
    hare = np.zeros(3)
    hare.fill(0)
    hare[id] = 6


    stag = np.zeros(3)
    stag.fill(2)

    # print("we are working with id ", id)
    # print("this is the new allocation ", new_allocation)
    # print("this is the corresponding hare thing ", hare)
    # nothing should be created automatically.
    new_current_options_matrix = [hare, stag, hare_move]
    # return this so we have a means with which we can specify the bots current eating desire.
    new_index = translateVecToIndexStagHare(new_allocation, new_current_options_matrix, False)
    new_movement = generate_movement(state, id, new_index)

    type = "Stag"
    if new_index == 0:
        type = "Hare"
    # print("Here is teh agent ", id, " and here is the movement type ", type)

    # print('this is the new movement ', new_movement)
    return new_movement[0], new_movement[1], new_index # pull out the raw index we will do stuff with him.

def generate_movement(state, id, new_index):
    player_name = "R" + str(id) # zero index, then 2 agetns in front of them.
    player_position = state.agent_positions[player_name]
    curr_row, curr_col = player_position[0], player_position[1]

    if new_index == 0:
        goal_row, goal_col = state.agent_positions["hare"][0], state.agent_positions["hare"][1]
        path = findPathGreedy(state, curr_row, curr_col, goal_row, goal_col)

    elif new_index == 1:#  literally 0 clue if this will work the wya that I think it will.
        goal_row, goal_col = state.agent_positions["stag"][0], state.agent_positions["stag"][1]
        path = findPathTeamAware(player_name, state, curr_row, curr_col, goal_row, goal_col)

    elif new_index == 2:
        goal_row, goal_col = state.agent_positions["hare"][0], state.agent_positions["hare"][1]
        path = findPathGreedy(state, curr_row, curr_col, goal_row, goal_col)
        # ADD STATE CHECKING TO SEE IF THEY ACTUALLY ATE THE THING OR NOT
        # actually it doesn't matter, we can just spit out the other thing on the back end.

    else:
        return curr_row, curr_col


    return path