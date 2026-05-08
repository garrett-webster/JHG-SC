# the purpose of this is to try and dry out a bunch of code.
# found in previous projects that I have a bunch of functions that I will recycle between runs, so its nice to have
# it all in one spot. That way, as I modify and upgrade it, we can make all the changes IN THIS FILE
# so all the functions are on the same level.
# yes we have had problems with it before. Don't worry about it.
import traceback

from packaging.utils import canonicalize_name

from stagHare.agents.cabAgentThing import CabAgent
from stagHare.agents.fetcherBot import FetcherBot
from stagHare.environment.jhgToStaghunt import create_map_from_intents
from stagHare.environment.state import State
from stagHare.environment.world import StagHare
from stagHare.agents.random_agent import Random
from stagHare.agents.hareAgent import HareAgent
from stagHare.agents.stagAgent import StagAgent
from stagHare.agents.alegaatr import AlegAATr # litmus test
import numpy as np
import time

from stagHare.loggingStuff.stagHareLogger import GameInformationObject
from stagHare.visualziationTools.gameLogger import GameLogger
from stagHare.visualziationTools.inviduvalRoundGrapher import IndividualRoundGrapher


# just gets rid of the stupid SKELARN warning for allegatr. I'm not touching that.
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

def create_intents_list(current_intents: dict) -> list:
    new_list = [-1 for _ in range(3)] # yeah that might blow up. whatever.
    for key, value in current_intents.items():
        if not key == "stag" and not key == "hare":
            # new_list.append(int(value))
            # R2 --> 2, etc. This WON'T work for human players. Whatever. I'll figure it out later.
            new_list[int(key[-1])] = int(value)
    return new_list

# takes in a list of list of lists, then returns both the total defect percent and defect by agent.
def process_intents(current_intents: list) -> tuple[int, list]:
    # this gets rid of the 2,2,2, which is easier to do when we are still thinking of them as a list of games of rounds of intents.
    filtered_and_flattened = [round_list for game_list in current_intents for round_list in game_list if round_list != [2,2,2]] # good lord what is happening in there.
    # this just then gets me the raw score.
    transposed = list(zip(*filtered_and_flattened))
    new_sum = np.sum(transposed, axis=1)
    num_rounds = len(filtered_and_flattened)
    column_percentages = new_sum / num_rounds
    return column_percentages # we ONLY want the column ones. for reasons.

# this is worth keeping around because it has to return specific stuff for the genetic algorithm.
def run_trial_genetic(hunters, height, width):

    # create the instance simulator
    while True:
        stag_hare = StagHare(height, width, hunters)
        if not stag_hare.is_over():
            break

    # IDK if this is necessary but I figure it can't hurt.
    stag_hare.state.hunting_hare_map = {"R" + str(i): 2 for i in range(3)}  # value that it can never be, sort of a NAN.

    while True: # the way this gets run is VERY VERY weird.

        # this is importnat for reasons.
        rewards = [0] * 5 # 3 hunters, 2 other peeps
        # this is a reminder to check the action map to make sure that we are hunting what we think we are.

        round_rewards = stag_hare.transition()
        for i, reward in enumerate(round_rewards):
            rewards[i] += reward

        if stag_hare.is_over():
            return create_new_score(stag_hare)


def run_trial_engine_stripped(stag_hare, noisy=True):
    allocations_list = []
    old_allocations_list = []
    while True: # the way this gets run is VERY VERY weird.
        rewards = [0] * 5 # 3 hunters, 2 other peepsdd
        # this is a reminder to check the action map to make sure that we are hunting what we think we are.

        # user specified version of the transition function based on noise requests.
        if noisy:
            round_rewards, old_allocations, allocations  = stag_hare.transition_noisy_return_allocations()
            old_allocations_list.append(list(old_allocations.values()))
            allocations_list.append(allocations)
        else:
            round_rewards, old_allocations = stag_hare.transition_return_allocations()
            old_allocations_list.append(list(old_allocations.values()))
            allocations_list.append(None)
        for i, reward in enumerate(round_rewards):
            rewards[i] += reward

        if stag_hare.is_over():
            return old_allocations_list, allocations_list



