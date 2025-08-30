from PyQt6.QtWidgets import QVBoxLayout, QTabWidget, QHBoxLayout, QLabel

from Client.combinedLayout.sc_tornado_graph import sc_create_tornado_graph
from Client.combinedLayout.SCVotingGrid import SCVotingGrid
from Client.combinedLayout.ScCreationPanel import ScCreationPanel


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
    # this is where we are going to need to work with the captain stuff.
    if main_window.round_state.captain != -1:
        main_window.add_captain_label(main_window.round_state.captain)

    # Update sc ui elements
    for button in main_window.SC_voting_grid.buttons: # WHEE
        if button.objectName() != "clear_button":
            button.setEnabled(True)
    main_window.SC_panel.setTabEnabled(0, True) # I think? this is whwere this needs to happen? Maybe?
    main_window.SC_panel.setCurrentIndex(0)  # make sure to move the fetcher back to the first panel here, regardless of where they were.
    main_window.SC_panel.setTabVisible(2, False)  # should disable it for everyone
    main_window.SC_voting_grid.update_utilities(main_window.round_state.utilities_mat)
    main_window.SC_panel.setCurrentIndex(0) # should forcefully move them over if they aren't there already.
   # print("This si the main_window_round staet round num thingy ", main_window.round_state.sc_round_num)
    # I think this just needs to always go off now in this branch, at least.
    main_window.SC_cause_graph.update_sc_nodes_graph_gritty(main_window.round_state.sc_round_num)


# Triggered by SC_OVER
def update_sc_utilities_labels(main_window, round_num, new_utilities, winning_vote, last_round_votes, last_round_utilities):
    history_grid = main_window.sc_history_grid
    history_grid.update_sc_history(round_num, last_round_votes, last_round_utilities, winning_vote)
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