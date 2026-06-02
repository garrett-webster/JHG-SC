# from Server.SC_Bots.transVecTranslator import translateVecToIndex
from operator import itemgetter

from rfc3987_syntax import is_valid_syntax_isegment_nz

from Server.Engine.completeBots.humanagent import HumanAgent
from stagHare.agents import agent
from stagHare.agents.alegaatr import AlegAATr
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

def create_map_from_intents(intents, hunting_hare_map):
    for name, intent in intents.items():
        if intent == 0 or intent == 1: # hare move, hare take
            hunting_hare_map[name] = True
        else:
            hunting_hare_map[name] = False # stag move, stag take.
    return hunting_hare_map




# old allcation to movement. needs work. tank needs fuel.
# this returns just the intent -- used primarily for debugging.
def allocation_to_intent(new_allocation, id, num_players):



    # the current options matrix and allocaition are noramlized internally.
    new_index = translateVecToIndexStagHare(new_allocation, id)


    if new_index == 0 or new_index == 1:
        return 1 # hare
    elif new_index == 2 or new_index == 3:
        return 0 # stag
    else:
        return None



def allocation_to_movement(new_allocation, id, state):
    new_current_options_matrix = create_options_matrix(id)
    # make sure to use the ABS when you are summing! otherwise negative breaks everything!
    # new_allocation = [element / np.sum(np.abs(new_allocation)) for element in new_allocation]
    # new allocation is normalized within translateVecToIndexStagHare
    # print("This is the new allocation ", new_allocation)
    # print("this is the new id ", id)
    new_index = translateVecToIndexStagHare(new_allocation, id)
    # print("This is the index we are returning ", new_index)
    new_movement = generate_movement(state, id, new_index)

    return new_movement, new_index # pull out the raw index we will do stuff with him.

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
        print("IF THIS FIRES SOMETHING IS TERRIBLY WRONG")
        return curr_row, curr_col


    return list(path) # just go ahead and turn that into a list.



def print_hare_hunting_map(hunting_hare_map):
    new_hunting_map = []
    for key in hunting_hare_map:
        if key == "stag" or key == "hare":
            continue
        new_hunting_map.append([key, hunting_hare_map[key]])
    new_hunting_map.sort(key=itemgetter(0))
    # print("This is the new hunting hare map ", new_hunting_map)


def create_agent_indicies(agents):
    new_agent_indicies = list(range(len(agents)))
    np.random.shuffle(new_agent_indicies)
    return new_agent_indicies


def get_allocations_from_agents(agents, state, round_num, agent_indicies):
    allocation_dict = {}
    for agent_index in agent_indicies:
        agent = agents[agent_index]
        if not (agent.name == 'stag' or agent.name == 'hare' or isinstance(agent, AlegAATr) or isinstance(agent, humanAgent)): # the humans don't GET an allocation sire.
            allocation_dict[agent.name] = agent.act(state, None, round_num)

    return allocation_dict

def get_hunting_hare_map_from_agents(agents, allocation_dict, agent_indicies):
    hunting_hare_map = {}
    for index in agent_indicies:
        agent = agents[index]
        # TODO: please make this a list.
        if agent.name == "stag" or agent.name == "hare" or isinstance(agent, AlegAATr) or isinstance(agent, humanAgent): #  or isinstance(agent, HareAgent) or isinstance(agent, StagAgent):
            hunting_hare_map[agent.name] = agent.is_hunting_hare()

        else:
            id = int(agent.name[-1])
            intent = translateVecToIndexStagHare(allocation_dict[agent.name], id)
            # stag are 2 and 3 and that leads to an input of 0. Hare if anything else.
            hunting_hare_map[agent.name] = False if intent == 2 or intent == 3 else True
            if isinstance(agent, CabAgent):
                print("This was there intent ", hunting_hare_map[agent.name])

    return hunting_hare_map

def get_action_map_from_agents(agents, state, rewards, round_num, allocations_dict, agent_indicies):
    new_moves_dict = {}
    for index in agent_indicies:
        agent = agents[index]
        # TODO: create a list that maps types to function types for this.
        if agent.name == "stag" or agent.name == "hare" or isinstance(agent, AlegAATr) or isinstance(agent, humanAgent): # humans don't create allocations either!
            new_moves_dict[agent.name] = agent.act(state, rewards[index], round_num)
        else:
            id = int(agent.name[-1])
            # we never actually do anything with the new index, so there's that.
            # we shoudl get rid of him but I have a hard time trying to care.
            new_moves_dict[agent.name], new_index = allocation_to_movement(allocations_dict[agent.name], id, state)

    return new_moves_dict





def set_jhg_agents_params(agents, engine):
    # set up the bots for the engine.
    for agent in agents:
        if isinstance(agent, CabAgent):
            agent.set_helpers(engine)  # sets all the JHG engine stuff.

# TODO: REMOVE THIS WHEN DONE TESTING
def jhg_to_staghunt(agents, state, rewards, round_num, engine):

    # first, lets grab all the allocations and separate the wheat from the chaff
    new_moves = {}
    new_allocations = {}
    new_intents = {}
    allocations = [[] for _ in range(3)]
    indices = list(range(len(agents)))
    # np.random.shuffle(indices)
    hunting_hare_map = {}
    for i in indices:
        agent = agents[i]
        reward = 0 if (i == 0 or i == 1) else rewards[i]
        if not isinstance(agent, CabAgent) and not isinstance(agent, FetcherBot) and not isinstance(agent, HareAgent) and not isinstance(agent, StagAgent) and not isinstance(agent, HumanAgent):
            new_moves[agent.name] = agent.act(state, reward, round_num) # should be noted that these are just prey moves. they are essentialy random.
            hunting_hare_map[agent.name] = agent.is_hunting_hare()
        else:
            # print("This is the id we are dealing with ", int(agent.name[-1]))
            allocation = agent.act(state, reward, round_num)
            new_allocations[agent.name] = allocation

    # allocation to generators (for which we have the translator)
    keys = new_allocations.keys()
    # print("hare are the initial allocations dict ", new_allocations)
    # print("here are hte new allocations ", new_allocations)

    for key in keys:
        id = int(key[-1]) # might be a desync here?
        # if id == 0:
        #     print("here is teh allocation ", new_allocations[key])
        # print(f"Raw allocation for {key}: {new_allocations[key]}, sum={sum(new_allocations[key])}")
        (new_row, new_col), movement_type = allocation_to_movement(new_allocations[key], id, state)
        new_move = [new_row, new_col]
        new_moves[key] = new_move # bars??
        new_intents[key] = movement_type

    new_allocations = dict(sorted(new_allocations.items(), key=lambda item: item[0]))
    # print("The initial allocations are as follows : ", new_allocations)
    # need TO PASS IT IN to account for discrepancies.

    # print("Round ", round_num, " thing ", new_allocations.items())

    hunting_hare_map = create_map_from_intents(new_intents, hunting_hare_map)
    print_hare_hunting_map(hunting_hare_map)
    return new_moves, hunting_hare_map, new_allocations # then just give the moves back.
    # note that these are in a dictionary, I'll have to do weird things to randomize the order that this happens in.

    # I really should preseve the dictionary aspect of this huh
    # that way I cna do things ot keep track and randomize things and keep track of who moved where.