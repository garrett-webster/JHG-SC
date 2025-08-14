from functools import partial

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QGridLayout, QFrame, QWidget, QHBoxLayout

from Client.combinedLayout.SCPlayerWidget import SCPlayerWidget
from Client.combinedLayout.SubmitUtilityButton import SubmitUtilityButton

from Client.combinedLayout.colors import COLORS


class ScCreationPanel(QWidget):
    def __init__(self, round_state, connection_manager, token_counter, sc_buttons):
        super().__init__()
        while round_state.client_id == -1: # tripping over its own shoelaces.
            pass
        # footer
        # Needs to go through the SubmitButton class so that the signal and socket works correctly
        submitButton = SubmitUtilityButton() # prolly need a new submit button cause the old one is gonna do JHG stuff.
        sc_buttons.append(submitButton)
        # change the folloiwng function, not sure how
        submitButton.clicked.connect(lambda: submitButton.submit(round_state, connection_manager)) # DEF need to hcange this.

        token_counter.setText(f"Tokens: {round_state.utility}") # need a new variable that isn't token. change it to allocations.

        # Each of the following blocks of code creates a column to display a particular type of data per player.
        # Each column loops through the players and adds the respective element from the associated player class.
        player_panel = QGridLayout()

        # Headers for the table
        player_panel.addWidget(QLabel("Player"), 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        player_panel.addWidget(QLabel("Allocations"), 0, 2, alignment=Qt.AlignmentFlag.AlignCenter)

        # Creates a row in the gui for each player to display the popularity, tokens sent to, and tokens received from
        # that player the last round. Also adds the elements to allow for token allocations
        row_index = 1
        sc_widgets = round_state.sc_widgets
        for i in range(round_state.num_players):
            # everyone else (only worried abotu everyone else in this iteration)
            if i == round_state.client_id: # if this is us, adjust the text accordingly and go from there.
                sc_widgets[i].id_label.setText("You " + "(" + str(i+1) + ")")

            player_panel.addWidget(sc_widgets[i].id_label, row_index, 0)

            sc_widgets[i].id_label.setStyleSheet(f"color: " + COLORS[i])
            # player_panel.addWidget(round_state.players[i].popularity_label, row_index, 1)
            # player_panel.addWidget(round_state.players[i].sent_label, row_index, 2)
            # player_panel.addWidget(round_state.players[i].received_label, row_index, 3)

            allocations_row = QGridLayout()
            allocations_row.addWidget(sc_widgets[i].utility_minus_button, 0, 0)
            allocations_row.addWidget(sc_widgets[i].utility_box, 0, 1)
            sc_widgets[i].utility_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
            allocations_row.addWidget(sc_widgets[i].utility_plus_button, 0, 2)

            sc_widgets[i].utility_minus_button.updateUtility.connect( # this is going to need to get changed as well.
                partial(sc_widgets[i].update_utility_minus, round_state, token_counter, i))
            sc_widgets[i].utility_plus_button.updateUtility.connect(
                partial(sc_widgets[i].update_utility_plus, round_state, token_counter, i))
            # need to somehow connect this button do an entirely different function. so that it updates the graph.


            player_panel.addLayout(allocations_row, row_index, 2)

            row_index += 1

        # round_state.num_players + 4 accounts for the header and the spacer lines.
        player_panel.addWidget(submitButton, round_state.num_players + 4, 0, 1, 3)
        player_panel.addWidget(token_counter, round_state.num_players + 4, 3, 1, 3)


        self.setLayout(player_panel)