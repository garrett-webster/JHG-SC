# the purpose of this is to try and dry out a bunch of code.
# found in previous projects that I have a bunch of functions that I will recycle between runs, so its nice to have
# it all in one spot. That way, as I modify and upgrade it, we can make all the changes IN THIS FILE
# so all the functions are on the same level.
# yes we have had problems with it before. Don't worry about it.

from copy import deepcopy

from stagHare.environment.jhgToStaghunt import *
from stagHare.environment.world import StagHare
from stagHare.agents.random_agent import Random
from stagHare.agents.hareAgent import HareAgent
from stagHare.agents.stagAgent import StagAgent
from stagHare.agents.alegaatr import AlegAATr # litmus test

from stagHare.loggingStuff.stagHareLogger import GameInformationObject
from stagHare.visualziationTools.gameLogger import GameLogger
from stagHare.visualziationTools.inviduvalRoundGrapher import IndividualRoundGrapher
from stagHare.environment.staghuntToJHG import * # get those fetchers out of here.
from stagHare.Simulations.sharedUtils import base_to_csv



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
# TODO: Fold this all into one.
def run_trial_genetic(theGenes, random_agents, forced_random, height, width, rounds_per_game):

    # create the hunters here and just hope it works.
    hunters = create_hunters_with_genes(theGenes, random_agents, forced_random)  # the assingment has been undererstood


    # create the instance simulator
    stag_hare = get_stag_hare(height, width, hunters)

    for i in range(rounds_per_game): # 1 game, do this once, flows it all into one.
        if i != 0:
            stag_hare = reset_stag_hare(stag_hare) # just puts the guys into new positions without overwriting existing data

        stag_hare = run_trials_given_simulator(stag_hare, False, None, None, True, False)

    # this does append, I triple checked.
    return create_new_score(stag_hare)


# TODO: this breaks when considering human players. Add a total order parameter.
# SORT THIS BASED ON THE LAST NUMBER, that should always be 0 1 or 2. might have to rework some server stuff
# but humans should always be first, and then we should have H0, R1, R2 or H0, H1, R2 or H0, H1, H2 (or all bots).
def allocations_dict_to_list(allocations_dict):
    new_allocations = [v for k, v in sorted(allocations_dict.items(), key=lambda x: int(x[0][1:]))]
    return new_allocations # IDK if this works all the way, I'll have to debug it. Grr.

# this takes in a simulator object, and runs the simulator until completion, with an optional noisy parameter.
def run_trials_given_simulator(stag_hare, graphing, current_round_grapher, current_game_logger, noisy=True, track_allocations=False):
    intents = [] # I want to return this now. this sucks.
    agent_positions = []
    all_allocations = []
    # print("This is noisy at the bottom layer ", noisy)
    stag_hare.state.hunting_hare_map = {"R" + str(i): 2 for i in range(3)}  # Fill with NULL value # just go ahead and do this here.

    while True: # the way this gets run is VERY VERY weird.

        intents.append(create_intents_list(stag_hare.state.hunting_hare_map)) # Might need to custom cast this to integers.
        agent_positions.append(stag_hare.state.agent_positions.copy())

        if graphing:
            current_game_logger.add_round(stag_hare.state)
            current_round_grapher.create_round_graph(stag_hare)

        rewards = [0] * 5 # 3 hunters, 2 other peepsdd


        old_agent_positions = stag_hare.state.agent_positions.copy() # make a copy of this otherwise it updates.
        old_state = deepcopy(stag_hare.state) # ditto.
        # JHG TO STAGHARE SECTION
        set_jhg_agents_params(stag_hare.agents, stag_hare.engine)
        agent_order_indicies = create_agent_indicies(stag_hare.agents)
        # agent_indicies = [0, 1, 2, 3, 4] # hard coded for non scramble for tests.

        allocations_dict = get_allocations_from_agents(stag_hare.agents, stag_hare.state, stag_hare.state.round_num, agent_order_indicies)
        action_map = get_action_map_from_agents(stag_hare.agents, stag_hare.state, rewards, stag_hare.state.round_num, allocations_dict, agent_order_indicies)
        hunting_hare_map = get_hunting_hare_map_from_agents(stag_hare.agents, allocations_dict, agent_order_indicies)
        # print("this here be the hunting hare map ", hunting_hare_map)

        stag_hare.state.hunting_hare_map = hunting_hare_map
        round_rewards = stag_hare.update_intents_and_get_rewards(action_map, hunting_hare_map)

        # STAGHARE to JHG SECTION
        if noisy: # means that we need to translate the allocations from movements, as opposed to passing them straight through.

            allocations_dict = get_allocations_from_movements(stag_hare.state, action_map, old_agent_positions, old_state)

        allocations_list = allocations_dict_to_list(allocations_dict)

        # # printing stuff. don't worry about it.
        # allocations_to_print = allocations_list.copy()
        # if isinstance(allocations_list[0][0], np.float64):
        #     allocations_to_print = [[float(x * 6) for x in row] for row in allocations_list]
        # print("here is the allocations list ", allocations_to_print)

        if track_allocations:
            stag_hare.allocations.append(allocations_list)


        if allocations_list != []: # can't update the engine w/ pure allegatrs.
            stag_hare.update_engine(allocations_list, stag_hare.state.round_num)
        else:
            allocations_list = [None, None, None] # defualt for test purposes.

        all_allocations.append(allocations_list)

        for i, reward in enumerate(round_rewards):
            rewards[i] += reward

        if stag_hare.is_over():
            stag_hare.set_final_variables()
            # agent_positions.append(stag_hare.state.agent_positions)
            if graphing:
                current_game_logger.add_round(stag_hare.state)
                current_round_grapher.create_round_graph(stag_hare)
            intents.append(create_intents_list(stag_hare.state.hunting_hare_map))
            # passes by value. thanks python.
            return stag_hare


