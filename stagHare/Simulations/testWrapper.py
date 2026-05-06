import json
import os
from tqdm import tqdm
from win32cryptcon import szOID_COMMON_NAME

from stagHare.loggingStuff.stagHareLogger import GameInformationResultsCompiler
from stagHare.visualziationTools.batchLogger import BatchLogger
from concurrent.futures import ProcessPoolExecutor, as_completed
from stagHare.runnerHelper import *  # this SHOULD be all we need.
from stagHare.visualziationTools.gameGrapher import GameGrapher
from stagHare.visualziationTools.gameLogger import information_object_to_game_logger

def run_test(curr_agent_name, scenario_type, height, width, random_agents, forced_random,
             GamesPerRound, graphing):

    # how many resources can we actually devote to this??
    max_workers = max(1, os.cpu_count() - 2)  # save just a few for other processes, plz don't crash.
    # max_workers = 1 # spawns only a single thread, simplifying debugging.
    current_batch_logger = GameInformationResultsCompiler(height, width, curr_agent_name, scenario_type)
    results = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for attempt in range(num_attempts):
            futures.append(
                executor.submit(run_trial_all, curr_agent_name, height, width, random_agents, forced_random,
                                scenario_type, GamesPerRound, graphing))

        for future in as_completed(futures):
            results.append(future.result())

        for result in results:
            current_batch_logger.add_game(result)  # this SHOULD be the actual information object.

    return current_batch_logger  # just do this once per scenario.

def write_batch_results_to_file(current_batch_logger, scenario_type):
    directory_path = "results/"
    new_dict = {}
    coop_scores, score_per_player, hare_intent_percent_total, popularity_over_time = current_batch_logger.get_batch_results()
    new_dict["coop_scores"] = coop_scores
    new_dict["score_per_player"] = score_per_player
    new_dict["hare_intent_percent_total"] = hare_intent_percent_total.tolist()
    new_dict["popularity_over_time"] = popularity_over_time
    with open(directory_path + f"{scenario_type}.json", "w") as f:
        json.dump(new_dict, f, indent=2)

# some global variables
height = 16
width = 16
RandomAgents = True
forced_random = False
num_attempts = 100

# base_agents = ["SCab", "HCab", "ECab99", "ECab199", "Allegatr"]
# base_agents = ["HCab", "ECab99", "ECab199"]
base_agents = ["HCab", "ECab199"]

base_to_csv = {
    "SCab": "16x16round4.csv",
    "HCab": "gen_z.csv",
    "ECab99": "gen_99.csv",
    "ECab199": "gen_199.csv",
    "Allegatr": "Allegatr",
}
game_types = ["Round", "Step"]

scenarios = ["SelfPlay", "VGHare1", "VGHare2", "VGStag1", "VGStag2", "Allegatr1", "Allegatr2"]
# scenarios = ["SelfPlay"]

def get_agents(agent, scenario):
    if scenario == "SelfPlay":
        new_list = [base_to_csv[agent] for _ in range(3)]
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

# removing Json implementatino because that was dumb and bad. back to pure script based.
if __name__ == "__main__":
    height, width, RandomAgents, forced_random, num_attempts = height, width, RandomAgents, forced_random, num_attempts
    games_per_round = 10
    graphing = False

    for agent in tqdm(base_agents):
        for scenario in scenarios:
            for game_type in game_types:
                scenario_type = str(agent) + str(scenario) + str(game_type)

                curr_agent_name = get_agents(agent, scenario)
                new_batch_logger = run_test(curr_agent_name, scenario_type, height, width, RandomAgents,
                                            forced_random, games_per_round, graphing)
                write_batch_results_to_file(new_batch_logger, scenario_type)