def run_trial_engine(stag_hare, graphing, current_round_grapher, current_game_logger, noisy=True):
    intents = [] # I want to return this now. this sucks.
    agent_positions = []
    while True: # the way this gets run is VERY VERY weird.

        intents.append(create_intents_list(stag_hare.state.hunting_hare_map)) # Might need to custom cast this to integers.
        agent_positions.append(stag_hare.state.agent_positions.copy())

        if graphing:
            current_game_logger.add_round(stag_hare.state)
            current_round_grapher.create_round_graph(stag_hare)
        rewards = [0] * 5 # 3 hunters, 2 other peepsdd
        # this is a reminder to check the action map to make sure that we are hunting what we think we are.

        # user specified version of the transition function based on noise requests.
        if noisy:
            round_rewards = stag_hare.transition_noisy()
        else:
            round_rewards = stag_hare.transition()
        for i, reward in enumerate(round_rewards):
            rewards[i] += reward

        if stag_hare.is_over():
            agent_positions.append(stag_hare.state.agent_positions)
            if graphing:
                current_game_logger.add_round(stag_hare.state)
                current_round_grapher.create_round_graph(stag_hare)
            intents.append(create_intents_list(stag_hare.state.hunting_hare_map))
            # passes by value. thanks python.
            return create_new_score(stag_hare), intents, agent_positions, stag_hare.popularity_over_time, stag_hare.hunters

def run_trial_debugging(stag_hare, graphing, current_round_grapher, current_game_logger, noisy):
    pre_intents = []
    post_intents = []
    post_intents.append([2, 2, 2])
    while True: # the way this gets run is VERY VERY weird.

        pre_intents.append(create_intents_list(stag_hare.state.hunting_hare_map)) # Might need to custom cast this to integers.


        if graphing:
            current_game_logger.add_round(stag_hare.state)
            current_round_grapher.create_round_graph(stag_hare)
        rewards = [0] * 5 # 3 hunters, 2 other peepsdd
        # this is a reminder to check the action map to make sure that we are hunting what we think we are.

        if noisy == True:
            round_rewards, new_intents = stag_hare.transition_sean_debug()
        if noisy == False:

            post_intents.append(new_intents)

        for i, reward in enumerate(round_rewards):
            rewards[i] += reward

        if stag_hare.is_over():
            if graphing:
                current_game_logger.add_round(stag_hare.state)
                current_round_grapher.create_round_graph(stag_hare)
            pre_intents.append(create_intents_list(stag_hare.state.hunting_hare_map))
            # post_intents.append(create_intents_list(stag_hare.state.hunting_hare_map)) # maybe???
            # passes by value. thanks python.
            return pre_intents, post_intents



def get_graphing_stuff(graphing, height, width, agent_names, scenario_type):
    if graphing == True:
        current_game_logger = GameLogger(height, width, agent_names, scenario_type)
        current_round_grapher = IndividualRoundGrapher()
    else: # we need to make the game logger and round grapher have something, so they have None.
        current_game_logger = None
        current_round_grapher = None
    return current_game_logger, current_round_grapher

def get_stag_hare(height, width, hunters):
    while True: # get stag hare.
        stag_hare = StagHare(height, width, hunters)
        if not stag_hare.is_over():
            break

    return stag_hare

def reset_stag_hare(stag_hare):
    while True:
        stag_hare.state.reset_positions()  # maybe this will work?
        if not stag_hare.is_over():
            break

    return stag_hare

