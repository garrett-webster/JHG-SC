import numpy as np

from Player import PlayerState
from Client.combinedLayout.JHGPlayerWidget import JHGPlayerWidget
from Client.combinedLayout.SCPlayerWidget import SCPlayerWidget

class RoundState:
    players = []
    client_id = -1 # look at JHG panel for debugging stuff.
    jhg_round_num = 0
    sc_round_num = 0

    # Stuff for jhg
    tokens = 0 # Number of tokens remaining for the current round
    allocations = [] # Represents the tokens that you will send to others
    received = [] # Each position in the list represents the number of tokens received from the player with id _
    sent = []
    popularity_over_time = []
    utility_over_time = []

    new_utilities = []


    # Stuff for sc
    # utility = 0 # total utilty
    options = []
    nodes = {}
    utilities = []
    utilities_mat = []

    def __init__(self, id, num_players, num_tokens_per_player, num_utility_per_player):
        self.captain = -1 # unless we hear anythign else, assume its a -1.
        self.num_players = num_players
        self.client_id = id
        self.tokens = num_tokens_per_player * num_players  # Number of tokens remaining for the current round
        self.utility = num_utility_per_player * num_players
        self.utility_per_player = num_utility_per_player
        self.tokens_per_player = num_tokens_per_player
        self.allocations = [0 for _ in range(num_players)]  # Represents the tokens that you will send to others
        self.received = [0 for _ in range(num_players)] # Each position in the list represents the number of tokens received from the player with id _
        self.sent = [0 for _ in range(num_players)]
        self.popularity_over_time = [100 for _ in range(num_players)]
        self.utility_over_time = [10 for _ in range(num_players)]
        self.influence_mat = np.array([[0 for _ in range(num_players)] for _ in range(num_players)])
        self.relationships_mat = np.array([[0 for _ in range(num_players)] for _ in range(num_players)])
        self.current_votes = [-1 for _ in range(num_players)]
        self.sc_cycle = None
        self.utilities = [0 for _ in range(num_players)]


        for i in range(num_players):
            self.players.append(PlayerState(i))

        self.jhg_widgets = [JHGPlayerWidget(ps) for ps in self.players]
        self.sc_widgets = [SCPlayerWidget(ps) for ps in self.players]



    def get_allocations_list(self):
        self.allocations[int(self.client_id)] = self.tokens
        return self.allocations

    def get_utilities_list(self):
        #self.utilities[int(self.client_id)] = self.utility # this was to find out self utilities. not sueful for allocations
        return self.utilities # this might have broken everything. lets find out.

    def reset_everything(self):
        self.utilities = [0 for _ in range(len(self.players))] # reset the utilities to all 0's
        self.utility = self.utility_per_player * self.num_players # resets the actual utility
        #self.allocations = [0 for _ in range(len(self.players))] # and resets the allocations back to zeros as well.
        #self.tokens = 2 * self.num_players
        for widget in self.sc_widgets:
            widget.utility_box.setText("0")
        self.tokens = self.tokens_per_player * self.num_players
        # for widget in self.jhg_widgets:
        #     widget.allocation_box.setText("0")


