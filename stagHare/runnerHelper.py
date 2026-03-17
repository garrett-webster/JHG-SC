# the purpose of this is to try and dry out a bunch of code.
# found in previous projects that I have a bunch of functions that I will recycle between runs, so its nice to have
# it all in one spot. That way, as I modify and upgrade it, we can make all the changes IN THIS FILE
# so all the functions are on the same level.
# yes we have had problems with it before. Don't worry about it.
from operator import itemgetter

from tqdm import tqdm

from offlineSimStuff.runningTools.runnerHelper import create_jhg_sim, create_total_order, create_jhg_engine
from stagHare.agents.cabAgentThing import CabAgent
from stagHare.agents.fetcherBot import FetcherBot
from stagHare.environment.world import StagHare
from stagHare.environment.allocationTranslator import allocation_to_movement, movement_to_allocation
from stagHare.visualziationTools.batchLogger import BatchLogger
from stagHare.visualziationTools.inviduvalRoundGrapher import IndividualRoundGrapher
from stagHare.visualziationTools.gameGrapher import GameGrapher
from stagHare.visualziationTools.gameLogger import GameLogger
from stagHare.agents.random_agent import Random
from stagHare.agents.hareAgent import HareAgent
from stagHare.agents.stagAgent import StagAgent
from stagHare.agents.alegaatr import AlegAATr # litmus test
# from stagHare.agents.qalegaatr import QAlegAATr
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed




def run_trial_graphing(stag_hare, current_round_grapher, current_game_logger):
    while True: # the way this gets run is VERY VERY weird.

        # current_game_logger.add_round(stag_hare.state)
        # have this generate right off the bat
        # current_round_grapher.create_round_graph(stag_hare)
        rewards = [0] * 5 # 3 hunters, 2 other peeps
        # this is a reminder to check the action map to make sure that we are hunting what we think we are.

        round_rewards = stag_hare.transition()
        for i, reward in enumerate(round_rewards):
            rewards[i] += reward

        if stag_hare.is_over():
            # current_game_logger.add_round(stag_hare.state)
            # current_round_grapher.create_round_graph(stag_hare)
            # passes by value. thanks python.
            return create_new_score(stag_hare)


def run_trial_genetic(hunters):

    height, width = 6, 6

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

def run_trial(agent_type, agent_name):

    # lets try this first...
    height = 6
    width = 6

    # want to monitor how things work.
    hunters = create_hunters(agent_type, agent_name, agent_scenario=0)

    while True:
        stag_hare = StagHare(height, width, hunters)
        if not stag_hare.is_over():
            break # no reason to start in a finished configuration.

    while True: # the way this gets run is VERY VERY weird.

        # current_game_logger.add_round(stag_hare.state)
        # have this generate right off the bat
        # current_round_grapher.create_round_graph(stag_hare)
        rewards = [0] * 5 # 3 hunters, 2 other peeps
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
            return create_new_score(stag_hare) # should return the new score array.



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

def create_hunters_with_genes(genes):
    new_hunters = []
    agent_name = "gen_199.csv"
    forcedRandom = False # just do this for now.

    for i in range(3):
        new_name = "R" + str(i)
        new_hunters.append(CabAgent(i, new_name, genes[i]))


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
        a.agent.setGameParams(game_params, forcedRandom)

    return new_hunters


def create_hunters_scenario(agent_name, agent_scenario):
    new_hunters = []

    if agent_scenario == 1:
        for i in range(3):
            new_name = "R" + str(i)
            new_hunters.append(CabAgent(i, new_name, agent_name))

    # start of the ecab v experts portion.


def create_hunters(agent_type, agent_name="", agent_scenario=0):

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
                new_hunters.append(CabAgent(i, new_name, agent_name))

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
                new_hunters.append(CabAgent(i, new_name, gene="", agent_name=agent_name))


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
    print("here was the cooperation score \n", cooperation_score)
    print("here was the scores per player \n", scores_per_player)
    print("here were the total scores \n", total_sum_per_player)

    return cooperation_score, scores_per_player