def run_trial_all(agent_names, height, width, random_agents, forced_random, scenario_type, num_rounds_per_game, graphing):
    current_game_logger, current_round_grapher = get_graphing_stuff(graphing, height, width, agent_names, scenario_type)

    # if there is an imputted value, use that. If none, run it only once.
    run_amount = num_rounds_per_game if num_rounds_per_game is not None else 1

    hunters = create_hunters_with_list(random_agents, forced_random, agent_names)

    scores = []
    intents = []
    agent_positions = []
    # this gets tracked in the fetching simulator. that was a terrible idea. what if we don't do that.
    end_popularities = []

    stag_hare = get_stag_hare(height, width, hunters)
    popularity_over_time = []

    for i in range(run_amount): # if we only do 1 game, we only do this once.
        # does this suck? possibly.

        stag_hare.state.hunting_hare_map = {"R" + str(i): 2 for i in range(3)}  # Fill with NULL value

                                                                            # consolidated this into one super function, tests are in the test suite.
        new_score, new_intents, new_positions, popularity_over_time, hunters = run_trial_engine(stag_hare, graphing,
                                                                                                current_round_grapher, current_game_logger)

        # make sure to add everything to its appropriate lists.
        scores.append(new_score)
        intents.append(new_intents)
        agent_positions.append(new_positions)
        end_popularities.append(popularity_over_time[-1])
        popularity_over_time = popularity_over_time

        # just set up a new state that doesn't break immediately
        stag_hare = reset_stag_hare(stag_hare)

    cooperation_score, scores_per_player = process_scores(scores)
    hare_intent_percent_player = process_intents(intents)
    # end_popularities = end_popularities[::-1] # don't need to do that now.
    game_information = GameInformationObject(scenario_type, cooperation_score, scores_per_player, agent_names,
                                             hare_intent_percent_player, agent_positions, end_popularities, hunters,
                                             height, width, intents, popularity_over_time)
    return game_information

def run_trial_all_debugging(agent_names, height, width, random_agents, forced_random, scenario_type, num_rounds_per_game, graphing):
    current_game_logger, current_round_grapher = get_graphing_stuff(graphing, height, width, agent_names, scenario_type)

    # if there is an imputted value, use that. If none, run it only once.
    run_amount = num_rounds_per_game if num_rounds_per_game is not None else 1

    hunters = create_hunters_with_list(random_agents, forced_random, agent_names)

    pre_intents = []
    post_intents = []
    stag_hare = get_stag_hare(height, width, hunters)

    for i in range(run_amount): # if we only do 1 game, we only do this once.
        # does this suck? possibly.
        stag_hare.state.hunting_hare_map = {"R" + str(i): 2 for i in range(3)}  # Fill with NULL value

                                                                            # consolidated this into one super function, tests are in the test suite.
        new_pre_intents, new_post_intents = run_trial_debugging(stag_hare, graphing, current_round_grapher, current_game_logger)

        # make sure to add everything to its appropriate lists.
        pre_intents.append(new_pre_intents)
        post_intents.append(new_post_intents)

        # just set up a new state that doesn't break immediately
        stag_hare = reset_stag_hare(stag_hare)

    # end_popularities = end_popularities[::-1] # don't need to do that now.
    return pre_intents, post_intents

def create_new_score(stag_hare):
    # optional last round printing thing... I think.
    # current_round_grapher.create_round_graph(stag_hare)

    if stag_hare.state.stag_captured():
        return [2, 2, 2] # stag score

    if stag_hare.state.hare_captured():
        # current_game_logger.add_round(stag_hare.state)

        new_score = [0 for _ in range(3)]  # only ever have 3 playuers.
        # gotta figure out WHO did it.
        hare_x, hare_y = stag_hare.state.agent_positions["hare"]
        # possible_hare_captures = stag_hare.state.neighboring_positions(hare_x, hare_y)
        possible_hare_captures = get_possible_agent_captures(hare_x, hare_y,
                                                             stag_hare.state.height)  # if its not square kill me
        for agent in stag_hare.state.agent_positions:
            if agent == "hare" or agent == "stag":
                pass
            else:
                agent_position = stag_hare.state.agent_positions[agent]
                if list(agent_position) in possible_hare_captures:
                    id = int(agent[-1])
                    new_score[id] = 1  # add a rabbit to that thing.

        return new_score



def get_possible_agent_captures(hare_x, hare_y, board_size):
    # possible_moves_col = [[0, -1], [0, 1]]
    # possible_moves_row = [[-1, 0], [1, 0]]

    # all possible move combinations
            # col moves        # row moves
    deltas = [[0, -1], [0, 1], [-1, 0], [1, 0]]

    neighboring_moves = []

    for delta in deltas:
        new_x, new_y = hare_x + delta[0], hare_y + delta[1]

        if new_x < 0:
            new_x = board_size - 1
        elif new_x == board_size:
            new_x = 0

        if new_y < 0:
            new_y = board_size - 1
        elif new_y == board_size:
            new_y = 0

        neighboring_moves.append([new_x, new_y])

    return neighboring_moves

