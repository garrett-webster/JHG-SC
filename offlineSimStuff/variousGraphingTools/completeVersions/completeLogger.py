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
        self.big_boy_data[curr_round]["JHG_STUFF"] = self.jhg_logger.return_round_for_writing()

    # this should close the json the way that I want it to. lets go ahead and build this into our offline version first and go from there.
    def close_json(self, filename): # not sure what to name these fetchers yet. Likely datetime again.
        print("ayo is this going off'")
        self.big_boy_data["SC_CONCLUSION"] = self.sc_logger.record_big_picture() # gets the big stuff
        self.big_boy_data["JHG_CONCLUSION"] = self.jhg_logger.record_big_picture() # TODO: Doesn't actually do anything yet.

        # in case you ever need it again, here is the code you like to use to look at where your current file path actually sends you
        relative_path = "variousGraphingTools/completeVersions/completeLogs/" + filename + ".json"
        absolute_path = os.path.abspath(relative_path)

        with open(absolute_path, "w") as file:
            json.dump(self.big_boy_data, file, indent=4)

