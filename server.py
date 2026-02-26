import os

from Server.JHGManager import JHGManager
from Server.OptionGenerators.generators import generator_factory
from Server.SCManager import SCManager
from Server.ServerConnectionManager import ServerConnectionManager
from offlineSimStuff.runningTools.batch_tester_JHG_SC import create_game_graphs
from offlineSimStuff.variousGraphingTools.individualLoggers.roundLogger import RoundLogger
from offlineSimStuff.variousGraphingTools.individualLoggers.gameLogger import GameLogger
import numpy as np


OPTIONS = {
    #General settings
    "NUM_HUMANS": 1, # utterly fetched but can I run this headless
    "TOTAL_PLAYERS": 6,
    "JHG_ROUNDS_PER_SC_ROUND" : [2,2,2], # Number of JHG rounds to play between each social choice round
    #"JHG_ROUNDS_PER_SC_ROUND" : [4,2,2,2,2], # Number of JHG rounds to play between each social choice round
    # "JHG_ROUNDS_PER_SC_ROUND" : [4,3,3,3,3] , # Number of JHG rounds to play between each social choice round
    "SC_GROUP_OPTION": 0, # See options_creation.py -> group_size_options to understand what this means
    "SC_VOTE_CYCLES": 3, # Number of cycles to play each social choice round. Players will vote this many times, with the nth vote being final.
    "LOGGING" : True,
    "NUM_TOKENS_PER_PLAYER": 2,
    "UTILITY_PER_PLAYER": 2,
    "STARTING_UTILITY": 10,
    "CAPTAIN_MODEL": False, # just want to test something


    #Misc (Wasn't sure where to put this)
    "PLAYER_ALLOCATIONS" : True,
    "ALL_ALLOCATIONS" : True,

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
        self.sc_vote_cycles = options["SC_VOTE_CYCLES"]
        self.logging = options["LOGGING"]
        self.tokens_per_player = options["NUM_TOKENS_PER_PLAYER"]
        self.utility_per_player = options["UTILITY_PER_PLAYER"]
        self.player_allocations = options["PLAYER_ALLOCATIONS"]
        self.all_allocations = options["ALL_ALLOCATIONS"]
        self.starting_utility = options["STARTING_UTILITY"]
        self.total_order = None
        self.generator = None
        self.SC_manager = None
        self.JHG_manager = None
        self.connection_manager = None
        self.current_logger = None
        self.rounds_list = self.determine_rounds(self.jhg_rounds_per_sc_round)
        self.captain_model = options["CAPTAIN_MODEL"]


    def start_server(self, host='0.0.0.0', port=12345):
        jhg_bot_type = 0
        # addAgents = r"C:\Users\Sean\Documents\GitHub\OtherGarrettStuff\JHG-SC\Server\Engine\scenarios\workingDirectory"
        my_path = os.path.dirname(os.path.abspath(__file__))
        addAgents = os.path.join(my_path, "Server", "Engine", "scenarios", "workingDirectory")

        self.connection_manager = ServerConnectionManager(host, port, OPTIONS["TOTAL_PLAYERS"], OPTIONS["NUM_BOTS"])

        self.total_order = self.connection_manager.get_total_list()
        print("Server started")
        # Halts execution until enough players have joined
        self.connection_manager.add_clients(OPTIONS["NUM_HUMANS"], OPTIONS["NUM_BOTS"], OPTIONS["SC_VOTE_CYCLES"], OPTIONS["NUM_TOKENS_PER_PLAYER"], OPTIONS["UTILITY_PER_PLAYER"], OPTIONS["STARTING_UTILITY"], OPTIONS["ALL_ALLOCATIONS"])

        # we will get here in a minute.
        self.JHG_manager = JHGManager(self.connection_manager, self.num_humans, self.num_players, self.num_bots, self.total_order, self.tokens_per_player, jhg_bot_type, addAgents)
        self.generator = generator_factory(OPTIONS["OPTION_GENERATOR"], OPTIONS["TOTAL_PLAYERS"], OPTIONS["NOISE_MAGNITUDE"],
                                           OPTIONS["MAX_UTILITY"], OPTIONS["MIN_UTILITY"], OPTIONS["NUM_OPTIONS"],
                                           self.JHG_manager, self.connection_manager)
        self.SC_manager = SCManager(self.connection_manager, self.num_humans, self.generator, self.num_players, self.num_bots,
                                    self.sc_group_option, self.sc_vote_cycles, self.total_order, self.utility_per_player, self.JHG_manager.jhg_sim.players)

        self.round_logger = RoundLogger()
        bot_types = self.JHG_manager.jhg_sim.get_bot_types()
        self.game_logger = GameLogger(self.num_players, bot_types, 0, "")
        self.round_logger.reset_up(self.JHG_manager.jhg_sim, self.SC_manager.sc_sim)
        self.game_logger.resetup(self.JHG_manager.jhg_sim, self.SC_manager.sc_sim)


    def play_game(self):
        sc_sim = self.SC_manager.sc_sim
        jhg_sim = self.JHG_manager.jhg_sim
        round_list = self.rounds_list

        sc_sim.set_group("") # just a null setting
        played_sc = False
        played_jhg = False
        curr_sc_round = 0
        influence_matrix = None

        for list_index in (range(0, len(round_list))):
            sc_rounds = round_list[list_index][-1] == "*"
            jhg_rounds = round_list[list_index][-1] == "-"
            is_last_jhg_round = False
            if list_index + 1 < len(self.rounds_list) and self.rounds_list[list_index + 1]:
                if self.rounds_list[list_index + 1][-1] == "*":
                    is_last_jhg_round = True


            curr_round = int(round_list[list_index][:-1])

            if jhg_rounds: # this SHOULD be it. fingers crossed.
                influence_matrix = self.JHG_manager.play_jhg_round(curr_round, is_last_jhg_round)
                played_jhg = True

            if sc_rounds: # lets be so real no allocations aren't THAT interesting.
                possible_peeps, indexes = self.generate_peeps(self.total_order, jhg_sim, sc_sim)
                self.highest_pop_player = self.JHG_manager.get_highest_popularity_player()
                self.SC_manager.play_sc_round(influence_matrix, possible_peeps, curr_round, curr_sc_round, indexes, self.captain_model, self.highest_pop_player)
                curr_sc_round += 1
                played_sc = True


            self.round_logger.save_round(curr_round, sc_rounds, jhg_rounds)
            # create_round_graphs(self.round_logger, curr_round, sc_rounds, jhg_rounds)

        self.game_logger.save_game(played_sc, played_jhg)
        create_game_graphs(self.game_logger)
        self.round_logger.actually_close_the_thing("noLongerFetched")
        self.game_logger.actually_close_the_thing("noLongerFetched")
        print("GAME OVER")
        # time.sleep(5) # just give it a little while before it closes the connection so the client can update


    def generate_peeps(self, total_order, jhg_sim, sc_sim):
        popularity_array = (jhg_sim.get_popularities())  # huh
        total = sum(popularity_array)
        # this is easy bc this will always be positive
        normalized_popularity_array = [val / total for val in popularity_array]
        # THIS IS WORSE.
        utilities_array = sc_sim.results_sums
        global_shift = min(0, min(utilities_array))
        # shift everything over. subtract bc its either 0 or a negative number.
        utilities_array = [val - global_shift for val in utilities_array]
        total = sum(utilities_array)  # yeah override this why not.
        normalized_utility_array = [val / total if total != 0 else 1 / len(total_order) for val in utilities_array]
        # new goal -- figure out how zip works
        overall_probability_array = [(p + u) / 2 for p, u in zip(normalized_popularity_array, normalized_utility_array)]
        probabilities = np.array(overall_probability_array)
        new_world_order = np.array(total_order)
        # shoudl pull without replacement from total order using the overall probability array, gives 3 choies without replacement.
        new_peeps = np.random.choice(new_world_order, p=probabilities, size=3, replace=False)
        indexes = self.peeps_to_total_order(new_peeps, total_order)
        return new_peeps, indexes

    # takes in a list of peeps (player or bot or both) and returns their player indexes as per total order
    def peeps_to_total_order(self, peeps, total_order):
        indexes = []
        for peep in peeps:
            indexes.append(total_order.index(peep)+1)
        return indexes


    # updated new and improved version ig.
    def determine_rounds(self, jhg_rounds_per_sc_game_list):
        new_list = []  # WHEEE gotta start somewhere
        if jhg_rounds_per_sc_game_list[0] == "J" or jhg_rounds_per_sc_game_list[0] == "S":
            print("engaging pure opertaiopns, standing by")
            if jhg_rounds_per_sc_game_list[0] == "J":
                num_rounds = int(jhg_rounds_per_sc_game_list[
                                     -1])  # possibly one of the jankier lines that I have ever written but here we are
                for i in range(num_rounds):
                    new_list.append(str(i) + "-")

            if jhg_rounds_per_sc_game_list[0] == "S":
                num_rounds = int(jhg_rounds_per_sc_game_list[-1])
                for i in range(num_rounds):
                    new_list.append(str(i) + "*")


        else:
            new_list = []
            current = 0  # Tracks number for "-" entries
            for instance in jhg_rounds_per_sc_game_list:
                for _ in range(instance):
                    new_list.append(f"{current}-")
                    current += 1
                new_list.append(f"{current - 1}*")  # Append the last "-" number with "*"

        return new_list

    def reconcile_influence(self, jhg_influence, sc_influence):

        # ok this fetcher uses convex recombination to put the two together and then uses the frobenius norm to decide on the magnitude to adjust back too. bars!
        alpha = 0.5  # THIS iS JUST A STARTER VALUE, WILL LIKELY BE MADE INTO A GENE OR WHATEVER.
        if sc_influence is None:
            print("something wrong :(")
            return jhg_influence

        sc_influence = np.array(sc_influence)
        jhg_influence = np.array(jhg_influence)  # This shbould never get used but it couldn't hurt

        jhg_norm = np.linalg.norm(jhg_influence, 'fro')

        combined = (1 - alpha) * jhg_influence + alpha * sc_influence

        combined_norm = np.linalg.norm(combined, 'fro')
        if combined_norm == 0:
            return np.zeros_like(jhg_influence)

        rescaled = combined * (jhg_norm / combined_norm)
        return rescaled


if __name__ == "__main__":
    server = Server(OPTIONS)
    server.start_server()
    server.play_game()