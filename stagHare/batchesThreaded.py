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


from stagHare.runnerHelper import run_trial, process_scores # this SHOULD be all we need.


# so what do we actually need to do
# lets create some cab agents
# and get them to play this fetcher
# we also need to work on the trnaslation machinery as well
# so that will be interesting.
# this is going ot be strange bc the simulator is VERY different from what I have worked with before
# the SC sim I created and the JHG sim was sort of built for cab agents
# this one has not been built for either of those things.



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



        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for attempt in range(num_attempts):
                futures.append(executor.submit(run_trial, agent_type, agent_name))

            for future in tqdm(as_completed(futures), desc="Submitting Results", total=num_attempts):
                results.append(future.result())

        cooperation_score, scores_per_player = process_scores(results)
