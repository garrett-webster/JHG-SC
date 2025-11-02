import os
import json

# Debug info

# class that contains various functions for saving stuff to jsons from old code.
from legacy.outDated.sc_tools.simLogger import simLogger
from legacy.outDated.jhg_tools.jhgLogger import JHGLogger


class CompleteLogger():
    def __init__(self):
        # so these boys need to persist so lets create em here.
        self.long_term_data = self.create_long_term_data()
        self.big_boy_data = {}  # initalize an empty dict.
        self.num_attempts = -1

    def resetup(self, jhg_sim, sc_sim):
        self.jhg_sim = jhg_sim
        self.sc_sim = sc_sim

        self.sc_logger = simLogger(self.sc_sim)
        self.jhg_logger = JHGLogger(self.jhg_sim)

    def set_attempts(self, attempts):
        self.num_attempts = attempts

    def get_attempts(self):
        return self.num_attempts

    def save_sc_round(self, curr_round, curr_logger_round):
        if curr_logger_round not in self.big_boy_data: # make sure he exists.
            self.big_boy_data[curr_logger_round] = {}

        self.big_boy_data[curr_logger_round]["SC_STUFF"] = self.sc_logger.record_individual_round()
        #print("here is self.big_boy_data at the thing ", self.big_boy_data[curr_logger_round]["SC_STUFF"]["results_sums"])

    def save_jhg_round(self, curr_round, curr_logger_round):
        if curr_logger_round not in self.big_boy_data: # make sure he exists.
            self.big_boy_data[curr_logger_round] = {}
        # new_var = self.jhg_logger.return_round_for_writing(curr_round)
        #print("this is the total size ", sys.getsizeof(new_var))

        # self.big_boy_data[curr_logger_round]["JHG_STUFF"] = self.jhg_logger.return_round_for_writing(curr_round)

    # this no longer closes the json. It grabs the concluding details and slaps them in where appropriate.
    def gather_ending_deets(self, attempt):

        if "CONCLUSION" not in self.big_boy_data:
            self.big_boy_data["CONCLUSION"] = {}

        if "SC_CONCLUSION" not in self.big_boy_data["CONCLUSION"] and self.sc_sim:
            self.big_boy_data["CONCLUSION"]["SC_CONCLUSION"] = {}
        if "JHG_CONCLUSION" not in self.big_boy_data["CONCLUSION"] and self.jhg_sim:
            self.big_boy_data["CONCLUSION"]["JHG_CONCLUSION"] = {}
        if "LONG_TERM_DATA" not in self.big_boy_data:
            self.big_boy_data["CONCLUSION"]["LONG_TERM_DATA"] = {}

        if self.sc_sim:
            self.big_boy_data["CONCLUSION"]["SC_CONCLUSION"][attempt] = self.sc_logger.record_big_picture()
        if self.jhg_sim:
            self.big_boy_data["CONCLUSION"]["JHG_CONCLUSION"][attempt] = self.jhg_logger.record_big_picture()
        self.big_boy_data["CONCLUSION"]["LONG_TERM_DATA"][attempt] = self.long_term_data # just slap that in there. just for funzies.

        self.big_boy_data["CONCLUSION"]["num_attempts"] = self.num_attempts # just go ahead and throw that in on its own. nice little dangler.
        num_players = 0
        if self.sc_sim:
            num_players = self.sc_sim.total_players
        else: # we gotta have one or the other or what are we even doing
            num_players = self.jhg_sim.total_players
        self.big_boy_data["CONCLUSION"]["num_players"] = num_players



    def actually_close_the_thing(self, filename): # actually closes the thing.
        base_dir = os.path.dirname(os.path.abspath(__file__)) # gets our current location
        relative_path = os.path.join(base_dir, "completeLogs", filename + ".json") # assembles the full file path
        os.makedirs(os.path.dirname(relative_path), exist_ok=True) # double check that we are free to boogy

        with open(relative_path, "w") as file: # opens and then writes the file.
            json.dump(self.big_boy_data, file, indent=4)



    def get_all_bot_types(self):
        sc_bot_types, allocation_bot_types, jhg_bot_types = None, None, None
        if self.sc_sim:
            sc_bot_types = self.sc_sim.bot_type
            allocation_bot_types = self.sc_sim.allocation_bot_type
        if self.jhg_sim:
            jhg_bot_types = self.jhg_sim.get_bot_types()

        return jhg_bot_types, sc_bot_types, allocation_bot_types

    def get_bot_types_from_json(self, dict):
        first_key = next(iter(dict)) # could add this in to be more robust in the future.
        sc_bot_types = dict["SC_CONCLUSION"]["0"]["bot_type"]
        allocation_bot_types = dict["SC_CONCLUSION"]["0"]["alloc_bot_type"]
        jhg_bot_types = dict["JHG_CONCLUSION"]["0"]["bot_types"]
        return jhg_bot_types, sc_bot_types, allocation_bot_types


    def get_coop_data(self):
        return self.big_boy_data["CONCLUSION"]["SC_CONCLUSION"]

    def get_jhg_cv_data(self):
        return self.big_boy_data["CONCLUSION"]["JHG_CONCLUSION"]

    # this function takes our existing long term data dict structure and condenses it to something graph-able.
    def calculate_long_term_stats(self):
        ## -- Getting average score per round and sums per player from the JHG game and SC game -- ##
        avg_pop_per_round = []
        per_player_per_round = []
        avg_utility_per_round = []
        utility_per_player_per_round = []
        # so I am not sure on the best way to do this, I think go
        if self.long_term_data["avg_pops"]:
            avg_pop_per_round, per_player_per_round = self.extract_data_from_dict(self.long_term_data["avg_pops"])
        if self.long_term_data["avg_utility"]:
            avg_utility_per_round, utility_per_player_per_round = self.extract_data_from_dict(self.long_term_data["avg_utility"])

        return avg_pop_per_round, per_player_per_round, avg_utility_per_round, utility_per_player_per_round

    def get_long_term_stats_from_dict(self, dict):
        first_key = next(iter(dict))  # get first key dynamically
        avg_pop_per_round, per_player_per_round = self.extract_data_from_dict(dict[first_key]["avg_pops"])
        avg_utility_per_round, utility_per_player_per_round = self.extract_data_from_dict(dict[first_key]["avg_utility"])
        return avg_pop_per_round, per_player_per_round, avg_utility_per_round, utility_per_player_per_round


    # so I realized that I was treating the popualrity and the utility exactly the same, so I was like "wait I can use the same function"
    # so here is a funciton that when given the data, will make the avg_per_round and avg_per_round_per_player
    def extract_data_from_dict(self, data):
        num_rounds = len(data)
        first_key = next(iter(data))
        num_players = len(data[first_key][0])
        num_attempts = len(data[first_key])

        sums_per_player = [[0 for _ in range(num_rounds)] for _ in range(num_players)]  # makes a 2d list
        # this is because sometimes when the json writes, it writes an oopsie that doesn't map the keys in order.
        round_keys = sorted(data.keys(), key=lambda x: int(x))
        round_index_map = {key: idx for idx, key in enumerate(round_keys)}

        for round_key in data:
            round_index = round_index_map[round_key]
            for attempt in data[round_key]:
                for i, player in enumerate(attempt):
                    sums_per_player[i][round_index] += player

        # now I need to normalize by attempts
        for i, score_list in enumerate(sums_per_player):
            for j, score in enumerate(score_list):
                sums_per_player[i][j] = score / num_attempts

        # sums per player stores the average score for player x at round x across all attempts. So, if [0][0] is 99, then the average score for round 1 player 1 is 99 across all attempts.
        # we can use those to graph fairly easily. now what we should do is find the average score per round
        average_score_per_round = [[] for _ in range(num_rounds)]
        for i, player in enumerate(sums_per_player):
            for i, round in enumerate(player):
                average_score_per_round[i].append(round)

        # now we gotta normalize those to be the length we expect
        for i, score_list in enumerate(average_score_per_round):
            new_average = sum(score_list) / len(score_list)
            average_score_per_round[i] = new_average

        return average_score_per_round, sums_per_player


    def create_long_term_data(self):
        long_term_data = {
            "avg_pops": {},
            "highest_pops": {},
            "avg_utility": {},
            "highest_utilities": {},
            # "coop_score": [], # look I want to
            # "cov": [],
            # maybe stick some other jhg stuff in here.
        }
        return long_term_data

    # when I wrote this, this seemed like a really cool idea. Now I hate it and it is compltely unreadable)
    def create_big_boy_graphs(self, max_rounds, offset):
        for i in range(max_rounds, 1, -1):
            curr_round = max_rounds - i # this way we start at 0 and work our way up

            if "SC_STUFF" in self.big_boy_data[curr_round + offset]:
                sc_round = self.big_boy_data[curr_round]["SC_STUFF"]["curr_round"] # saves the current SC round in the fetcher. (Creates a comprehensible dictinoary)
                self.long_term_data["avg_utility"][sc_round] = []  # trust
                self.long_term_data["highest_utilities"][sc_round] = []

                # so I think keeping the line of best fit is probably good, I think keeping the average rise is good, I think we need to try and get the coefficient of varation tho
                self.long_term_data["avg_utility"][sc_round].append(self.big_boy_data[curr_round + offset]["SC_STUFF"]["results_sums"])
                self.long_term_data["highest_utilities"][sc_round].append(max(self.big_boy_data[curr_round + offset]["SC_STUFF"]["results_sums"]))


            if "JHG_STUFF" in self.big_boy_data[curr_round + offset]: # so right now we are doing this weird thing where uhh, we have JHG thing every round. might be worth baking something in that makes it so we don't have to do that.
                self.long_term_data["avg_pops"][curr_round] = []  # creates an empty list at every round
                self.long_term_data["highest_pops"][curr_round] = []  # just make this a list, its fine

                # we need the offset to account for the fact that round 40 and round 20 are the same for long term, but very different for the logger. wraps around.
                self.long_term_data["avg_pops"][curr_round].append(self.big_boy_data[curr_round+offset]["JHG_STUFF"]["Popularity"])
                self.long_term_data["highest_pops"][curr_round].append(max(self.big_boy_data[curr_round+offset]["JHG_STUFF"]["Popularity"]))









