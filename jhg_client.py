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
    host = '127.0.0.1'
    #port = 12346
    port = 12346

    connection_manager = ClientConnectionManager(host, port)

    init_vals = connection_manager.get_message()[0]
    client_id = init_vals["CLIENT_ID"]
    num_players = init_vals["NUM_PLAYERS"]
    num_cycles = init_vals["NUM_CYCLES"]

    window = MainWindow(connection_manager, num_players, client_id, num_cycles)
    window.show()
    app.exec()