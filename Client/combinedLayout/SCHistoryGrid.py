from PyQt6.QtWidgets import QHBoxLayout, QLabel, QComboBox

from Client.combinedLayout.SCGrid import SCGrid


class SCHistoryGrid(SCGrid):
    def __init__(self, num_players, player_id, col_2_header_text, causes_graph):
        self.sc_history = {}
        self.sc_history_for_viewing = {}
        self.causes_graph = causes_graph
        col_2_vals = [0 for _ in range(num_players)]
        utility_mat = [[0 for _ in range(3)] for _ in range(num_players)]
        super().__init__(num_players, player_id, col_2_header_text, col_2_vals, utility_mat)

        self.round_drop_down = QComboBox()
        self.round_drop_down.currentIndexChanged.connect(self.change_round)

        self.selector_layout = QHBoxLayout()
        self.selector_layout.addWidget(QLabel("Round to view"))
        self.selector_layout.addWidget(self.round_drop_down)

        self.layout.insertLayout(0, self.selector_layout)
        self.winning_vote = -1
        self.captain = -1 # need to update and keep trakc of whether or not we are the captains.
        self.client_id = player_id
        self.num_players = num_players

    def change_round(self, index):
        round_key = str(index + 1)

        if round_key in self.sc_history:
            self.update_sc_grid(self.sc_history[round_key]["votes"], self.sc_history[round_key]["utilities"], round_key)
        self.parent().parent().setTabText(1, "History")

    # make sure that sc history actually gets the full thing.
    def update_sc_history(self, round, votes, utilities, winning_vote, captain):
        self.round_drop_down.addItem(f"Round {round}")

        if captain != -1:
            new_utilities = [[0, 0, 0] for _ in range(self.num_players)]
            for i in range(len(new_utilities)):
                new_utilities[i][winning_vote-1] = utilities[i][winning_vote-1]
            self.sc_history[str(round)] = {"votes": votes, "utilities": new_utilities, "winning_vote": winning_vote, "captain": captain}
        else:
            self.sc_history[str(round)] = {"votes": votes, "utilities": utilities, "winning_vote": winning_vote, "captain": captain}

        self.round_drop_down.repaint()
        self.round_drop_down.setCurrentIndex(round - 1)
        self.captain = captain


    def update_sc_grid(self, votes, utilities, round_num, winning_vote=None):
        one_idx_votes = {key: value + 1 for key, value in votes.items()}
        super().update_grid(one_idx_votes, utilities)
        # winning_vote = get_winning_vote(votes)
        # winning_vote += 1

        # Color the labels for each player coinciding with the winning vote. Green if that cause has positive utility
        # for that player, red if it has negative utility for the player, and white if it is zero. Also resets the labels
        # for every other cause to white
        for row_idx, row in enumerate(self.cause_utility_labels):
            for cause_idx, label in enumerate(row):
                if cause_idx + 1 == winning_vote and winning_vote != 0:
                    if utilities[row_idx][winning_vote - 1] > 0:
                        label.setStyleSheet("color: green;")
                    elif utilities[row_idx][winning_vote - 1] < 0:
                        label.setStyleSheet("color: red;")
                    else:
                        label.setStyleSheet("color: white;")
                else:
                    label.setStyleSheet("color: white;")

        for i, label in enumerate(self.header_labels):
            label.setStyleSheet("color: white;")
            if winning_vote != 0:
                if i - 1 == winning_vote:
                    label.setStyleSheet("color: green;")


        # winning_vote -= 1
        # Draw the graph for the selected round
        self.causes_graph.draw_causes_graph(votes, utilities, winning_vote, int(round_num))
