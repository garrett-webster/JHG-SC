import json
import os
from tqdm import tqdm

from stagHare.loggingStuff.stagHareLogger import GameInformationResultsCompiler
from concurrent.futures import ProcessPoolExecutor, as_completed
from stagHare.runnerHelper import *  # this SHOULD be all we need.
from stagHare.Simulations.sharedUtils import base_to_csv

def run_test(curr_agent_name, scenario_type, height, width, random_agents, forced_random, GamesPerRound, graphing, num_attempts, noisy=True):

    # how many resources can we actually devote to this??
    # max_workers = max(1, os.cpu_count() - 2)  # save just a few for other processes, plz don't crash.
    max_workers = 1 # spawns only a single thread, simplifying debugging.
    current_batch_logger = GameInformationResultsCompiler(height, width, curr_agent_name, scenario_type)
    results = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for attempt in range(num_attempts):
            futures.append(
                executor.submit(run_trial_all, curr_agent_name, height, width, random_agents, forced_random,
                                scenario_type, GamesPerRound, graphing, noisy))

        for future in tqdm(as_completed(futures)):
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




# base_agents = ["SCab", "HCab", "ECab99", "ECab199", "Allegatr"]
base_agents = ["Allegatr"]



scenarios = ["SelfPlay", "VGHare1", "VGHare2", "VGStag1", "VGStag2", "Allegatr1", "Allegatr2"]
# scenarios = ["Allegatr1", "Allegatr2"]
# some global variables
height = 16 # should be 16 but I want to speed it up sire.
width = 16

num_attempts = 100

def set_seed(freeze_seed, seed=0):
    if freeze_seed:
        np.random.seed(0)
        random_agents = False
        forced_random = True
    else:
        random_agents = True
        forced_random = False

    return random_agents, forced_random

# removing Json implementatino because that was dumb and bad. back to pure script based.
if __name__ == "__main__":
    height, width, num_attempts = height, width, num_attempts
    # agents = ["HCab"]
    # agents = ["ECab199"]
    # agents = ["HardHomo", "ECab3"]
    # agents = ["ECab3"]
    # agents = ["ECab3"]
    # agents = ["GStag"]

    freeze_seed = False
    random_agents, forced_random = set_seed(freeze_seed)

    agents = ["HardHomo"]
    scenario = "SelfPlay"
    game_type = "Round"
    graphing = False
    num_games_per_round = 1 # no reason to super scale it rn.
    print_results_to_console = True
    noisy = True

    for curr_agents in agents:
        print("Current Agent: ", curr_agents)

        scenario_type = str(curr_agents) + str(scenario) + str(game_type)

        curr_agent_name = get_agents(curr_agents, scenario)
        new_batch_logger = run_test(curr_agent_name, scenario_type, height, width, random_agents, forced_random, num_games_per_round, graphing, num_attempts, noisy)
        new_batch_logger.get_batch_results(print_results_to_console)
        # write_batch_results_to_file(new_batch_logger, scenario_type)



