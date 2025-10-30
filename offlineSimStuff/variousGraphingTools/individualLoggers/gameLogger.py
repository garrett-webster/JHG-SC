import os
import json

class GameLogger():


    def __init__(self, num_players, bot_types, peep_constant, agent_name):
        self.game_data = {}
        self.jhg_sim = None
        self.sc_sim = None
        self.create_header(num_players, bot_types, peep_constant, agent_name)

    def resetup(self, jhg_sim, sc_sim):
        self.jhg_sim = jhg_sim
        self.sc_sim = sc_sim
        if self.sc_sim:
            self.game_data["SC_STUFF"] = {}
        if self.jhg_sim:
            self.game_data["JHG_STUFF"] = {}

    def create_header(self, num_players, bot_types, peep_constant, agent_name):
        self.game_data["HEADER"] = {}
        self.game_data["HEADER"]["num_players"] = num_players
        self.game_data["HEADER"]["bot_types"] = bot_types
        self.game_data["HEADER"]["peep_constant"] = peep_constant
        self.game_data["HEADER"]["agent_name"] = agent_name


    def save_game(self, played_sc, played_jhg):
        # save game is going to need a metadata header
        # needs bot types, num_players.
        if played_sc:
            self.game_data["SC_STUFF"] = self.sc_sim.get_game_deets()
        if played_jhg:
            self.game_data["JHG_STUFF"] = self.jhg_sim.get_game_deets()


    def get_game_data(self, sc_request, jhg_request):
        if sc_request:
            sc = self.game_data.get("SC_STUFF")
            (cooperation_score, avg_rise, results, results_sums, num_rounds, sums_per_round, cv, influence, utility_per_round,
             avg_utility_per_round, enforce_majority) = (self.extract_keys(sc, ["cooperation_score", "avg_rise", "results", "results_sums",
                                                              "num_rounds", "sums_per_round", "cv", "influence", "utility_per_round",
                                                              "avg_utility_per_round", "enforce_majority"]))
            return cooperation_score, avg_rise, results, results_sums, num_rounds, sums_per_round, cv, influence, utility_per_round, avg_utility_per_round, enforce_majority

        if jhg_request:
            jhg = self.game_data.get("JHG_STUFF")
            b, pops, cv, influence, pop_per_round = (self.extract_keys(jhg, ["b", "pop", "cv", "influence", "pop_per_round"]))
            return b, pops, cv, influence, pop_per_round



    def get_header(self):
        return self.game_data["HEADER"]["num_players"], self.game_data["HEADER"]["bot_types"], self.game_data["HEADER"]["peep_constant"], self.game_data["HEADER"]["agent_name"]

    def extract_keys(self, d, keys, default=None):
        return tuple(d.get(k, default) for k in keys)



    def actually_close_the_thing(self, filename):  # actually closes the thing.
        base_dir = os.path.dirname(os.path.abspath(__file__))  # gets our current location
        relative_path = os.path.join(base_dir, "gameFiles", filename + ".json")  # assembles the full file path
        os.makedirs(os.path.dirname(relative_path), exist_ok=True)  # double check that we are free to boogy

        with open(relative_path, "w") as file:  # opens and then writes the file.
            json.dump(self.game_data, file, indent=4)



