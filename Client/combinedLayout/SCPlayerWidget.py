from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel
from Client.Player import PlayerState
from Client.combinedLayout.utility_buttons import PlusButtonUtility, MinusButtonUtility


class SCPlayerWidget(QWidget):
    def __init__(self, player_state: PlayerState):
        super().__init__()
        self.player_state = player_state
        self.id = self.player_state.id
        self.id_label = QLabel(str(self.id + 1))
        self.utility_box = QLabel("0")
        # Center the labels
        self.id_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Label to display total utilities
        self.utility_plus_button = PlusButtonUtility()
        self.utility_minus_button = MinusButtonUtility()
        #self.utility_minus_button = self.player_state.utility_minus_button
        #self.utility_plus_button = self.player_state.utility_plus_button


        # these will need more testing later, when I know that everything works.

    def update_utility_minus(self, round_state, tokens_label, player):
        if round_state.utility >= 0 and round_state.utilities[player] > -10: # don't want to be able to nuke them into oblivion.
            round_state.utilities[player] = round_state.utilities[player] - 1
            round_state.utility += 1  # they get one for the negative
        self.utility_box.setText(str(round_state.utilities[player]))
        tokens_label.setText("Utility: " + str(round_state.utility))




    def update_utility_plus(self, round_state, tokens_label, player):
        if round_state.utility > 0 and round_state.utilities[player] < 10: # don't want to be able to raise ourselves all the way up.
            round_state.utilities[player] = round_state.utilities[player] + 1
            round_state.utility -= 1
        self.utility_box.setText(str(round_state.utilities[player]))
        tokens_label.setText("Utility: " + str(round_state.utility))