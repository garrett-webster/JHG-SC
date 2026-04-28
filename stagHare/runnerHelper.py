# the purpose of this is to try and dry out a bunch of code.
# found in previous projects that I have a bunch of functions that I will recycle between runs, so its nice to have
# it all in one spot. That way, as I modify and upgrade it, we can make all the changes IN THIS FILE
# so all the functions are on the same level.
# yes we have had problems with it before. Don't worry about it.
import traceback

from packaging.utils import canonicalize_name

from stagHare.agents.cabAgentThing import CabAgent
from stagHare.agents.fetcherBot import FetcherBot
from stagHare.environment.state import State
from stagHare.environment.world import StagHare
from stagHare.agents.random_agent import Random
from stagHare.agents.hareAgent import HareAgent
from stagHare.agents.stagAgent import StagAgent
from stagHare.agents.alegaatr import AlegAATr # litmus test
import numpy as np
import time

from stagHare.loggingStuff.stagHareLogger import stagHareLogger, informationObject
from stagHare.visualziationTools.gameLogger import GameLogger
from stagHare.visualziationTools.inviduvalRoundGrapher import IndividualRoundGrapher


def run_trial_graphing(stag_hare, current_round_grapher, current_game_logger):
    intents = [] # I want to return this now. this sucks.
    agent_positions = []
    while True: # the way this gets run is VERY VERY weird.

        current_game_logger.add_round(stag_hare.state)
        intents.append(create_intents_list(stag_hare.state.hunting_hare_map)) # Might need to custom cast this to integers.
        agent_positions.append(stag_hare.state.agent_positions.copy())
        # have this generate right off the bat
        # current_round_grapher.create_round_graph(stag_hare)
        rewards = [0] * 5 # 3 hunters, 2 other peeps
        # this is a reminder to check the action map to make sure that we are hunting what we think we are.

        round_rewards = stag_hare.transition()
        for i, reward in enumerate(round_rewards):
            rewards[i] += reward

        if stag_hare.is_over():
            agent_positions.append(stag_hare.state.agent_positions)
            current_game_logger.add_round(stag_hare.state)
            intents.append(create_intents_list(stag_hare.state.hunting_hare_map))
            # current_round_grapher.create_round_graph(stag_hare)
            # passes by value. thanks python.
            return create_new_score(stag_hare), intents, agent_positions, stag_hare.popularity_over_time, stag_hare.hunters

def run_trial_sim_no_graphing(stag_hare):
    intents = [] # THIs is not elegant, but it does work.
    agent_positions = []
    while True:
        intents.append(create_intents_list(stag_hare.state.hunting_hare_map)) # Might need to custom cast this to integers.
        print("here are the intents ", intents)
        agent_positions.append(stag_hare.state.agent_positions.copy())
        rewards = [0] * 5 # 3 hunters, 2 other peeps

        round_rewards = stag_hare.transition()
        for i, reward in enumerate(round_rewards):
            rewards[i] += reward

        if stag_hare.is_over():
            intents.append(create_intents_list(stag_hare.state.hunting_hare_map))
            agent_positions.append(stag_hare.state.agent_positions)
            # print(f"here are the agent positions, {agent_positions}")
            return create_new_score(stag_hare), intents, agent_positions, stag_hare.popularity_over_time, stag_hare.hunters # that should do the trick.


def create_intents_list(current_intents: dict) -> list:
    new_list = []
    for key, value in current_intents.items():
        if not key == "stag" and not key == "hare":
            new_list.append(int(value))
    return new_list

