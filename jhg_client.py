import sys
import os

# Make sure we are running from the same folder as the .exe
if hasattr(sys, '_MEIPASS'):
    os.chdir(sys._MEIPASS)
else:
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("Client"), relative_path)

# import pyqtgraph


# --- Everything above this line is necessary for building the executable --- #

from PyQt6.QtWidgets import QApplication
from Client.ClientConnectionManager import ClientConnectionManager
from Client.combinedLayout.MainWindow import MainWindow

def load_stylesheet(path):
    with open(resource_path(path), "r") as file:
        return file.read()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet("combinedLayout/style.qss"))

    #host = '10.55.10.49'
    host = '127.0.0.1'  # if testing on personal machine or whatever
    #host = '192.168.36.5' # if testing on jonathons machine (note: sometimes that last number likes to change)
    #port = 12346
    port = 12345

    connection_manager = ClientConnectionManager(host, port)

    init_vals = connection_manager.get_message()[0]
    client_id = init_vals["CLIENT_ID"]
    num_players = init_vals["NUM_PLAYERS"]
    num_cycles = init_vals["NUM_CYCLES"]
    num_tokens_per_player = init_vals["TOKENS_PER_PLAYER"]
    utility_per_player = init_vals["UTILITY_PER_PLAYER"]
    starting_utility = init_vals["STARTING_UTILITY"]
    all_allocations = init_vals["ALL_ALLOCATIONS"]

    window = MainWindow(connection_manager, num_players, client_id, num_cycles, num_tokens_per_player, utility_per_player, starting_utility, all_allocations)
    #window.showFullScreen() # this enables full screen on the chromebooks
    window.show()
    app.exec()