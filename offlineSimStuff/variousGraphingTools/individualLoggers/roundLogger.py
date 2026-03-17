import os
import json


class RoundLogger():
    def __init__(self):
        self.round_data = {}
        self.jhg_sim = None
        self.sc_sim = None

    def reset_up(self, jhg_sim, sc_sim):
        self.jhg_sim = jhg_sim
        self.sc_sim = sc_sim
        if self.sc_sim:
            self.round_data["SC_STUFF"] = {}
        if self.jhg_sim:
            self.round_data["JHG_STUFF"] = {}


    # just becuase we have the sim doesn't mean we have anything in it. might be smarter to save it UNDER the actual sim instead.
    def save_round(self, curr_round, played_sc, played_jhg):
        if played_sc:
            self.round_data["SC_STUFF"][curr_round] = self.sc_sim.prepare_graph()
        if played_jhg:
            self.round_data["JHG_STUFF"][curr_round] = self.jhg_sim.record_individual_round(curr_round)


    def get_round_data(self, curr_round, sc_round, jhg_round):
        if sc_round:
            sc = self.round_data["SC_STUFF"].get(curr_round)
            all_nodes, all_votes, winning_vote_list, current_options_matrix, types_list, group, curr_round, influence_matrix, results_sums, results, peeps = (
                self.extract_keys(sc, ["all_nodes", "all_votes", "winning_vote_list", "current_options_matrix", "types_list",
                                             "group", "curr_round", "influence_matrix",
                                       "results_sums", "results", "peeps"]))

            return all_nodes, all_votes, winning_vote_list, current_options_matrix, types_list, group, curr_round, influence_matrix, results_sums, results, peeps
        if jhg_round:
            jhg = self.round_data["JHG_STUFF"].get(curr_round)
            allocations, popularity, influence, old_popularity = self.extract_keys(jhg, ["T", "pop_new", "influence", "pop_old"])
            return allocations, popularity, influence, old_popularity


    def extract_keys(self, d, keys, default=None):
        return tuple(d.get(k, default) for k in keys)



    def actually_close_the_thing(self, filename):  # actually closes the thing.
        # print("do we get here ")
        base_dir = os.path.dirname(os.path.abspath(__file__))  # gets our current location
        relative_path = os.path.join(base_dir, "roundFiles", filename + ".json")  # assembles the full file path
        os.makedirs(os.path.dirname(relative_path), exist_ok=True)  # double check that we are free to boogy

        with open(relative_path, "w") as file:  # opens and then writes the file.
            json.dump(self.round_data, file, indent=4)
