import time

from PyQt6.QtWidgets import QVBoxLayout, QTabWidget, QHBoxLayout, QLabel
import pyqtgraph as pg

from Client.combinedLayout.sc_tornado_graph import sc_create_tornado_graph
from Client.combinedLayout.SCVotingGrid import SCVotingGrid
from Client.combinedLayout.ScCreationPanel import ScCreationPanel

from Client.combinedLayout.colors import COLORS
from Client.combinedLayout.hoverScatter import HoverScatter


from PyQt6.QtCore import QTimer


def create_sc_ui_elements(main_window):
    client_id = main_window.round_state.client_id
    graphs_layout = QVBoxLayout()
    main_window.tornado_canvas = sc_create_tornado_graph(main_window, main_window.tornado_fig, main_window.tornado_ax, main_window.tornado_y)

    sc_graph_tabs = QTabWidget()
    sc_graph_tabs.addTab(main_window.SC_cause_graph, "Causes Graph")
    sc_graph_tabs.addTab(main_window.tornado_canvas, "Effect of past votes")

    graphs_layout.addWidget(sc_graph_tabs)

    # Set up the SC history panel
    main_window.SC_voting_grid = SCVotingGrid(main_window.round_state.num_players, client_id, graphs_layout, main_window)
    main_window.SC_voting_grid.update_grid([main_window.starting_util for _ in range(main_window.round_state.num_players)], [[0 for _ in range(3)] for _ in range(main_window.round_state.num_players)])

    main_window.SC_panel.setMinimumWidth(400)
    main_window.SC_panel.addTab(main_window.SC_voting_grid, "Next Round")
    main_window.SC_panel.setTabEnabled(0, False)
    main_window.SC_panel.setCurrentIndex(1) # don't let them touch it yet

    # Set up the SC allocations panel



# Triggered by SC_INIT
def SC_round_init(main_window):
    if main_window.round_state.captain != -1 and main_window.round_state.captain != main_window.round_state.client_id:
        print("or is it this causing it ")
        # There is a captain, but we aren't the captain
        main_window.add_captain_label(main_window.round_state.captain)
        main_window.SC_panel.setTabEnabled(0, False)
        # also create an auto submitted vote here.
        time.sleep(0.5) # just go ahead and rattle something off for us.
        # this sends a vote back just so we don't have to worry about it
        # get rid of this and hope for the best
        main_window.connection_manager.send_message("SUBMIT_SC", main_window.round_state.client_id, -1)

    else:
        main_window.add_captain_label(main_window.round_state.captain)
        main_window.SC_panel.setTabEnabled(0, True)

    # Update sc ui elements
    for button in main_window.SC_voting_grid.buttons: # WHEE
        if button.objectName() != "clear_button":
            button.setEnabled(True)
    # I think? this is whwere this needs to happen? Maybe?
    main_window.SC_panel.setCurrentIndex(0)  # make sure to move the fetcher back to the first panel here, regardless of where they were.
    main_window.SC_panel.setTabVisible(2, False)  # should disable it for everyone
    if main_window.round_state.captain != -1:
        if main_window.round_state.captain != main_window.round_state.client_id:
            pass # if we are NOT the captain
            new_utilities = [[0,0,0] for _ in range(main_window.round_state.num_players)]
            main_window.SC_voting_grid.update_utilities(new_utilities)
        else: # captain model enabled, and we are the captain. we need to see everything.
            main_window.SC_voting_grid.update_utilities(main_window.round_state.utilities_mat)
    main_window.SC_panel.setCurrentIndex(0) # should forcefully move them over if they aren't there already.
   # print("This si the main_window_round staet round num thingy ", main_window.round_state.sc_round_num)
    # I think this just needs to always go off now in this branch, at least.
    main_window.SC_cause_graph.update_sc_nodes_graph_gritty(main_window.round_state.sc_round_num)


# Triggered by SC_OVER
def update_sc_utilities_labels(main_window, round_num, new_utilities, winning_vote, last_round_votes, last_round_utilities):
    history_grid = main_window.sc_history_grid
    captain = main_window.round_state.captain
    history_grid.update_sc_history(round_num, last_round_votes, last_round_utilities, winning_vote, captain)
    main_window.SC_panel.setCurrentIndex(1)
    main_window.SC_cause_graph.update_arrows(history_grid.sc_history[str(round_num)]["votes"], True)
    main_window.SC_panel.setTabText(1, "Results")
    main_window.SC_panel.setTabText(0, "Next Round")
    main_window.SC_panel.setTabEnabled(0, False)

    if winning_vote != -1:
        main_window.SC_voting_grid.update_col_2(new_utilities)


