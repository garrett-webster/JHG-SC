import copy
import time
from functools import partial

import numpy as np
from PyQt6.QtCore import QThread
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import QMainWindow, QHBoxLayout, QLabel, QWidget, QPushButton

from Client.RoundState import RoundState
from Client.ServerListener import ServerListener
from matplotlib.figure import Figure

from Client.combinedLayout.JHGPlayerWidget import JHGPlayerWidget
from Client.combinedLayout.JhgPanel import JhgPanel
from Client.combinedLayout.JhgTornadoGraph import JhgTornadoGraph
from Client.combinedLayout.JhgVotingPanel import JhgVotingPanel

from Client.combinedLayout.SCHistoryGrid import SCHistoryGrid

from Client.combinedLayout.MainDocks import CornerContainer
from Client.combinedLayout.SCCausesGraph import SCCausesGraph
from Client.combinedLayout.SCPlayerWidget import SCPlayerWidget
from Client.combinedLayout.ui_functions.SC_functions import *
from Client.combinedLayout.ui_functions.JHG_functions import *
from Client.combinedLayout.SC_Allocations_Grapher import SC_Allocations_Grapher

from Client.combinedLayout.sc_tornado_graph import update_sc_tornado_graph
from Client.combinedLayout.SCInfluenceGrapher import update_sc_network_graph


