import json
import os
from tqdm import tqdm

from stagHare.loggingStuff.stagHareLogger import GameInformationResultsCompiler
from concurrent.futures import ProcessPoolExecutor, as_completed
from stagHare.runnerHelper import *  # this SHOULD be all we need.

def run_test(curr_agent_name, scenario_type, height, width, random_agents, forced_random, GamesPerRound, graphing, num_attempts):

    # how many resources can we actually devote to this??
    # max_workers = max(1, os.cpu_count() - 2)  # save just a few for other processes, plz don't crash.
    max_workers = 1 # spawns only a single thread, simplifying debugging.
    current_batch_logger = GameInformationResultsCompiler(height, width, curr_agent_name, scenario_type)
    results = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for attempt in tqdm(range(num_attempts)):
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
    new_dict["hare_intent_percent_total"] = hare_intent_percent_total
    new_dict["popularity_over_time"] = popularity_over_time
    with open(directory_path + f"{scenario_type}.json", "w") as f:
        json.dump(new_dict, f, indent=2)


def get_agents(agent, scenario):
    if scenario == "SelfPlay":
        if agent in base_to_csv:
            new_list = [base_to_csv[agent] for _ in range(3)]
        else:
            new_list = ["GStag" for _ in range(3)]
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




# base_agents = ["SCab", "HCab", "ECab99", "ECab199", "Allegatr"]
base_agents = ["Allegatr"]

base_to_csv = {
    "SCab": "16x16round4.csv",
    "HCab": "gen_z.csv",
    "HSCab": "homoSCabs.csv",
    "ECab99": "gen_99.csv",
    "ECab199": "gen_199.csv",
    "Allegatr": "Allegatr",
    "HardHomo": "HardHomo.csv",
}

games_per_round = 2
scenarios = ["SelfPlay", "VGHare1", "VGHare2", "VGStag1", "VGStag2", "Allegatr1", "Allegatr2"]
# scenarios = ["Allegatr1", "Allegatr2"]
# some global variables
height = 6 # should be 16 but I want to speed it up sire.
width = 6
RandomAgents = True
forced_random = False
num_attempts = 1


# removing Json implementatino because that was dumb and bad. back to pure script based.
if __name__ == "__main__":
    height, width, RandomAgents, forced_random, num_attempts = height, width, RandomAgents, forced_random, num_attempts

    # agents = ["HCab"]
    # agents = ["ECab199"]
    # agents = ["HCab", "ECab199"]
    agents = ["GStag"]
    # agents = ["HardHomo"]
    # curr_agents = agents[0] # just get the first entry
    scenario = "SelfPlay"
    game_type = "Round"
    graphing = True
    num_games_per_round = 10
    print_results_to_console = True

    for curr_agents in agents:
        print("Current Agent: ", curr_agents)

        scenario_type = str(curr_agents) + str(scenario) + str(game_type)

        curr_agent_name = get_agents(curr_agents, scenario)
        new_batch_logger = run_test(curr_agent_name, scenario_type, height, width, RandomAgents, forced_random, num_games_per_round, graphing, num_attempts)
        new_batch_logger.get_batch_results(print_results_to_console)
        # write_batch_results_to_file(new_batch_logger, scenario_type)



