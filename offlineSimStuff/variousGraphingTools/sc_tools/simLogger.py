import json
import os
from pathlib import Path
import copy
import numpy as np

class simLogger:
    def __init__(self, current_sim=None):
        self.sim = current_sim
        self.big_boy_data = {}

    def record_individual_round(self):
        all_nodes, all_votes, winning_vote_list, current_options_matrix, types_list, scenario, group, curr_round, cycle, chromosome = self.sim.prepare_graph()
        total_data = {}
        total_data["types_list"] = types_list
        total_data["all_nodes"] = all_nodes
        new_votes = copy.deepcopy(all_votes)
        total_data["all_votes"] = new_votes
        total_data["winning_vote"] = winning_vote_list
        total_data["current_options_matrix"] = current_options_matrix
        total_data["scenario"] = scenario
        total_data["group"] = group
        total_data["curr_round"] = curr_round
        total_data["cycle"] = cycle
        total_data["chromosome"] = chromosome

        return total_data
        # my_path = os.path.dirname(os.path.abspath(__file__))
        # filename = "sc_logs_repo/individual_round/" + " scenario" + str(scenario) + "groups" + str(group) + "round" + str(
        #     curr_round) + "cycle" + str(cycle) + "chromosome" + str(chromosome) + ".json"
        # file_path = os.path.join(my_path, filename)
        #
        # with open(file_path, "w") as file:
        #     json.dump(total_data, file, indent=4)

    def record_big_picture(self):
        results, cooperation_score, bot_type, num_rounds, scenario, group, chromosome = self.sim.get_results()
        total_data = {}
        total_data["results"] = results
        total_data["cooperation_score"] = cooperation_score
        total_data["bot_type"] = bot_type
        total_data["num_rounds"] = num_rounds
        total_data["scenario"] = scenario
        total_data["group"] = group
        total_data["chromosome"] = chromosome
        return total_data

        # my_path = os.path.dirname(os.path.abspath(__file__))
        # filename = "sc_logs_repo/big_picture/" + " scenario" + str(scenario) + "groups" + str(group) + "chromosome" + str(chromosome) + ".json"
        # file_path = os.path.join(my_path, filename)
        #
        # with open(file_path, "w") as file:
        #     json.dump(total_data, file, indent=4)


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

        return total_data

        # my_path = os.path.dirname(os.path.abspath(__file__))
        # filename = "sc_logs_repo/test/" + " scenario" + str(scenario) + "groups" + str(group) + "round" + str(curr_round) + "cycle" + str(cycle) + ".json"
        # file_path = os.path.join(my_path, filename)
        #
        # with open(file_path, "w") as file:
        #     json.dump(total_data, file, indent=4)

    def add_round_to_sim(self, round_num):
        #print("This is the round number that we are adding ", round_num)
        self.big_boy_data[round_num] = self.record_individual_round()

    def finish_json(self, filename):
        self.big_boy_data["Conclusion"] = self.record_big_picture()
        self.write_a_json_to_file(self.big_boy_data)
        file_path = "../../sc_logs_repo/"
        file_path += filename + ".json"
        my_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(my_path, file_path)
        with open(file_path, "w") as file:
            json.dump(self.big_boy_data, file, indent=4)



    def log_stuff_for_chromosome(self, big_boy_json):
        results, cooperation_score, bot_type, num_rounds, scenario, group, chromosome = self.sim.get_results()
        sums_per_round = {}
        for bot in results:
            sums_per_round[bot] = []
            current_sum = 0
            for i, new_sum in enumerate(results[bot]):
                current_sum += new_sum
                sums_per_round[bot].append(current_sum)

        new_list = []
        for bot in sums_per_round:
            new_list.append(sums_per_round[bot][num_rounds - 1])
        std = np.std(new_list)
        mean = np.mean(new_list)
        cv = std / abs(mean)  # measures distribution bet  ter than, say, std or mean on their own.

        # Prepare the x-axis (rounds)
        rounds = range(num_rounds)  # just generates a list so we can zip with it later

        # total score per round (for the black line)
        total_scores_per_round = [sum(results[player][round_num] for player in results) for round_num in rounds]

        # average score per round, by using the total score and num playres.
        num_players = len(results)  # Number of players (bots)
        average_scores_per_round = [total_score / num_players for total_score in total_scores_per_round]

        # cum average score and total score increase
        cumulative_average_score = [sum(average_scores_per_round[:i + 1]) for i in range(len(average_scores_per_round))]
        total_average_increase = cumulative_average_score[-1] / num_rounds
        json_to_write = {}
        json_to_write["total_average_increase"] = total_average_increase
        json_to_write["cooperation_score"] = cooperation_score
        json_to_write["cv"] = cv
        big_boy_json[chromosome] = json_to_write


    def write_a_json_to_file(self, big_boy_json):
        my_path = os.path.dirname(os.path.abspath(__file__))
        directory_name = "chromosomeResults"
        file_name = "chromosomeLoggingTime.txt"  # Add .json to indicate it's a file

        directory_path = os.path.join(my_path, directory_name)
        os.makedirs(directory_path, exist_ok=True)

        file_path = os.path.join(directory_path, file_name)
        with open(file_path, "w") as file:
            json.dump(big_boy_json, file, indent=4)