def run_single_round_given_simulator(stag_hare, noisy=True):


        rewards = [0] * 5 # 3 hunters, 2 other peepsdd


        old_agent_positions = stag_hare.state.agent_positions.copy() # make a copy of this otherwise it updates.
        old_state = deepcopy(stag_hare.state) # ditto.
        # JHG TO STAGHARE SECTION
        set_jhg_agents_params(stag_hare.agents, stag_hare.engine)
        agent_order_indicies = create_agent_indicies(stag_hare.agents)
        # agent_indicies = [0, 1, 2, 3, 4] # hard coded for non scramble for tests.

        allocations_dict = get_allocations_from_agents(stag_hare.agents, stag_hare.state, stag_hare.state.round_num, agent_order_indicies)
        action_map = get_action_map_from_agents(stag_hare.agents, stag_hare.state, rewards, stag_hare.state.round_num, allocations_dict, agent_order_indicies)
        stag_hare.action_map = action_map # update the action map, trust.
        hunting_hare_map = get_hunting_hare_map_from_agents(stag_hare.agents, allocations_dict, agent_order_indicies)
        # print("this here be the hunting hare map ", hunting_hare_map)

        stag_hare.state.hunting_hare_map = hunting_hare_map
        round_rewards = stag_hare.update_intents_and_get_rewards(action_map, hunting_hare_map)

        # STAGHARE to JHG SECTION
        if noisy: # means that we need to translate the allocations from movements, as opposed to passing them straight through.

            allocations_dict = get_allocations_from_movements(stag_hare.state, action_map, old_agent_positions, old_state)

        allocations_list = allocations_dict_to_list(allocations_dict)


        if allocations_list != []: # can't update the engine w/ pure allegatrs.
            stag_hare.update_engine(allocations_list, stag_hare.state.round_num)
        else:
            allocations_list = [None, None, None] # defualt for test purposes.

        for i, reward in enumerate(round_rewards):
            rewards[i] += reward

        print("This is the allocations list ", allocations_dict)

        return rewards

def get_graphing_stuff(graphing, height, width, agent_names, scenario_type="SelfPlay"):
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

