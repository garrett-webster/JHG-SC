import json
import os
from tqdm import tqdm



from stagHare.loggingStuff.stagHareLogger import BigBatchLogger
from stagHare.visualziationTools.batchLogger import BatchLogger
from concurrent.futures import ProcessPoolExecutor, as_completed
from stagHare.runnerHelper import *  # this SHOULD be all we need.
from stagHare.visualziationTools.gameGrapher import GameGrapher
from stagHare.visualziationTools.gameLogger import information_object_to_game_logger

def run_test(curr_agent_name, scenario_type, game_type, height, width, random_agents, forced_random):

    # how many resources can we actually devote to this??
    max_workers = max(1, os.cpu_count() - 2)  # save just a few for other processes, plz don't crash.
    current_batch_logger = BigBatchLogger(height, width, curr_agent_name, scenario_type)

    # max_workers = 1 # just... just do this for rn. makes debugging a little easier.
    if game_type == "Step":
        run_function = run_trial_step
    else:
        run_function = run_trial_round

    results = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for attempt in range(num_attempts):
            futures.append(
                executor.submit(run_function, curr_agent_name, height, width, random_agents, forced_random,
                                scenario_type))

        for future in as_completed(futures):
            results.append(future.result())

        for result in results:
            pass
            # game_logger = information_object_to_game_logger(result)
            # # we should be able to do all of this
            #
            # # game_grapher = GameGrapher(result.popularity_over_time,3, curr_agent_name, scenario_type)
            # # game_grapher.playback_game(game_logger)
            # # game_grapher.create_game_graph(game_logger)
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





if __name__ == "__main__":
    file = "testToRun.json" # where we have all the stuff done
    with open(file) as f:
        data = json.load(f)  # Load the entire file as a single JSON object

    tests_list = data["tests"] # this is the object w/ all the test
    config_list = data["config"]

    height, width, RandomAgents, forced_random, num_attempts = (config_list["Height"],
                                                                config_list["Width"], config_list["RandomAgents"],
                                                                config_list["forced_random"], config_list["num_attempts"])


    for test in tqdm(tests_list):
        curr_test = data["tests"][test]
        scenario_type = curr_test["scenario_type"]
        curr_agent_name = curr_test["curr_agent_name"]
        GamesPerRound = curr_test["GamesPerRound"]
        statuses = curr_test["Status"]

        # separate status for Round and Step, check both
        for status in statuses:
            if statuses[status] == True: # skip already done statuses.
                continue
            else:
                if status == "Round":
                    game_type = run_trial_round
                elif status == "Step":
                    game_type = run_trial_step
                else:
                    game_type = None
                    print(f"Here is the status {status}")
                    break

                new_batch_logger = run_test(curr_agent_name, scenario_type, game_type, height, width, RandomAgents, forced_random)
                write_batch_results_to_file(new_batch_logger, scenario_type)
                statuses[status] = True # mark this as true when we finish.
