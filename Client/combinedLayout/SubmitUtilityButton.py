from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import QTimer

class SubmitUtilityButton(QPushButton):
    def __init__(self):
        super().__init__()
        self.setText('Submit')
        self.setObjectName("UtilitySubmitButton")
        self.cooldown_timer = QTimer(self)
        self.cooldown_timer.setSingleShot(True)
        self.cooldown_timer.timeout.connect(self.enable_button)

    def submit(self, round_state, connection_manager):
        if self.isEnabled():

            connection_manager.send_message("SUBMIT_UTILITY", round_state.client_id, round_state.jhg_round_num, round_state.get_utilities_list())
            self.setText('Resubmit')
            self.setEnabled(False)
            self.cooldown_timer.start(500)

    def enable_button(self):
        self.setEnabled(True)