# takes in a list of list of lists, then returns both the total defect percent and defect by agent.
def process_intents(current_intents: list) -> tuple[int, list]:

    # this gets rid of the 2,2,2, which is easier to do when we are still thinking of them as a list of games of rounds of intents.
    filtered_and_flattened = [round_list for game_list in current_intents for round_list in game_list if round_list != [2,2,2]] # good lord what is happening in there.

    # this just then gets me the raw score.

    transposed = list(zip(*filtered_and_flattened))

    new_sum = np.sum(transposed, axis=1)

    num_rounds = len(filtered_and_flattened)
    num_columns = len(transposed)

    column_percentages = new_sum / num_rounds
    total_percentage = sum(new_sum) / (num_rounds * num_columns)

    # print("Bad intents sum ", new_sum, " and the total bad intents ", sum(new_sum))
    # print("percentages defect ", column_percentages, " and total ", total_percentage)

    return total_percentage, column_percentages


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

def run_trial_test(agents):
    height = 6
    width = 6

    hunters = agents

    while True:
        stag_hare = StagHare(height, width, hunters)
        if not stag_hare.is_over():
            break  # no reason to start in a finished configuration.

    while True:  # the way this gets run is VERY VERY weird.

        # current_game_logger.add_round(stag_hare.state)
        # have this generate right off the bat
        # current_round_grapher.create_round_graph(stag_hare)
        rewards = [0] * 5  # 3 hunters, 2 other peeps
        # this is a reminder to check the action map to make sure that we are hunting what we think we are.

        round_rewards = stag_hare.transition()
        for i, reward in enumerate(round_rewards):
            rewards[i] += reward

        if stag_hare.is_over():
            # if stag_hare.state.hare_captured():
            #     print("hare dead")
            # else:
            #     print('stag dead')

            # current_game_logger.add_round(stag_hare.state)
            # passes by value. thanks python.
            return create_new_score(stag_hare)  # should return the new score array.

def run_trial_step(agent_names, height, width, random_agents, forced_random, scenario_type):

    scores = []
    intents = []
    agent_positions = []
    popularity_over_time = []

    num_rounds_per_game = 10 # lets start here.
    current_logger = stagHareLogger()


    hunters = create_hunters_with_list(random_agents, forced_random, agent_names)


    while True:
        stag_hare = StagHare(height, width, hunters)
        if not stag_hare.is_over():
            break

    for i in range(num_rounds_per_game):
        # does this suck? possibly.
        stag_hare.state.hunting_hare_map = {"R" + str(i): 2 for i in
                                            range(3)}  # value that it can never be, sort of a NAN.

        # just run the fetcher.
        new_score, new_intents, new_positions, popularity_over_time, hunters = run_trial_sim_no_graphing(stag_hare)

        # just set up a new state that doesn't break immediatel.y
        while True:
            stag_hare.state.reset_positions()  # maybe this will work?
            if not stag_hare.is_over():
                break

        scores.append(new_score)
        intents.append(new_intents)
        agent_positions.append(new_positions)

    cooperation_score, scores_per_player = process_scores(scores)
    hare_intent_percent_total, hare_intent_percent_player = process_intents(intents)
    game_information = informationObject(scenario_type, cooperation_score, scores_per_player, agent_names, hare_intent_percent_total, hare_intent_percent_player, agent_positions, popularity_over_time, hunters, height, width, intents)
    return game_information




# def run_trial_step(agent_type, agent_name, height, width, random_agents, forced_random):
#     try:
#         # changed on 3/17 to allow height and width to be passed in instead of specified here.
#         new_scores = []
#         new_intents = []
#         # want to monitor how things work.
#         hunters = create_hunters(agent_type, random_agents, forced_random, agent_name, agent_scenario=0)
#         round = 0
#         num_per_batch = 5
#
#         while True:
#             stag_hare = StagHare(height, width, hunters)
#             if not stag_hare.is_over():
#                 break # no reason to start in a finished configuration.
#
#         i = 0
#         while True: # the way this gets run is VERY VERY weird.
#             new_intents.append(create_intents_list(stag_hare.state.hunting_hare_map))  # Might need to custom cast this to integers.
#             new_scores.append(create_new_score(stag_hare))
#             round += 1
#             rewards = [0] * 5 # 3 hunters, 2 other peeps
#
#             round_rewards = stag_hare.transition()
#             for i, reward in enumerate(round_rewards):
#                 rewards[i] += reward
#
#
#
#             if stag_hare.is_over():
#                 new_scores.append(create_new_score(stag_hare))
#                 i += 1
#                 if i == num_per_batch: # gotta get out here at some point.
#                     break
#
#                 while True:
#                     stag_hare.state.reset_positions()  # maybe this will work?
#                     if not stag_hare.is_over():
#                         break
#
#         return process_scores(new_scores), process_intents(new_intents) # should return the new score array.
#     except Exception as e:
#         print("FUTURE CRASHED: ", e)
#         traceback.print_exc()


