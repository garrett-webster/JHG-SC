import copy
import random

from Server.JHGManager import JHGManager
from Server.OptionGenerators.generators import generator_factory
from Server.SCManager import SCManager
from Server.ServerConnectionManager import ServerConnectionManager
from offlineSimStuff.variousGraphingTools.completeVersions.completeLogger import CompleteLogger
import numpy as np


OPTIONS = {
    #General settings
    "NUM_HUMANS": 1,
    "TOTAL_PLAYERS": 6,
    "JHG_ROUNDS_PER_SC_ROUND" : 2, # Number of JHG rounds to play between each social choice round
    "NUM_CYCLES": 2, # Max number of JHG rounds to play. Game ends after the nth round
    "SC_GROUP_OPTION": 0, # See options_creation.py -> group_size_options to understand what this means
    "SC_VOTE_CYCLES": 3, # Number of cycles to play each social choice round. Players will vote this many times, with the nth vote being final.
    "LOGGING" : True,
    "NUM_TOKENS_PER_PLAYER": 2,
    "UTILITY_PER_PLAYER": 3,
    # TODO: MOve the utility and toekn allocation from 2 different spots server and client side and make them options that we can mess with here.

    #Misc (Wasn't sure where to put this)
    "PLAYER_ALLOCATIONS" : True,

    # Generator options
    "OPTION_GENERATOR": 2, # Defines what behavior the options generator should use. See Server.OptionsGenerators.generators for the full list
    "NOISE_MAGNITUDE": 5, # Maximum noise to add to a generated number
    "MAX_UTILITY": 10, # The max number that a utility can be. Any utility generated higher will be snapped to this number
    "MIN_UTILITY": -10, # The min number that a utility can be. Any utility generated lower will be snapped to this number
    "NUM_OPTIONS": 3
}
OPTIONS["NUM_BOTS"] =  OPTIONS["TOTAL_PLAYERS"] - OPTIONS["NUM_HUMANS"]


