import os

from tqdm import tqdm

from offlineSimStuff.runningTools.runnerHelper import create_jhg_sim, create_total_order, create_jhg_engine
from stagHare.agents.cabAgentThing import CabAgent
from stagHare.environment.world import StagHare
from stagHare.environment.allocationTranslator import allocation_to_movement, movement_to_allocation
from stagHare.visualziationTools.batchLogger import BatchLogger
from stagHare.visualziationTools.inviduvalRoundGrapher import IndividualRoundGrapher
from stagHare.visualziationTools.gameGrapher import GameGrapher
from stagHare.visualziationTools.gameLogger import GameLogger
from stagHare.agents.random_agent import Random
from stagHare.agents.hareAgent import HareAgent
from stagHare.agents.stagAgent import StagAgent
from stagHare.agents.alegaatr import AlegAATr  # litmus test

from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np

from stagHare.environment.state import State


# so what do we actually need to do
# lets create some cab agents
# and get them to play this fetcher
# we also need to work on the trnaslation machinery as well
# so that will be interesting.
# this is going ot be strange bc the simulator is VERY different from what I have worked with before
# the SC sim I created and the JHG sim was sort of built for cab agents
# this one has not been built for either of those things.
def run_trial(agent_type, agent_name):

    height = 6
    width = 6
    # create the stag hare fetcher.
    hunters = create_hunters(agent_type, agent_name)  # no reason to make this every attempt. just once per agent should be fine.

    while True:
        stag_hare = StagHare(height, width, hunters)
        if not stag_hare.is_over():
            break

    while True:  # the way this gets run is VERY VERY weird.

        # have this generate right off the bat
        # current_round_grapher.create_round_graph(stag_hare)
        rewards = [0] * 5  # 3 hunters, 2 other peeps
        # this is a reminder to check the action map to make sure that we are hunting what we think we are.

        round_rewards = stag_hare.transition()
        for i, reward in enumerate(round_rewards):
            rewards[i] += reward

        # current_game_logger.add_round(stag_hare.state)

        if stag_hare.is_over():
            return not stag_hare.state.hare_captured() # return a bool, add it to the list.


def create_hunters(agent_type, agent_name=""):
    new_hunters = []
    for i in range(3):
        new_name = "R" + str(i)

        if agent_type == -1:
            new_hunters.append(AlegAATr(name=new_name, lmbda=0.0, ml_model_type='knn', enhanced=True))

        if agent_type == 0:
            new_hunters.append(Random(name=new_name))

        if agent_type == 1:
            new_hunters.append(HareAgent(name=new_name))

        if agent_type == 2:
            new_hunters.append(StagAgent(name=new_name))

        if agent_type == 3:
            new_hunters.append(CabAgent(i, new_name, agent_name))

    return new_hunters  # just make sure to get those new guys in somewhere.


if __name__ == '__main__':

    max_workers = max(1, os.cpu_count()-2) # save just a few for other processes, plz don't crash.

    forcedRandom = True
    random_agents = True  # better for human distribution

    # no round list unfortunately, doesn't work that way

    num_players = 3  # as dictated by the stag hare thing
    num_humans = 0  # yeah...
    # for testing purposes right off the bat, lets work with social welfare. that wi
    jhg_bot_type = 2  # 0 is gene bots, 2 is social welfare and 3 is random. 4 is the new social welfare that I am developing that is just a hair smarter.
    num_attempts = 1000  # don't worry about this
    # don't add cats yet, we will worry about that later.
    # agent_name = "mixedJHGSelfPlay.csv"
    # agent_names = ["gen_99.csv", "gen_Z.csv", "homoJHGSelfPlay.csv", "homoSCselfPlayMFalse.csv",
    #                "homoSCselfPlayMTrue.csv"]
    # agent_names = ["mixedJHGSelfPlay.csv", "mixedSCselfPlayMFalse.csv",
    #                "mixedSCselfPlayMTrue.csv"]

    agent_names = ["homoJHGSelfPlay.csv"]


    # agents = [CabAgent(i, "H"+str(i), agent_name) for i in range(num_players)] # they need names or something.
    addAgents = []
    new_agents = []

    height, width = 6, 6  # lets start there, not too big but there.
    agent_type = 3  # -1 is ALLEGATR, 0 is a random agent, 1 is the hare greedy agent, 2 is stag greedy agent.

    for agent_name in agent_names:
        print("Agent name: " + agent_name)
        current_batch_logger = BatchLogger()
        # unless we want randomize it, then that could a problem.
        # actually yeah thats a problem.
        results = []



        with ProcessPoolExecutor(max_workers=num_players) as executor:
            futures = []
            for attempt in range(num_attempts):
                futures.append(executor.submit(run_trial, agent_type, agent_name))

            for future in as_completed(futures):
                results.append(future.result())




        new_num = np.mean(results)
        print("the ration of stag to hare was ", new_num, " for agent ", agent_name)