class MainWindow(QMainWindow):
    def __init__(self, connection_manager, num_players, client_id, num_cycles, num_tokens_per_player, utility_per_player, starting_utility, all_allocations):
        super().__init__()
        # This window is very dependent on things happening in the correct order.
        # If you mess with it, you might break a lot of things.
        # It has been broken up into blocks below to try to mitigate that

        # 1# Block one: Sets up the round_state and client socket. Must be the first thing done
        self.tornado_ax = None
        self.tornado_canvas = None
        self.SC_cause_graph = SCCausesGraph(num_cycles)
        self.player_labels = {}
        self.jhg_buttons = []
        self.sc_buttons = []
        self.num_players = num_players
        self.round_state = RoundState(client_id, num_players, num_tokens_per_player, utility_per_player)
        self.connection_manager = connection_manager
        self.num_cycles = num_cycles
        self.starting_util = starting_utility
        self.all_allocations = all_allocations



        # /1#

        # 2# Block two: Creates the elements that will be passed to the server listener for dynamic updating. Must happen before the server listener is created
        self.setWindowTitle(f"Junior High Game: Player {int(self.round_state.client_id) + 1}")

        # Dynamically updated elements
        self.token_label = QLabel()
        self.sc_allocations_label = QLabel()
        self.jhg_popularity_graph = pg.PlotWidget()

        self.jhg_popularity_graph.setXRange(0, 2)
        self.jhg_popularity_graph.setYRange(0, 120)
        self.jhg_popularity_graph.getAxis('bottom').setTicks(
            [[(i, str(i)) for i in range(100)]])
        self.jhg_popularity_graph.setBackground("#282828ff")
        view_box = self.jhg_popularity_graph.getViewBox()
        view_box.setLimits(xMin=0, xMax=2, yMin=0, yMax=120)
        self.jhg_network = pg.PlotWidget()
        self.jhg_network.setBackground("#282828ff")
        tabs = QTabWidget()

        # Initialize the social choice panel. This includes defining several variables that will be initialized in SC_functions
        self.tornado_fig = Figure(figsize=(5, 4), dpi=100)
        self.tornado_y = np.arange(self.round_state.num_players)
        self.tornado_ax = self.tornado_fig.add_subplot(111)

        # The QLabels used to display the utility values of each choice in the social choice game
        self.utility_qlabels = []
        self.SC_voting_grid = QTabWidget()
        self.cause_table = QWidget()

        self.sc_influence = pg.PlotWidget() # just so we have it
        self.sc_influence.setBackground("#282828ff") # same as the above.

        # Header for JHG tab
        self.headerLayout = QHBoxLayout()
        self.round_counter = QLabel("Round 1")
        self.round_counter_font = QFont()
        self.round_counter_font.setPointSize(20)
        self.round_counter.setFont(self.round_counter_font)
        self.headerLayout.addWidget(self.round_counter)
        # /2#

        # 3# Block three: Sets up the server listener, which depends on blocks 1&2.
        # Server Listener setup
        self.ServerListener = ServerListener(self, connection_manager, self.round_state, self.round_counter,
                                             self.token_label, self.sc_allocations_label,
                                             self.jhg_popularity_graph, tabs)
        self.ServerListener_thread = QThread()
        self.ServerListener.moveToThread(self.ServerListener_thread)

        self.set_up_signals()

        self.ServerListener_thread.start()
        # /3#

        # 4# Block four: Lays out the client. Dependent on blocks 1&2
        self.JHG_panel = QWidget()
        self.JHG_panel.setMinimumWidth(400)
        self.JHG_panel.setMinimumHeight(2400)
        round_state = self.round_state
        self.JHG_panel.setLayout(JhgPanel(round_state, connection_manager, self.token_label,
                                          self.jhg_popularity_graph, self.jhg_network, self.jhg_buttons))
        self.JHG_panel.setObjectName("JHG_Panel")
        self.JHG_panel.setProperty("min-height", 80 + 40 * self.round_state.num_players)


        self.JHG_tornado_graph = JhgTornadoGraph(num_players)

        plots_panel = QTabWidget()
        plots_panel.tabBar().setExpanding(True)
        plots_panel.addTab(self.jhg_popularity_graph, "Popularity over time")
        plots_panel.addTab(self.jhg_network, "Network graph")
        plots_panel.addTab(self.JHG_tornado_graph, "Tornado Graph")



        self.SC_panel = QTabWidget()
        self.SC_panel.setObjectName("SC_Panel")
        self.SC_panel.setProperty("min-height", 200 + 20 * self.round_state.num_players)
        self.SC_panel.setLayout(QVBoxLayout())

        create_sc_ui_elements(self)
        self.SC_cause_graph.init_sc_nodes_graph(self.round_state)

        self.sc_utility_graph = pg.PlotWidget()

        self.sc_utility_graph.setXRange(0, 2)
        self.sc_utility_graph.setYRange(0, 120)
        self.sc_utility_graph.getAxis('bottom').setTicks(
            [[(i, str(i)) for i in range(10)]])
        self.sc_utility_graph.setBackground("#282828ff")
        view_box = self.sc_utility_graph.getViewBox()
        view_box.setLimits(xMin=0, xMax=2, yMin=0, yMax=12)

        graphs_layout = QVBoxLayout()

        sc_graph_tabs = QTabWidget()
        sc_graph_tabs.addTab(self.SC_cause_graph, "Causes Graph")
        sc_graph_tabs.addTab(self.tornado_canvas, "Effect of past votes")
        sc_graph_tabs.addTab(self.sc_influence, "Influence Graph") # not running yet but should! appear.
        sc_graph_tabs.addTab(self.sc_utility_graph, "Util Graph")

        graphs_layout.addWidget(sc_graph_tabs)

        self.sc_history_grid = SCHistoryGrid(self.round_state.num_players, self.round_state.client_id, "Voted for",
                                             self.SC_cause_graph)
        self.SC_panel.addTab(self.sc_history_grid, "History")

        self.SC_panel.currentChanged.connect(self.SC_tab_changed)
        self.SC_creations_panel = ScCreationPanel(self.round_state, self.connection_manager, self.sc_allocations_label,
                                                  self.sc_buttons)
        self.attach_sc_buttons() #no longer does waht we want it to do, no gurantee of 3 diemsinons, scrapping that whole thing.
        self.SC_panel.addTab(self.SC_creations_panel, "Allocations")
        self.SC_panel.setTabVisible(2, False)  # disable the tab unless you need it
        self.SC_panel.setCurrentIndex(1)

        self.SC_Allocations_grapher = SC_Allocations_Grapher(self.round_state.client_id) # idc how tempting it is do NOT throw main window in here.

        self.dockWidget = CornerContainer(self.JHG_panel, plots_panel, self.SC_panel, sc_graph_tabs)

        self.setWindowTitle("JHG: Round 1")
        self.setCentralWidget(self.dockWidget)
        #self.SC_cause_graph.update_sc_nodes_given_allocations.connect(self.SC_Allocations_grapher.create_graph())

    # /4#

    ### --- Setting up pyqt signals --- ###

    def set_up_signals(self):
        # pyqt signal hook-ups
        self.ServerListener.update_jhg_round_signal.connect(partial(update_jhg_ui_elements, self))
        self.ServerListener.update_sc_utillity_graph.connect(partial(update_sc_ui_elements, self))
        self.ServerListener.update_sc_round_signal.connect(partial(SC_round_init, self))
        self.ServerListener.enable_allocations_interface.connect(partial(self.enable_allocations_interface))
        self.ServerListener.disable_sc_buttons_signal.connect(partial(disable_sc_buttons, self))
        self.ServerListener.update_sc_utilities_labels_signal.connect(self.update_sc_utilities_labels)
        self.ServerListener.update_tornado_graph_signal.connect(self.update_tornado_graph)
        self.ServerListener.jhg_over_signal.connect(self.jhg_over)
        self.ServerListener.update_sc_votes_signal.connect(self.update_sc_votes)
        self.ServerListener.update_sc_nodes_graph_signal.connect(self.update_sc_nodes_graph)
        self.ServerListener.switch_to_jhg_signal.connect(self.start_jhg_round)
        self.ServerListener_thread.started.connect(self.ServerListener.start_listening)
        #self.ServerListener.disable_jhg_buttons_signal.connect(self.disable_jhg_buttons)
        self.ServerListener.sc_create_stuff.connect(self.sc_create_allocations)
        self.ServerListener.update_sc_influence.connect(self.sc_update_influence)

    def update_sc_votes(self, votes, cycle, is_last_cycle):
        self.round_state.sc_cycle = cycle
        # print("here are hte votes when it crashes ", votes, " bc cycle doesn't appear to be an issue")
        time.sleep(0.1)
        self.SC_cause_graph.update_arrows(votes, True)
        self.SC_voting_grid.set_selected_button_style_to_border()


        if not is_last_cycle:
            self.SC_voting_grid.submit_button.setText("Submit")
            self.dockWidget.bottom_left.start_flashing(4)
        else:
            self.SC_voting_grid.current_vote = -1
            self.SC_voting_grid.select_button(None)  # Clears the selection from the SC voting buttons

        if self.round_state.captain != -1 and self.round_state.captain != self.round_state.client_id:
            time.sleep(0.5) # should wait and then throw back a vote.
            self.connection_manager.send_message("SUBMIT_SC", self.round_state.client_id,
                                                        self.SC_voting_grid.current_vote)


    def update_sc_utilities_labels(self, round_num, new_utilities, winning_vote, last_round_votes,
                                   last_round_utilities):
        update_sc_utilities_labels(self, round_num, new_utilities, winning_vote, last_round_votes, last_round_utilities)

    def update_tornado_graph(self, tornado_ax, positive_vote_effects, negative_vote_effects):
        update_sc_tornado_graph(self, tornado_ax, positive_vote_effects, negative_vote_effects)

    def update_sc_nodes_graph(self, winning_vote, round_num):
        self.sc_history_grid.winning_vote = winning_vote
        self.SC_cause_graph.update_arrows(self.round_state.current_votes)
        self.round_state.current_votes = {i: -1 for i in range(self.round_state.num_players)}
        self.sc_history_grid.winning_vote = winning_vote

    def SC_tab_changed(self, index):
        try:
            tab_changed(self, index)
        except AttributeError:
            pass # just tired of the red text that happens sometimes.

    def start_jhg_round(self):
        self.enable_jhg_buttons(self.JHG_panel)
        start_jhg_round(self)

    def jhg_over(self, is_last, init_pop_influence):
        time.sleep(0.1)
        #self.disable_jhg_buttons(self.JHG_panel) Try not putting that there, let it get cancelled somewhere else.
        jhg_over(self, is_last, init_pop_influence)
        self.round_state.utilities = [0 for _ in range(self.round_state.num_players)] # reset this bc this isn't happening quick enough.
        #self.SC_panel.setCurrentIndex(0)  # don't move them there now, sometimes this doesn't do what we wnat it to do.
        # self.update_sc_graph() # hard coding this bc I want to see somethign real quick.

    def enable_allocations_interface(self):
        self.sc_buttons[0].setText("Submit")
        self.SC_panel.setTabVisible(2, True)  # shoudl now enable it for those that need it.
        self.SC_panel.setCurrentIndex(2) # should force the third tab to open.
        self.SC_panel.setTabEnabled(0, False) # make sure they HAVE to allocate before they can vote.
        new_nodes = self.SC_Allocations_grapher.create_graph(self.round_state.get_utilities_list()) # should be all 0's. s
        self.SC_cause_graph.draw_allocations_graph(new_nodes)

    def disable_jhg_buttons(self, panel):
        panel.setEnabled(False)
        for button in self.jhg_buttons:
            if button.objectName() == "JHGSubmitButton":
                button.setText("Submit")
            button.setEnabled(False) # don't turn him on but like set the text appropraitely.

    def enable_jhg_buttons(self, panel):
        panel.setEnabled(True)
        self.SC_voting_grid.submit_button.setText("Submit")

    def change_cause_labels(self, total_ids):
        new_total_ids = copy.deepcopy(total_ids)
        for i, button in enumerate(self.SC_voting_grid.buttons):
            if button.text().startswith("Cause"):
                button.setText("Cause " + str(i+1) + " (" + str(new_total_ids.pop(0)+1) + ")")

    def update_sc_graph(self):
        new_arrows = self.SC_Allocations_grapher.create_arrows(self.round_state.utilities)
        self.SC_cause_graph.update_allocation_arrows(new_arrows)

    def attach_sc_buttons(self):
        for widget in self.round_state.sc_widgets:
            widget.utility_minus_button.updateUtility.connect(  # this is going to need to get changed as well.
                partial(self.update_sc_graph))
            widget.utility_plus_button.updateUtility.connect(  # this is going to need to get changed as well.
                partial(self.update_sc_graph))


    def sc_create_allocations(self, client_id_list, total_id_list):


        self.disable_jhg_buttons(self.JHG_panel)

        if self.all_allocations: # if we wnat everyone to send allocations, go for it
            print("enabling the fetcher. might not be runing fast enough")
            self.enable_allocations_interface() # this enables it for all clients
        else: # if we only want specific people to allocatione:
            if self.round_state.client_id in client_id_list:
                self.enable_allocations_interface()
            else: # sit tight, get a new utilities list, go from there.
                utilities_list = [0 for _ in range(self.round_state.num_players)]
                # go ahead and just send back and empty list of 0's for our repsonse so its all good to go. shouldn't actually touch anything.
                self.connection_manager.send_message("SUBMIT_UTILITY", self.round_state.client_id, self.round_state.jhg_round_num, utilities_list)
                self.SC_voting_grid.setEnabled(False) # turn this off. Should become reenabled when all is said and done.

        if self.round_state.captain != -1: # DO THIS AFTER MAYBE>
            print("this is coming down from the create allocations thing")
            self.add_captain_label(self.round_state.captain)

        self.round_state.reset_everything()
        self.change_cause_labels(total_id_list)
        # self.update_sc_graph()  # go ahead and refresh the origin thing as well.

    def add_captain_label(self, captain):
        # lets try something just a lil different

        # so this code needs to check what label we need to put down
        # if we ARE the captain we put in a certain label
        # if we are NOT the captain, make sure to update the number


        ## edge case - we are no longer the captain, but we were the captian.


        if captain == self.round_state.client_id: # WE ARE THE CAPTAIN
            new_label = "YOU are the captain!"
            is_captain = True
            other_label = "the captain is player "

        else:  # so it falls under here
            new_label = "The captain is player "
            is_captain = False
            other_label = "YOU are the captain!"


        for index in range(self.SC_panel.count()):
            if (self.SC_panel.tabText(index).startswith(new_label)) or (self.SC_panel.tabText(index).startswith(other_label)):
                if new_label.startswith("The captain"):
                    new_label += str(captain+1)

                self.SC_panel.setTabText(index, new_label)
                return



        # initalize the new tab
        new_tab_widget = QWidget()
        new_tab_label = QLabel("This is a disabled tab")

        new_layout = QVBoxLayout()
        new_layout.addWidget(new_tab_label)
        new_tab_widget.setLayout(new_layout)

        if not is_captain: # lil on the fly adjustment for the label
            new_label += (str(self.round_state.captain + 1))

        new_tab_index = self.SC_panel.addTab(new_tab_widget, new_label)

        # Disable the new tab so it can't be selected
        self.SC_panel.setTabEnabled(new_tab_index, False)

    def sc_update_influence(self, Influence, new_utilities):
        # ok what did this need to do
        update_sc_network_graph(self, Influence, new_utilities, self.round_state.sc_round_num) # yeah sure why not