def run_trial_all(agent_names, height, width, random_agents, forced_random, scenario_type, num_rounds_per_game, graphing, noisy=True):
    current_game_logger, current_round_grapher = get_graphing_stuff(graphing, height, width, agent_names, scenario_type)
    run_amount = num_rounds_per_game if num_rounds_per_game is not None else 1
    hunters = create_hunters_with_list(random_agents, forced_random, agent_names)
    # np.random.seed(42)
    stag_hare = get_stag_hare(height, width, hunters)

    for i in range(run_amount): # if we only do 1 game, we only do this once.
        if i != 0: # first run shenanigans.
            stag_hare = reset_stag_hare(stag_hare)

        # consolidated into one super function to make sure everything runs the way that I want it to.
        stag_hare = run_trials_given_simulator(stag_hare, graphing, current_round_grapher, current_game_logger, noisy)


    game_information = stag_hare.get_game_information()
    return game_information

# def run_trial_all_debugging(agent_names, height, width, random_agents, forced_random, scenario_type, num_rounds_per_game, graphing):
#     current_game_logger, current_round_grapher = get_graphing_stuff(graphing, height, width, agent_names, scenario_type)
#
#     # if there is an imputted value, use that. If none, run it only once.
#     run_amount = num_rounds_per_game if num_rounds_per_game is not None else 1
#
#     hunters = create_hunters_with_list(random_agents, forced_random, agent_names)
#
#     pre_intents = []
#     post_intents = []
#     stag_hare = get_stag_hare(height, width, hunters)
#
#     for i in range(run_amount): # if we only do 1 game, we only do this once.
#         # does this suck? possibly.
#         stag_hare.state.hunting_hare_map = {"R" + str(i): 2 for i in range(3)}  # Fill with NULL value
#
#                                                                             # consolidated this into one super function, tests are in the test suite.
#         new_pre_intents, new_post_intents = run_trial_debugging(stag_hare, graphing, current_round_grapher, current_game_logger)
#
#         # make sure to add everything to its appropriate lists.
#         pre_intents.append(new_pre_intents)
#         post_intents.append(new_post_intents)
#
#         # just set up a new state that doesn't break immediately
#         stag_hare = reset_stag_hare(stag_hare)
#
#     # end_popularities = end_popularities[::-1] # don't need to do that now.
#     return pre_intents, post_intents

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
def create_hunters_with_genes(genes, random_agents, forced_random, num_agents=3):
    new_hunters = []
    agent_name = "gen_199.csv"

    # print("these are the genes ", genes)
    # forced random and random agents don't actually matter here, because we are passing a gene down.
    for i in range(num_agents):
        new_name = "R" + str(i)
        # get a random gene, pull that off the top.
        # this could result in everything blowing up if I did this wrongl.
        new_hunters.append(CabAgent(i, new_name, random_agents, forced_random, gene=genes[0], agent_name=agent_name))


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




def get_agents(agent, scenario):
    if scenario == "SelfPlay":
        if agent in base_to_csv:
            new_list = [base_to_csv[agent] for _ in range(3)]
        else:
            if agent == "GHare":
                new_list = ["GHare" for _ in range(3)]

            elif agent == "GStag":
                new_list = ["GStag" for _ in range(3)]

            else:
                print("Borked! Try a different agent name")
                return
    else:
        if "Allegatr" in scenario:
            opponent_type = scenario[0:-1]  # "Allegatr"
        else:
            opponent_type = scenario[1:6]  # "GHare" or "GStag"

        num_opponents = int(scenario[-1])
        num_test_agents = 3 - num_opponents

        test_agents = [base_to_csv[agent] for _ in range(num_test_agents)]
        opponents = [opponent_type for _ in range(num_opponents)]

        new_list = test_agents + opponents


    return new_list


# def process_allocations_for_intent_graphing(allocations):
#     # used entirely for debugging, leave him alone.
#     # old_allocations = deepcopy(allocations)
#
#     # transposes it and gives me a player by player allocation list by round.
#     player_1_allocations, player_2_allocations, player_3_allocations = zip(*allocations)
#
#     # this does nothing but helps me mentally
#     player_1_allocations = player_1_allocations
#
#     # swap the first and second index inner elements of hte lists.
#     for sublist in player_2_allocations: sublist[0], sublist[1] = sublist[1], sublist[0]
#
#     # make the order 3, 1, 2 rather than 1, 2, 3. Yes its ugly!
#     for sublist in player_3_allocations: sublist[0], sublist[1], sublist[2] = sublist[2], sublist[0], sublist[1]
#
#
#     return player_1_allocations, player_2_allocations, player_3_allocations

