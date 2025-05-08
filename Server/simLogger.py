import json
import os
from pathlib import Path

class simLogger:
    def __init__(self, current_sim):
        self.sim = current_sim

    def record_individual_round(self):
        all_nodes, all_votes, winning_vote, current_options_matrix, bot_list, scenario, group, curr_round, cycle = self.sim.prepare_graph()
        total_data = {}
        total_data["bot_list"] = bot_list
        total_data["all_nodes"] = all_nodes
        total_data["all_votes"] = all_votes
        total_data["winning_vote"] = winning_vote
        total_data["current_options_matrix"] = current_options_matrix
        total_data["scenario"] = scenario
        total_data["group"] = group
        total_data["curr_round"] = curr_round
        total_data["cycle"] = cycle
        my_path = os.path.dirname(os.path.abspath(__file__))
        filename = "logs_repo/individual_round/" + " scenario" + str(scenario) + "groups" + str(group) + "round" + str(
            curr_round) + "cycle" + str(cycle) + ".json"
        file_path = os.path.join(my_path, filename)

        with open(file_path, "w") as file:
            json.dump(total_data, file, indent=4)

    def record_big_picture(self):
        results, cooperation_score, bot_type, num_rounds, scenario, group = self.sim.get_results()
        total_data = {}
        total_data["results"] = results
        total_data["cooperation_score"] = cooperation_score
        total_data["bot_type"] = bot_type
        total_data["num_rounds"] = num_rounds
        my_path = os.path.dirname(os.path.abspath(__file__))
        filename = "logs_repo/big_picture/" + " scenario" + str(scenario) + "groups" + str(group) + ".json"
        file_path = os.path.join(my_path, filename)

        with open(file_path, "w") as file:
            json.dump(total_data, file, indent=4)


    def record_round(self): # this saves everything. I don't know why you would want this, it was mroe of a proof of concept type beat.
        (current_node_json, final_votes, winning_vote,
         current_options_matrix, results,
         cooperation_score, bot_type, num_rounds,
         scenario, group, cycle, curr_round) = self.sim.get_everything_for_logger()
        scenario = Path(scenario).name

        total_data = {}
        total_data["scenario"] = scenario
        total_data["group"] = group
        total_data["cooperation_score"] = cooperation_score
        total_data["bot_type"] = bot_type
        total_data["num_rounds"] = num_rounds
        total_data["winning_vote"] = winning_vote
        total_data["current_options_matrix"] = current_options_matrix
        total_data["all_nodes"] = current_node_json
        total_data["final_votes"] = final_votes
        total_data["results"] = results

        my_path = os.path.dirname(os.path.abspath(__file__))
        filename = "logs_repo/test/" + " scenario" + str(scenario) + "groups" + str(group) + "round" + str(curr_round) + "cycle" + str(cycle) + ".json"
        file_path = os.path.join(my_path, filename)

        with open(file_path, "w") as file:
            json.dump(total_data, file, indent=4)