class Server():
    def __init__(self, options):
        self.num_players = options["TOTAL_PLAYERS"]
        self.num_humans = options["NUM_HUMANS"]
        self.num_bots = options["NUM_BOTS"]
        self.sc_group_option = options["SC_GROUP_OPTION"]
        self.jhg_rounds_per_sc_round = options["JHG_ROUNDS_PER_SC_ROUND"]
        self.num_cycles = options["NUM_CYCLES"]
        self.sc_vote_cycles = options["SC_VOTE_CYCLES"]
        self.logging = options["LOGGING"]
        self.tokens_per_player = options["NUM_TOKENS_PER_PLAYER"]
        self.utility_per_player = options["UTILITY_PER_PLAYER"]
        self.player_allocations = options["PLAYER_ALLOCATIONS"]
        self.total_order = None
        self.generator = None
        self.SC_manager = None
        self.JHG_manager = None
        self.connection_manager = None
        self.current_logger = None
        self.max_rounds = self.determine_rounds()


    def start_server(self, host='0.0.0.0', port=12345):
        self.connection_manager = ServerConnectionManager(host, port, OPTIONS["TOTAL_PLAYERS"], OPTIONS["NUM_BOTS"])

        self.total_order = self.connection_manager.get_total_list()
        print("Server started")
        # Halts execution until enough players have joined
        self.connection_manager.add_clients(OPTIONS["NUM_HUMANS"], OPTIONS["NUM_BOTS"], OPTIONS["SC_VOTE_CYCLES"], OPTIONS["NUM_TOKENS_PER_PLAYER"], OPTIONS["UTILITY_PER_PLAYER"])

        # we will get here in a minute.
        self.JHG_manager = JHGManager(self.connection_manager, self.num_humans, self.num_players, self.num_bots, self.total_order)
        self.generator = generator_factory(OPTIONS["OPTION_GENERATOR"], OPTIONS["TOTAL_PLAYERS"], OPTIONS["NOISE_MAGNITUDE"],
                                           OPTIONS["MAX_UTILITY"], OPTIONS["MIN_UTILITY"], OPTIONS["NUM_OPTIONS"],
                                           self.JHG_manager, self.connection_manager)
        self.SC_manager = SCManager(self.connection_manager, self.num_humans, self.generator, self.num_players, self.num_bots,
                                    self.sc_group_option, self.sc_vote_cycles, self.total_order)

        self.current_logger = CompleteLogger(self.SC_manager.sc_sim, self.JHG_manager.jhg_sim)


    def play_game(self):
        # Main game loop -- Play as many rounds as specified in OPTIONS

        for curr_round in range(self.max_rounds):
            is_last_jhg_round = False
            # on hte last round, fire this so it goes off twice, else, don't have it go off.
            print("this is the current round ", curr_round, " and this is the modulo ", curr_round % self.jhg_rounds_per_sc_round)
            # DO the JHG STUFF FIRST.
            if curr_round == self.max_rounds - 1: is_last_jhg_round = True
            self.JHG_manager.play_jhg_round(self.JHG_manager.current_round, is_last_jhg_round)
            self.current_logger.save_jhg_round(curr_round)
            # THEN DECIDE IF YOU NEED TO RUN AN SC ROUND.
            if (curr_round % self.jhg_rounds_per_sc_round) == self.jhg_rounds_per_sc_round -1:
                if self.player_allocations:
                    peeps, total_order_index = self.generate_peeps(self.total_order, self.JHG_manager, self.SC_manager)
                    influence_matrix = self.JHG_manager.get_influence_matrix()
                    current_options_matrix = self.SC_manager.server_side_options_matrix(peeps, influence_matrix)
                    self.SC_manager.init_next_round((current_options_matrix, total_order_index))
                else:
                    self.SC_manager.init_next_round()
                self.SC_manager.play_social_choice_round(self.JHG_manager.get_sim)
                self.current_logger.save_sc_round(curr_round)


        self.current_logger.close_json("TRIAL TRIAL TRIAL")
        print("game over")

    def generate_peeps(self, total_order, jhg_manager, sc_manager):
        popularity_array = jhg_manager.get_popularity_array(total_order)
        total = sum(popularity_array)
        # this is easy bc this will always be positive
        normalized_popularity_array = [val / total for val in popularity_array]
        # THIS IS WORSE.
        utilities_array = sc_manager.sc_sim.results_sums
        global_shift = min(0, min(utilities_array))
        # shift everything over. subtract bc its either 0 or a negative number.
        utilities_array = [val - global_shift for val in utilities_array]
        total = sum(utilities_array) # yeah override this why not.
        normalized_utility_array = [val / total if total != 0 else 1 / len(total_order) for val in utilities_array]
        # new goal -- figure out how zip works
        overall_probability_array = [(p + u) / 2 for p, u in zip(normalized_popularity_array, normalized_utility_array)]
        probabilities = np.array(overall_probability_array)
        new_world_order = np.array(total_order)
        # shoudl pull without replacement from total order using the overall probability array, gives 3 choies without replacement.
        new_peeps = np.random.choice(new_world_order, p=probabilities, size=3, replace=False)
        indexes = self.peeps_to_total_order(new_peeps, self.total_order)
        return new_peeps, indexes

    # takes in a list of peeps (player or bot or both) and returns their player indexes as per total order
    def peeps_to_total_order(self, peeps, total_order):
        indexes = []
        for peep in peeps:
            indexes.append(total_order.index(peep)+1)
        return indexes

    def determine_rounds(self):
        num_cycles = self.num_cycles
        num_games_in_cycle = self.jhg_rounds_per_sc_round
        max_rounds = num_games_in_cycle * num_cycles
        return max_rounds # for i in range this number




if __name__ == "__main__":
    server = Server(OPTIONS)
    server.start_server()
    server.play_game()