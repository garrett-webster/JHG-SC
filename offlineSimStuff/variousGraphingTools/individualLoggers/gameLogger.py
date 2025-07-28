
class GameLogger():


    def __init__(self, num_players, gen_number):
        self.game_data = {}
        self.jhg_sim = None
        self.sc_sim = None
        self.create_header(num_players, gen_number)

    def resetup(self, jhg_sim, sc_sim):
        self.jhg_sim = jhg_sim
        self.sc_sim = sc_sim
        if self.sc_sim:
            self.game_data["SC_STUFF"] = {}
        if self.jhg_sim:
            self.game_data["JHG_STUFF"] = {}

    def create_header(self, num_players, gen_number):
        self.game_data["HEADER"] = {}
        self.game_data["HEADER"] = num_players, gen_number # might not need


    def save_game(self):
        # save game is going to need a metadata header
        # needs bot types, num_players.
        if self.sc_sim:
            self.game_data["SC_STUFF"] = self.sc_sim.get_game_deets()
        if self.jhg_sim:
            self.game_data["JHG_STUFF"] = self.jhg_sim.get_game_deets()


    def get_game_data(self, sc_request, jhg_request):
        if sc_request:
            sc = self.game_data.get("SC_STUFF")
            (cooperation_score, avg_rise, results, results_sums, num_rounds, sums_per_round, cv, influence, utility_per_round,
             avg_utility_per_round) = (self.extract_keys(sc, ["cooperation_score", "avg_rise", "results", "results_sums",
                                                              "num_rounds", "sums_per_round", "cv", "influence", "utility_per_round",
                                                              "avg_utility_per_round"]))
            return cooperation_score, avg_rise, results, results_sums, num_rounds, sums_per_round, cv, influence, utility_per_round, avg_utility_per_round

        if jhg_request:
            jhg = self.game_data.get("JHG_STUFF")
            b, pops, cv, influence, pop_per_round = (self.extract_keys(jhg, ["b", "pop", "cv", "influence", "pop_per_round"]))
            return b, pops, cv, influence, pop_per_round



    def get_header(self):
        return self.game_data["HEADER"]

    def extract_keys(self, d, keys, default=None):
        return tuple(d.get(k, default) for k in keys)



