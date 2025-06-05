from Server.JHGManager import JHGManager
from Server.OptionGenerators.generators import generator_factory
from Server.SCManager import SCManager
from Server.ServerConnectionManager import ServerConnectionManager

OPTIONS = {
    #General settings
    "NUM_HUMANS": 1,
    "TOTAL_PLAYERS": 11,
    "JHG_ROUNDS_PER_SC_ROUND" : 1, # Number of JHG rounds to play between each social choice round
    "MAX_ROUNDS": 10, # Max number of JHG rounds to play. Game ends after the nth round
    "SC_GROUP_OPTION": 0, # See options_creation.py -> group_size_options to understand what this means
    "SC_VOTE_CYCLES": 3, # Number of cycles to play each social choice round. Players will vote this many times, with the nth vote being final.
    "JHG_LOGGING": False,
    "SC_LOGGING": True,

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
        self.max_rounds = options["MAX_ROUNDS"]
        self.sc_vote_cycles = options["SC_VOTE_CYCLES"]
        self.SC_logging = options["SC_LOGGING"]
        self.JHG_logging = options["JHG_LOGGING"]
        self.total_order = None
        self.generator = None
        self.SC_manager = None
        self.JHG_manager = None
        self.connection_manager = None


    def start_server(self, host='0.0.0.0', port=12346):
        self.connection_manager = ServerConnectionManager(host, port, OPTIONS["TOTAL_PLAYERS"], OPTIONS["NUM_BOTS"])
        self.total_order = self.connection_manager.get_total_list()
        print("Server started")
        # Halts execution until enough players have joined
        self.connection_manager.add_clients(OPTIONS["NUM_HUMANS"], OPTIONS["NUM_BOTS"], OPTIONS["SC_VOTE_CYCLES"])


        self.JHG_manager = JHGManager(self.connection_manager, self.num_humans, self.num_players, self.num_bots,
                                      self.JHG_logging, self.total_order)
        self.generator = generator_factory(OPTIONS["OPTION_GENERATOR"], OPTIONS["TOTAL_PLAYERS"], OPTIONS["NOISE_MAGNITUDE"],
                                           OPTIONS["MAX_UTILITY"], OPTIONS["MIN_UTILITY"], OPTIONS["NUM_OPTIONS"],
                                           self.JHG_manager, self.connection_manager)
        self.SC_manager = SCManager(self.connection_manager, self.num_humans, self.generator, self.num_players, self.num_bots,
                                    self.sc_group_option, self.sc_vote_cycles, self.SC_logging, self.total_order)


    def play_game(self):
        # Main game loop -- Play as many rounds as specified in OPTIONS
        self.SC_manager.init_next_round()
        while self.JHG_manager.current_round <= self.max_rounds:
            is_last_jhg_round = False
            for i in range(self.jhg_rounds_per_sc_round): # This range says how many jhg rounds to play between sc rounds
                if i == self.jhg_rounds_per_sc_round - 1: is_last_jhg_round = True
                self.JHG_manager.play_jhg_round(self.JHG_manager.current_round, is_last_jhg_round)
            self.SC_manager.play_social_choice_round()
        self.JHG_manager.log_jhg_overview()

        print("game over")


if __name__ == "__main__":
    server = Server(OPTIONS)
    server.start_server()
    server.play_game()