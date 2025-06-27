from PyQt6.QtWidgets import QPushButton


class SubmitUtilityButton(QPushButton):
    def __init__(self):
        super().__init__()
        self.setText('Submit')
        self.setObjectName("UtilitySubmitButton")


    def submit(self, round_state, connection_manager):
        print("these are the utilities that we are submnitting ", round_state.get_utilities_list())
        connection_manager.send_message("SUBMIT_UTILITY", round_state.client_id, round_state.jhg_round_num, round_state.get_utilities_list())
        self.setText('Resubmit')