def run_trial(agent_names, height, width, random_agents, forced_random, scenario_type):
    try:
        start = time.time()
        # changed on 3/17 to allow height and width to be passed in instead of specified here.

        # want to monitor how things work.
        hunters = create_hunters_with_list(random_agents, forced_random, agent_names)
        current_game_logger = GameLogger(height, width, agent_names, scenario_type)
        current_round_grapher = IndividualRoundGrapher()

        while True:
            stag_hare = StagHare(height, width, hunters) # np
            if not stag_hare.is_over():
                break # no reason to start in a finished configuration.

        # it will break if you get rid of this. you know, as a heads up.
        stag_hare.state.hunting_hare_map = {"R" + str(i): 2 for i in
                                            range(3)}  # value that it can never be, sort of a NAN.

        # print(f"this si the fetcher for {stag_hare.state.agent_positions}")

        # new_score, new_intents, new_positions, popularity_over_time, hunters = run_trial_sim_no_graphing(stag_hare)
        new_score, new_intents, new_positions, popularity_over_time, hunters = run_trial_graphing(stag_hare, current_round_grapher, current_game_logger)

        scores, intents, agent_positions, popularity_over_time = [new_score], [new_intents], new_positions, popularity_over_time

        cooperation_score, scores_per_player = process_scores(scores)
        hare_intent_percent_total, hare_intent_percent_player = process_intents(intents)
        game_information = informationObject(scenario_type, cooperation_score, scores_per_player, agent_names,
                                             hare_intent_percent_total, hare_intent_percent_player, agent_positions,
                                             popularity_over_time, hunters, height, width, intents)
        return game_information


        # while True: # the way this gets run is VERY VERY weird.
        #     # print("do we get here")
        #     round += 1
        #     # current_game_logger.add_round(stag_hare.state)
        #     # have this generate right off the bat
        #     # current_round_grapher.create_round_graph(stag_hare)
        #     rewards = [0] * 5 # 3 hunters, 2 other peeps
        #     # this is a reminder to check the action map to make sure that we are hunting what we think we are.
        #
        #     round_rewards = stag_hare.transition()
        #     for i, reward in enumerate(round_rewards):
        #         rewards[i] += reward
        #
        #     if round > 100:
        #         print("l9onger than 100 rounds")
        #     if round > 500:
        #         print("longer than 500 rounds")
        #     if round > 1000:
        #         print("longer than 1000 rounds")
        #
        #     elapsed = time.time() - start
        #     if elapsed > 10.0:
        #         print("AYO WE GOT A STRAGLER HERE, num rounds ", str(round))
        #     if stag_hare.is_over():
        #         # if stag_hare.state.hare_captured():
        #         #     print("hare dead")
        #         # else:
        #         #     print('stag dead')
        #
        #         # current_game_logger.add_round(stag_hare.state)
        #         # passes by value. thanks python.
        #         return create_new_score(stag_hare) # should return the new score array.



    except Exception as e:
        print("FUTURE CRASHED: ", e)
        traceback.print_exc()



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

def create_hunters_with_genes(genes, random_agents, forced_random):
    new_hunters = []
    agent_name = "gen_199.csv"


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


