import os
import json

# class that contains various functions for saving stuff to jsons from old code.
from offlineSimStuff.variousGraphingTools.sc_tools.simLogger import simLogger
from offlineSimStuff.variousGraphingTools.jhg_tools.jhgLogger import JHGLogger

class CompleteLogger():
    def __init__(self, sc_sim, jhg_sim):
        self.jhg_sim = jhg_sim
        self.sc_sim = sc_sim
        self.big_boy_data = {} # initalize an empty dict.
        self.sc_logger = simLogger(self.sc_sim)
        self.jhg_logger = JHGLogger(self.jhg_sim)

    def save_sc_round(self, curr_round):
        if curr_round not in self.big_boy_data: # make sure he exists.
            self.big_boy_data[curr_round] = {}
        self.big_boy_data[curr_round]["SC_STUFF"] = self.sc_logger.record_individual_round()

    def save_jhg_round(self, curr_round):
        if curr_round not in self.big_boy_data: # make sure he exists.
            self.big_boy_data[curr_round] = {}
        self.big_boy_data[curr_round]["JHG_STUFF"] = self.jhg_logger.return_round_for_writing(curr_round)

    # this should close the json the way that I want it to. lets go ahead and build this into our offline version first and go from there.
    def close_json(self, filename):
        self.big_boy_data["SC_CONCLUSION"] = self.sc_logger.record_big_picture()

        # Get the directory of the current file (this script)
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Build the full path
        relative_path = os.path.join(base_dir, "completeLogs", filename + ".json")

        # Make sure the folder exists
        os.makedirs(os.path.dirname(relative_path), exist_ok=True)

        with open(relative_path, "w") as file:
            json.dump(self.big_boy_data, file, indent=4)