def tab_changed(main_window, index):
    current_tab = main_window.SC_panel.widget(index)
    cause_graph = main_window.SC_cause_graph
    if current_tab == main_window.SC_voting_grid:
        cause_graph.update_sc_nodes_graph_gritty(main_window.round_state.sc_round_num)
        cause_graph.update_arrows(main_window.round_state.current_votes, True)

        if main_window.SC_panel.tabText(1) == "Results":
            main_window.SC_panel.setTabText(1, "History")


    elif current_tab == main_window.sc_history_grid and main_window.sc_history_grid.sc_history:
        sc_history_tab = main_window.sc_history_grid
        selected_round = sc_history_tab.round_drop_down.currentIndex() + 1
        votes = sc_history_tab.sc_history[str(selected_round)]["votes"]
        winning_vote = sc_history_tab.sc_history[str(selected_round)]["winning_vote"]
        cause_graph.update_sc_nodes_graph_gritty(selected_round, winning_vote)
        cause_graph.update_arrows(votes)

        # # SO
        # # this si gonna get werid.
        # if main_window.round_state.captain != -1 and main_window.round_state.captain != main_window.round_state.client_id:
        #     sc_history_tab.self.sc_history =
        # else:
        #     pass # full history
        # # this needs to be changed to make sure that only the captian can see the history.

def sc_vote(main_window, vote):
    main_window.SC_voting_grid.current_vote = vote


def sc_submit(main_window, voting_grid):
    # voting_grid.select_button(None) # Clears the selection from the SC voting buttons
    main_window.connection_manager.send_message("SUBMIT_SC", main_window.round_state.client_id, main_window.SC_voting_grid.current_vote)


def disable_sc_buttons(main_window):
    for button in main_window.SC_voting_grid.buttons:
        button.setEnabled(False)
        if button.objectName() == "SCSubmitButton":
            button.setText("Submit Vote")
    main_window.SC_voting_grid.current_vote = -1


def get_winning_vote(votes):
    vote_counts = {"0": 0, "1": 0, "2": 0}
    for vote in votes.values():
        if vote != -1:
            vote_counts[str(vote)] += 1
    winning_vote = int(max(vote_counts, key=vote_counts.get))

    if vote_counts[str(winning_vote)] <= len(votes) // 2:
        winning_vote = -1

    return winning_vote + 1

def update_sc_ui_elements(main_window):
    player_utilities = main_window.round_state.new_utilities
    print("here are the player_utilities ", player_utilities)
    for i in range(main_window.round_state.num_players):
        main_window.round_state.players[i].utility_over_time.append(player_utilities[str(i)])
        print("here is the len of main_windows.round_state.players[i].utilities_over_time ", len(main_window.round_state.players[i].utility_over_time))
        QTimer.singleShot(0, lambda: update_sc_util_graph(main_window.round_state, main_window.sc_utility_graph))


def update_sc_util_graph(round_state, sc_util_graph):
    sc_util_graph.clear()
    try:
        sc_util_graph.useOpenGL(False)
    except:
        pass

    max_utility = 0
    all_spots = []

    for i, player in enumerate(round_state.players):
        color = COLORS[i]
        pen = pg.mkPen(color, width=2)

        x = list(range(len(player.utility_over_time)))
        y = player.utility_over_time

        line = pg.PlotDataItem(x, y, pen=pen)
        sc_util_graph.addItem(line)

        player_spots = [
            {
                'pos': (x[j], y[j]),
                'data': f"Player {player.id + 1} (Round {j}): {y[j]}",
                'brush': pg.mkBrush(color),
                'size': 8,
                'pen': None
            }
            for j in range(len(x))
        ]
        all_spots.extend(player_spots)
        max_utility = max(max_utility, max(y))

    scatter = HoverScatter(spots=all_spots)
    sc_util_graph.addItem(scatter)

    view_box = sc_util_graph.getViewBox()
    view_box.setLimits(
        xMin=0,
        xMax=len(round_state.players[0].utility_over_time)-1+0.1,
        yMin=0,
        yMax=max_utility + 10,
    )

    max_rounds = max(len(p.utility_over_time) for p in round_state.players)
    sc_util_graph.setXRange(0, max_rounds-1, padding=2)

    sc_util_graph.setYRange(0, max_utility + 10, padding=0)
    #view_box.autoRange()
    sc_util_graph.repaint()