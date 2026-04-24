

import os
from tqdm import tqdm
from stagHare.visualziationTools.batchLogger import BatchLogger
from concurrent.futures import ProcessPoolExecutor, as_completed
from stagHare.runnerHelper import * # this SHOULD be all we need.
from stagHare.visualziationTools.gameGrapher import GameGrapher
from stagHare.visualziationTools.gameLogger import information_object_to_game_logger

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
    # max_workers = 1 # just... just do this for rn. makes debugging a little easier.

    forced_random = True
    random_agents = True  # better for human distribution

    # no round list unfortunately, doesn't work that way
    num_attempts = 4  # don't worry about this
    # keep agent names as a list, will make literally EVERYTHING easier.
    agent_names = [["6x6round3.csv", "6x6round3.csv", "6x6round3.csv"]]
    scenario_types = ["HCAB_self_play"]
    # agent_names = ["homoJHGSelfPlay.csv"]

    print("Step based")
    type="step_based"
    height, width = 16, 16  # lets start there, not too big but there.
    print("height, wdith ", height, " ", width)

    for i, scenario_type in enumerate(scenario_types):
        print("Scenario: " + scenario_type)
        scenario_type += f"_{type}_{num_attempts}"
        current_batch_logger = BatchLogger()
        # unless we want randomize it, then that could a problem.
        # actually yeah thats a problem.
        results = []
        curr_agent_name = agent_names[i] # get just the curr agent names.
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for attempt in range(num_attempts):
                futures.append(executor.submit(run_trial_step, curr_agent_name, height, width, random_agents, forced_random, scenario_type))

            for future in tqdm(as_completed(futures), desc="Submitting Results", total=num_attempts):
                results.append(future.result())

            for result in results:
                game_logger = information_object_to_game_logger(result)
                # we should be able to do all of this
                game_grapher = GameGrapher(result.popularity_over_time,3, curr_agent_name, scenario_type)
                game_grapher.create_game_graph(game_logger)