# also used specifically under the genetic algorithm. Leave him alone, he mad wierd.
def create_hunters_with_genes(genes, random_agents, forced_random):
    new_hunters = []
    agent_name = "gen_199.csv"

    # forced random and random agents don't actually matter here, because we are passing a gene down.
    for i in range(3):
        new_name = "R" + str(i)
        new_hunters.append(CabAgent(i, new_name, random_agents, forced_random, gene=genes[i], agent_name=agent_name))


    alpha_min, alpha_max = 0.20, 0.20
    beta_min, beta_max = 0.5, 1.0
    keep_min, keep_max = 0.95, 0.95
    give_min, give_max = 1.30, 1.30
    steal_min, steal_max = 1.6, 1.60

    num_players = 3

    poverty_line = 0

    game_params = {
        "num_players": num_players,
        "alpha": alpha_min,  # np.random.uniform(alpha_min, alpha_max),
        "beta": beta_min,  # np.random.uniform(beta_min, beta_max),
        "keep": keep_min,  # np.random.uniform(keep_min, keep_max),
        "give": give_min,  # np.random.uniform(give_min, give_max),
        "steal": steal_min,  # np.random.uniform(steal_min, steal_max),
        "poverty_line": poverty_line,
        "base_popularity": np.array([100,100,100])

    }

    for a in new_hunters:
        a.agent.setGameParams(game_params, forced_random)

    return new_hunters


# aight here's the plan
# I need a much simpler and more effective way to be able to specify agents all in one go
# instead of this agent scenario agent type agent name tricker.
# so lets fix that -- pass in a list of agents you will be using and go from there. really is that simple.
# the reason we haven't fixed this before was because my original code made assumptions about bot types
# that are no longer reasonable.
def create_hunters_with_list(random_agents:bool , forced_random:bool, agent_list:list):
    """
    :param random_agents: True: Pull random agents from gene pool. False: Pull top agents from gene pool
    :param forced_random: True: Use random.text for RNG generation. False: Standard Numpy RNG.
    :param agent_list: A list containing the agent names (Either the gene name or "Allegatr" or "HCAB"
    """

    new_hunters = []
    # print("curr agnet name ", agent_list)

    for i in range(3):
        new_name = "R" + str(i)
        agent_name = agent_list[i]
        cab_agent = False
        if agent_name.endswith(".csv"):
            cab_agent = True

        if cab_agent:
            new_hunters.append(CabAgent(i, new_name, random_agents, forced_random, gene="", agent_name=agent_name))
            # print("Here is the new gene ", new_hunters[-1].agent.genes_long)
            # confirmed that forcedRandom works as anticipated.

        else: # we have 3 options rught now: G_hare, G_stag, and Allegatr.
            if agent_name == "GHare":
                new_hunters.append(HareAgent(i, name=new_name))
            elif agent_name == "GStag":
                new_hunters.append(StagAgent(i, name=new_name))
            elif agent_name == "Allegatr":
                new_hunters.append(AlegAATr(name=new_name, lmbda=0.0, ml_model_type='knn', enhanced=True))
            elif agent_name == "Random":
                new_hunters.append(Random(name=new_name))
            else:
                print("Unknown agent: ", agent_name, " What are you smoking")

    return new_hunters  # just make sure to get those new guys in somewhere.



def process_scores(scores):
    score_per_player = list(zip(*scores))
    total_sum_per_player = [sum(score) for score in score_per_player]
    scores_per_player = [] # empty list, will hold tuples.
    for i, player in enumerate(score_per_player):
        new_score = [0 for _ in range(3)] # three different types of animals
        for entry in player:
            new_score[entry] += 1
        scores_per_player.append(new_score)

    cooperation_score = sum([2, 2, 2] == score for score in scores) / len(scores)

    # # I should be doing this in a json logger thing but I don't care.
    # print("here was the cooperation score \n", cooperation_score)
    # print("here was the scores per player \n", scores_per_player)
    # print("here were the total scores \n", total_sum_per_player)

    return cooperation_score, scores_per_player

