import time
from collections import defaultdict

import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal
from matplotlib.axes import Axes
from pyexpat.errors import messages


class ServerListener(QObject):
    update_jhg_round_signal = pyqtSignal()
    update_sc_utillity_graph = pyqtSignal()
    update_sc_round_signal = pyqtSignal()
    enable_allocations_interface = pyqtSignal()
    disable_sc_buttons_signal = pyqtSignal()
    enable_jhg_buttons_signal = pyqtSignal()
    jhg_over_signal = pyqtSignal(bool, float)
    update_sc_votes_signal = pyqtSignal(dict, int, bool)
    update_sc_utilities_labels_signal = pyqtSignal(int, list, int, dict, list)
    update_tornado_graph_signal = pyqtSignal(Axes, list, list)
    switch_to_jhg_signal = pyqtSignal()
    update_sc_nodes_graph_signal = pyqtSignal(int, int)
    sc_create_stuff = pyqtSignal(list, list)
    update_sc_influence = pyqtSignal(list, list)


    def __init__(self, main_window, connection_manager, round_state, round_counter, token_label, allocations_label, jhg_popularity_graph, tabs):
        super().__init__()
        self.response_functions = defaultdict(lambda: self.unknown_message_type_handler, {
            "JHG_OVER": self.JHG_OVER,
            "SC_INIT": self.SC_INIT,
            "SC_OPTIONS_CREATE": self.SC_CREATE,
            "SC_VOTES": self.SC_VOTES,
            "SC_OVER": self.SC_OVER,
        })

        self.connection_manager = connection_manager
        self.round_state = round_state
        self.round_counter = round_counter
        self.main_window = main_window
        self.token_label = token_label
        self.allocations_label = allocations_label
        self.jhg_popularity_graph = jhg_popularity_graph
        self.tabs = tabs


    # Once connected to the server, this method is called on a threaded object. Once the thread calls it, it
    # continuously listens for data from the server. This is the entrance point for all functionality based on
    # receiving data from the server. Kinda a switch board of sorts
    def start_listening(self):
        time.sleep(1)
        while True:
            # Get all of the messages from the server waiting
            messages = self.connection_manager.get_message()
            for message in messages:
                # Run the appropriate function based on the message type
                try:
                    self.response_functions[message["TYPE"]](message)
                except Exception as e:
                    print(message)
                    raise e


    def JHG_OVER(self, message):
        time.sleep(0.1)
        self.round_state.influence_mat = np.array(message["INFLUENCE_MAT"])
        self.update_jhg_state(message)
        self.jhg_over_signal.emit(message["IS_LAST"], message["INIT_POP_INFLUENCE"])


    def SC_INIT(self, message):
        # self.tabs.setCurrentIndex(1)
        self.round_state.sc_round_num = message["ROUND_NUM"]
        self.round_state.options = message["OPTIONS"]
        self.round_state.captain = message["CAPTAIN"]
        # if captain mode is enabled
        if self.round_state.captain != -1:
            if self.round_state.captain != self.round_state.client_id:
                new_nodes = message["NODES"]
                for node in new_nodes:
                    if node["type"] == "PLAYER":
                        node["x_pos"] = 0.0
                        node["y_pos"] = 0.0
                self.round_state.nodes[self.round_state.sc_round_num] = new_nodes
            else: # we ARE the captain
                self.round_state.nodes[self.round_state.sc_round_num] = message["NODES"]
        else:
            self.round_state.nodes[self.round_state.sc_round_num] = message["NODES"]
        self.round_state.utilities_mat = message["UTILITIES"]



        self.update_sc_round_signal.emit()  # go ahead and adjust all the SC stuff appropriately as well.


    def SC_CREATE(self, message):
        self.round_state.captain = message["CAPTAIN"]
        self.sc_create_stuff.emit(message["CLIENT_IDS"], message["TOTAL_IDS"])
        # this actually does a lot of stuff, its just all hidden under main window.

    def SC_VOTES(self, message):
        self.round_state.current_votes = message["VOTES"]
        self.update_sc_votes_signal.emit(message["VOTES"], message["CYCLE"] + 1, message["IS_LAST_CYCLE"])


    def SC_OVER(self, message):
        print("SC OVER, GOING OFF")
        # This is the only time that the user won't switch the tab to see a round it the history tab, so it needs a little manual help.
        # if self.round_state.jhg_round_num == 1:
        winning_vote = message["WINNING_VOTE"]
        winning_vote += 1
        new_utilities = message["NEW_UTILITIES"]

        if self.round_state.captain != -1:
            new_nodes = self.round_state.nodes[self.round_state.sc_round_num]
            for node in new_nodes:
                if node["type"] == "PLAYER":
                    node["x_pos"] = 0.0
                    node["y_pos"] = 0.0
            self.round_state.nodes[self.round_state.sc_round_num] = new_nodes



        if self.main_window.round_state.captain != -1:
            current_utilities = message["UTILITIES"]
            blank_utilities = [[0, 0, 0] for _ in range(self.main_window.round_state.num_players)]
            for i in range(len(current_utilities)):
                blank_utilities[i][winning_vote-1] = current_utilities[i][winning_vote-1]
            self.main_window.sc_history_grid.update_sc_grid(message["VOTES"], blank_utilities, self.round_state.sc_round_num, winning_vote)
        else:
            self.main_window.sc_history_grid.update_sc_grid(message["VOTES"], message["UTILITIES"], self.round_state.sc_round_num, winning_vote)

        self.disable_sc_buttons_signal.emit()
        # new_utilities = message["NEW_UTILITIES"]

        # ok so what is new utilties and what we are expecting it to be
        if self.main_window.round_state.captain != -1:
            current_utilities = message["UTILITIES"]
            blank_utilities = [[0, 0, 0] for _ in range(self.main_window.round_state.num_players)]
            for i in range(len(current_utilities)):
                blank_utilities[i][winning_vote-1] = current_utilities[i][winning_vote-1]
            self.update_sc_utilities_labels_signal.emit(message["ROUND_NUM"], new_utilities, winning_vote, message["VOTES"], blank_utilities)
        else:
            self.update_sc_utilities_labels_signal.emit(message["ROUND_NUM"], new_utilities, winning_vote, message["VOTES"], message["UTILITIES"])
        #                                           int,                  dict,          int,          dict,              list

        # self.update_tornado_graph_signal.emit(self.main_window.tornado_ax, message["POSITIVE_VOTE_EFFECTS"], message["NEGATIVE_VOTE_EFFECTS"])

        self.update_sc_nodes_graph_signal.emit(winning_vote, message["ROUND_NUM"])

        self.round_state.new_utilities = new_utilities

        self.update_sc_utillity_graph.emit() # PLEASE work

        # self.update_sc_influence.emit(message["INFLUENCE_MATRIX"], message["NEW_UTILITIES"])

        # Switch to JHG
        self.switch_to_jhg_signal.emit()


    def unknown_message_type_handler(self, message):
        print(f"[Warning] Unknown message TYPE: {message.get('TYPE')}, message: {message}")


    # Prepares the client for the next round by updating self.round_state and the gui
    def update_jhg_state(self, json_data):
        time.sleep(0.1)
        self.round_state.message = json_data

        self.round_state.received = json_data["RECEIVED"]
        self.round_state.sent = json_data["SENT"]
        self.round_state.jhg_round_num = json_data["ROUND"]
        self.round_state.tokens = self.round_state.num_players * self.round_state.tokens_per_player
        self.round_state.current_popularities = json_data["POPULARITY"]
        #print("this si the new round_state.current_popularities ", self.round_state.current_popularities)
        self.jhg_popularity_graph.clear()

        self.update_jhg_round_signal.emit()

        self.round_counter.setText(f'Round {self.round_state.jhg_round_num + 1}')
        self.token_label.setText(f"Tokens: {self.round_state.tokens}")
