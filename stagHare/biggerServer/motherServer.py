import json
import socket
import copy

from stagHare.shared import enemy
from stagHare.biggerServer.gameServer import GameServer

HUMAN_PLAYERS = 1
HEADLESS = HUMAN_PLAYERS == 0  # just in case I decide to run it headless it saves us a headache.

PAUSE_TIME = 3
connected_clients = {}
client_input = {}
client_usernames = {}
HEIGHT = 3
WIDTH = 3
client_id_dict = {}
hunters = []
MAX_ROUNDS = 2
round = 1

HARE_POINTS = 10
STAG_POINTS = 20
stag = enemy.Enemy("stag", HEIGHT, WIDTH)
hare = enemy.Enemy("hare", HEIGHT, WIDTH)

def maybe_start_game():
    """Start a game session if we have enough players."""
    if len(connected_clients) == HUMAN_PLAYERS:
        new_player_list = copy.copy(connected_clients)
        GameServer(new_player_list, client_id_dict, client_usernames)
        connected_clients.clear()
        client_id_dict.clear()
        client_usernames.clear()

def start_server(host='127.0.0.1', port=12345):
    print("do we get in here")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)

    while True:
        if HEADLESS:
            maybe_start_game()  # check before blocking on accept()

        client_socket, client_address = server_socket.accept()
        connected_clients[len(connected_clients)] = client_socket
        client_id_dict[client_socket] = len(connected_clients)

        data = client_socket.recv(1024)
        print("RAAG")
        try:
            received_json = json.loads(data.decode())
            client_usernames[len(connected_clients)] = received_json["USERNAME"]

            response = {
                "message": "Hello from the server!",
                "HEIGHT": HEIGHT,
                "WIDTH": WIDTH,
                "CLIENT_ID": client_id_dict[client_socket],
            }
            client_socket.send(json.dumps(response).encode())
        except json.JSONDecodeError:
            pass

        if not HEADLESS:
            maybe_start_game()  # check after accept() + handshake

if __name__ == "__main__":
    start_server()