def create_hunters_scenario(agent_name, agent_scenario):
    new_hunters = []
    random_agents = True
    forced_random = False

    if agent_scenario == 1:
        for i in range(3):
            new_name = "R" + str(i)
            new_hunters.append(CabAgent(i, new_name, random_agents, forced_random, gene="", agent_name=agent_name))

    # start of the ecab v experts portion.

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

    for i in range(3):
        new_name = "R" + str(i)
        agent_name = agent_list[i]
        cab_agent = False
        if agent_name.endswith(".csv"):
            cab_agent = True

        if cab_agent:
            new_hunters.append(CabAgent(i, new_name, random_agents, forced_random, gene="", agent_name=agent_name))

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



def create_hunters(agent_type, random_agents, forced_random, agent_name="", agent_scenario=0):

    new_hunters = []

    if agent_scenario == 2:
        for i in range(2):
            new_name = "R" + str(i)

            if agent_type == -1:
                new_hunters.append(AlegAATr(name=new_name, lmbda=0.0, ml_model_type='knn', enhanced=True))

            if agent_type == 0:
                new_hunters.append(Random(name=new_name))

            if agent_type == 1:
                new_hunters.append(HareAgent(i, name=new_name))

            if agent_type == 2:
                new_hunters.append(StagAgent(i, name=new_name))

            if agent_type == 3:
                new_hunters.append(CabAgent(i, new_name, random_agents, forced_random, gene="", agent_name=agent_name))


        # this guy doesn't need an agent name or anything.
        new_name = "R2"
        new_hunters.append(FetcherBot(2, new_name))

    elif agent_scenario == 3: # put one cab agent in with a bunch of guys.
        new_name = "R0"
        new_hunters.append(CabAgent(0, new_name, agent_name))
        new_name = "R1"
        new_hunters.append(StagAgent(1, name=new_name))
        new_name = "R2"
        new_hunters.append(StagAgent(2, name=new_name))

    elif agent_scenario == 5:
        new_name = "R0"
        new_hunters.append(CabAgent(0, new_name, agent_name))
        new_name = "R1"
        new_hunters.append(CabAgent(1, new_name, agent_name))
        new_name = "R2"
        new_hunters.append(StagAgent(2, name=new_name))


    elif agent_scenario == 4: # put one cab agent in with a bunch of guys.
        new_name = "R0"
        new_hunters.append(CabAgent(0, new_name, agent_name))
        new_name = "R1"
        new_hunters.append(HareAgent(1, name=new_name))
        new_name = "R2"
        new_hunters.append(HareAgent(2, name=new_name))

    elif agent_scenario == 6:
        new_name = "R0"
        new_hunters.append(CabAgent(0, new_name, agent_name))
        new_name = "R1"
        new_hunters.append(CabAgent(1, new_name, agent_name))
        new_name = "R2"
        new_hunters.append(HareAgent(2, name=new_name))



    else:
        for i in range(3):
            new_name = "R" + str(i)

            if agent_type == -1:
                new_hunters.append(AlegAATr(name=new_name, lmbda=0.0, ml_model_type='knn', enhanced=True))

            if agent_type == 0:
                new_hunters.append(Random(name=new_name))

            if agent_type == 1:
                new_hunters.append(HareAgent(i, name=new_name))

            if agent_type == 2:
                new_hunters.append(StagAgent(i, name=new_name))

            if agent_type == 3:
                new_hunters.append(CabAgent(i, new_name, random_agents, forced_random, gene="", agent_name=agent_name))


            # if agent_type == 4:
            #     new_hunters.append(QAlegAATr(name=new_name, enhanced=True))



        # print("this shoudl fire")


    return new_hunters # just make sure to get those new guys in somewhere.


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

    # I should be doing this in a json logger thing but I don't care.
    # print("here was the cooperation score \n", cooperation_score)
    # print("here was the scores per player \n", scores_per_player)
    # print("here were the total scores \n", total_sum_per_player)

    return cooperation_score, scores_per_player

