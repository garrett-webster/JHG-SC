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

from concurrent.futures import ProcessPoolExecutor, as_completed




def run_trial_graphing(stag_hare, current_round_grapher, current_game_logger):
    while True: # the way this gets run is VERY VERY weird.

        # current_game_logger.add_round(stag_hare.state)
        # have this generate right off the bat
        current_round_grapher.create_round_graph(stag_hare)
        rewards = [0] * 5 # 3 hunters, 2 other peeps
        # this is a reminder to check the action map to make sure that we are hunting what we think we are.

        round_rewards = stag_hare.transition()
        for i, reward in enumerate(round_rewards):
            rewards[i] += reward
        stag_hare.engine



        if stag_hare.is_over():
            # current_game_logger.add_round(stag_hare.state)
            current_round_grapher.create_round_graph(stag_hare)
            # passes by value. thanks python.
            return create_new_score(stag_hare)



def run_trial(agent_type, agent_name):

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
                new_hunters.append(StagAgent(name=new_name))

            if agent_type == 3:
                new_hunters.append(CabAgent(i, new_name, agent_name))

        # this guy doesn't need an agent name or anything.
        new_name = "R2"
        new_hunters.append(FetcherBot(2, new_name))

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
                new_hunters.append(StagAgent(name=new_name))

            if agent_type == 3:
                new_hunters.append(CabAgent(i, new_name, agent_name))

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

