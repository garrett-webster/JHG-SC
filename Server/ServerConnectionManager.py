import json
import select
import random

from ConnectionManager import ConnectionManager


class ServerConnectionManager(ConnectionManager):
    def __init__(self, host, port, num_players, num_bots = 0):
        super().__init__(host, port)
        self.socket.bind((host, port))
        self.socket.listen(num_players)  # Allow only one connection

        # Init server-specific attributes
        self.num_players = num_players
        self.num_clients = 0
        self.num_bots = num_bots
        self.clients = {}
        self.player_only_ids = []
        self.create_total_order(num_players, num_bots)

        self.message_type_names = {
            "SC_INIT": ["ROUND_NUM", "OPTIONS", "NODES", "UTILITIES"],
            "SETUP": ["CLIENT_ID", "NUM_PLAYERS", "NUM_CYCLES"],
            "JHG": ["CURRENT_VOTES"],
            "JHG_OVER": ["ROUND", "POPULARITY", "INFLUENCE_MAT", "INIT_POP_INFLUENCE", "IS_LAST", "RECEIVED", "SENT"],
            "SC_VOTES": ["VOTES", "CYCLE", "IS_LAST_CYCLE"],
            "SC_OVER": ["ROUND_NUM", "WINNING_VOTE", "NEW_UTILITIES", "POSITIVE_VOTE_EFFECTS",
                        "NEGATIVE_VOTE_EFFECTS", "VOTES", "UTILITIES"],
        }

        # NOTE: All messages also receive the CLIENT_ID, but it is not included in the message_type specification
        self.received_message_type_names = {
            "JHG_ALLOCATIONS": ["ROUND_NUMBER", "ALLOCATIONS"],
            "SUBMIT_JHG": ["ROUND_NUMBER", "ALLOCATIONS"],
            "SUBMIT_SC": ["FINAL_VOTE"],
        }

    def create_total_order(self, num_players, num_bots):
        num_clients = num_players - num_bots
        client_list = []
        bots_list = []
        for i in range(num_clients):  # call me old fashioned but I want them to start at 1
            client_list.append("P" + str(i + 1))
        for i in range(num_bots):
            bots_list.append("B" + str(i + 1))

        total_list = client_list + bots_list
        random.shuffle(total_list)  # bars
        self.total_order = total_list
        print("This is the total order ", self.total_order)
        # now we need to list out hte player ID's.
        self.player_only_ids = [self.total_order.index(val) for val in total_list if
                                val.startswith("P")]  # this ID is zero indexed.
        print("these are the player only ID's ", self.player_only_ids)

    def get_total_list(self):
        return self.total_order



    ''' Functions to send messages to clients '''

    # Sends a given message to all clients
    '''
    distribute_message takes all of the passed values and pairs them with the names in message_type_names base off the 
    "TYPE" field. If the message is to be the same for all clients, then all of the items to be sent should be put as 
    positional arguments. If you need any individualized messages, you should pass a list of dictionaries to 
    unique_messages, where each dictionary corresponds with one field. Each dictionary should have an entry for each
    client, with its key being the associated client's id, and the value being what you want to send to that client for
    the specified name in message_type_names.
    '''
    def distribute_message(self, *args, unique_messages=None):
        for client_id, client_socket in self.clients.items():
            if unique_messages is None:
                self.send_message(client_socket, *args)
            else: # If a unique_message was passed, send the appropriate message to each client
                message = tuple(msg_dict.get(client_id) for msg_dict in unique_messages)
                self.send_message(client_socket, *args, *message)


    # Sends a message to a single client, given by their client id. Everything you want to send should be passed as a positional argument
    def send_individual_message(self, client, *args):
        client_socket = self.clients[client - self.num_bots] # Client ids are usually 1 indexed
        self.send_message(client_socket, *args)


    ''' Functions to accept input from clients '''

    def get_responses(self, continuous_distribution_type = None):
        responses = {}
        num_received = 0

        # Keep listening until all clients have responded
        while num_received < self.num_clients:
            data = self.read_responses() # Gets all the responses that have been sent thus far


            # Creates a response and appends it to responses for each received response
            for client, received_json in data.items():
                message_type = received_json["TYPE"]
                client_id = received_json["CLIENT_ID"]

                if client_id not in responses:
                    num_received += 1

                response = {"TYPE": message_type, "CLIENT_ID": client_id}
                for name in self.received_message_type_names[message_type]:
                    response[name] = received_json[name]

                responses[client_id] = response

            # Sometimes you want to continuously send out the responses until everyone has responded. If the
            # continuousDistributionType parameter is not none, it is the name of the message to send.
            if continuous_distribution_type is not None:
                self.distribute_message(continuous_distribution_type, responses)

        return responses


    # Checks for any clients that have sent a response and reads that response.
    def read_responses(self):
        ready_to_read, _, _ = select.select(list(self.clients.values()), [], [], 0.1)
        data = {}
        for client in ready_to_read:
            try:
                msg = ''
                while True:  # Accumulate data until the full message is received
                    chunk = client.recv(4096).decode()
                    msg += chunk
                    if len(chunk) < 4096:  # End of the message
                        break
                if msg:
                    data[client] = json.loads(msg)
            except Exception as e:
                pass
        return data


    # Wait until the expected number of clients have connected and initialize those connections
    # NOTE: This is somewhat hard coded for JHG/SC.
    # If trying to make this a more general use codebase, this needs some refactoring.
    def add_clients(self, num_clients, num_bots, num_cycles):
        # LETS SEE IF THIS WORKS
        # Accept new connections and add them to the connection manager until the specified number of connections have been made
        while len(self.clients) < num_clients:
            client_socket, client_address = self.socket.accept()
            player_specific_id = self.player_only_ids.pop(0)
            print("Received new client from: ", client_address)
            self.clients[player_specific_id] = client_socket
            self.num_clients += 1
            self.send_message(client_socket, "SETUP", player_specific_id, num_clients + num_bots, num_cycles)

