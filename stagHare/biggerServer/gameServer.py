#this is where the scheduling and holding all the big dicts / writing to disk takes place. also instantiates game instances given specific things.
import os

import numpy as np

from littleServer import gameInstance
from multiprocessing import Process
import multiprocessing
import json
import time


# 1. Random, 2. AlegAAtr, 3. QAlegAATr, 4. SMAlegAATr 5.RAW0,  ## agent types. # we won't need these anymore
# but this is where we will put the bot types once those have been cleared up.

STAG_POINTS = 20
HARE_POINTS = 10

connected_clients = {}

class GameServer():
    def __init__(self, new_clients, client_id_dict, client_usernames, num_iterations, HEIGHT, WIDTH):
        self.connected_clients = new_clients
        self.client_id_dict = client_id_dict
        self.client_usernames = client_usernames
        self.user_name_to_client_id_dict = {v: k for k, v in client_usernames.items()}
        self.points = self.player_points_initialization()
        self.current_round = 0
        self.max_iterations = 2
        # this takes the stuff at a high level.
        self.high_level_dict = {}  # this stores the round and then situation break down.
        self.num_iterations = num_iterations
        self.height = HEIGHT
        self.width = WIDTH
        self.scheduler(new_clients)


    # this is where the meat of the function happens.
    def scheduler(self, new_clients):
        q = multiprocessing.Queue()

        # for i in range(1, 40): ## code for testing smaller edge cases. Just leave it here incase something breaks and we need to test.
        #     current_round = i
        #     player_indices_round_2 = [[0]]  # the players that will be in the same game
        #     situations = [["A"]]  # the number and type of bot we are expecting.
        #     games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, situations).
        #     self.run_games(games_list, q, current_round)
        #     self.append_average_points(current_round)

        for i in range(1, 2): # run just a single round so I can check that its running 3 times.
            current_round = i
             # TODO: Turn this into an actual parameter somewhere.
            # there's DEFINITELY a better way to do this. Like frfr.
            # well we really only need GHare, GStag, ALlegatr as human information will be limited up higher by connected clients in the room settings.
            players_indicies_round_1 = [[0]] # player indicies in each room
            situations = [["CABAgent1"], ["CABAgent1"]] # sitation of each room.
            games_list = self.create_game_processes(players_indicies_round_1, current_round, new_clients, q, situations, self.num_iterations, self.height, self.width)
            self.run_games(games_list, q, current_round)
            self.append_average_points(current_round)

        for i in range(2, 3): # run just a single round so I can check that its running 3 times.
            current_round = i
             # TODO: Turn this into an actual parameter somewhere.
            # there's DEFINITELY a better way to do this. Like frfr.
            # well we really only need GHare, GStag, ALlegatr as human information will be limited up higher by connected clients in the room settings.
            players_indicies_round_1 = [[0]] # player indicies in each room
            situations = [["CABAgent1"], ["CABAgent1"]] # sitation of each room.
            games_list = self.create_game_processes(players_indicies_round_1, current_round, new_clients, q, situations, self.num_iterations, self.height, self.width)
            self.run_games(games_list, q, current_round)
            self.append_average_points(current_round)

        # for i in range(3, 4): # run just a single round so I can check that its running 3 times.
        #     current_round = i
        #     max_rounds = 2 # TODO: Turn this into an actual parameter somewhere.
        #     # there's DEFINITELY a better way to do this. Like frfr.
        #     # well we really only need GHare, GStag, ALlegatr as human information will be limited up higher by connected clients in the room settings.
        #     players_indicies_round_2 = [[0]] # player indicies in each room
        #     situations = [["CABAgent1"]] # sitation of each room.
        #     print("this is what we think the current round is ", current_round, " iterating up to ", current_round + (max_rounds - 1))
        #     games_list = self.create_game_processes(players_indicies_round_2, current_round, new_clients, q, situations)
        #     self.run_games(games_list, q, current_round + (max_rounds - 1))
        #     self.append_average_points(current_round)

        self.save_stuff_small() # this is where this is supposed to get used... I think.


        print("all done!")





    # this thing is a DOOZY
    def create_game_processes(self, player_indices, current_round, new_clients, q, situations, num_iterations, height, width, save=True):
        games_list = [] # a lit of all the games we want to run (as delta functions)

        for i, indices in enumerate(player_indices): # every list in the list of lists of players that we need to treat separate.
            # Create a new process for each list of indices
            # we also need to create the player dict pairs, pass in the queue, the current round, the expected situation, and if we want to write it to json
            game_process = Process(target=self.game_thread,
                                   args=(
                                   self.create_player_dict_pairs(indices, new_clients), q, current_round,
                                   situations[i], num_iterations, height, width, save))
            games_list.append(game_process)

        return games_list


    def run_games(self, games_list, q, current_round):
        # modifies self.points more than anything else after the games conclude.
        self.start_and_join_games(games_list, q)
        points_to_send, points_to_save = self.calc_avg_points(current_round)
        print("These are the points to save ", points_to_save)
        self.points_to_save = points_to_save
        self.points_to_send = points_to_send # I don't want to calculate that by hand, that's dumb.
        self.send_leaderboard(points_to_send)  # sends out the updated leaderboard.



    def start_and_join_games(self, games_list, q):
        # start the threads
        for game in games_list:
            game.start()
        # monitor the threads
        for game in games_list:
            game.join()

        # create the smaller dicts and the big dicts prepared
        dicts_to_merge = []
        all_big_dicts = []
        # pop all the return values off the queue and add it to the list
        while not q.empty():
            item = q.get()
            dicts_to_merge.append(item)

        # combine all possible instances and throw it in the big one.
        # also modifies self.points, which is where the real magic happens.
        return self.merge_dicts(dicts_to_merge), all_big_dicts


    def create_player_dict_pairs(self, new_players, new_clients): # new players is a list containing a bunch of indexes, and returns a dict of pairs.
        return_players =  {}
        for player in new_players:
            player_1 = list(new_clients.items())[player]
            player_1_key, player_1_socket = player_1
            return_players[player_1_key] = player_1_socket
        return return_players


    def game_thread(self, new_clients, q, current_round, situations, num_iterations, height, width, save):
        new_points_1 = gameInstance(new_clients, self.client_id_dict, situations, num_iterations, height, width, current_round, save)  # need to somehow include an agent type
        for game_points_list in new_points_1.return_list:
            q.put(game_points_list) # just throw the points lists onto q and we will go through them later.

    def player_points_initialization(self):
        player_points = {}
        for i in range(len(self.connected_clients)):
            player_points[i] = {}

        return player_points


    def merge_dicts(self, dicts_to_merge):
        for dict in dicts_to_merge:
            curr_client = dict["Player"]
            curr_points = dict["Games"]
            curr_round = dict["Round"]

            self.points[curr_client][curr_round] = curr_points
            print("These are the curr points ", curr_points)

        return self.points



    def calc_avg_points(self, target_round):
        print("here is the self.points ", self.points)
        new_list_to_send = [] # list of tuples, holds the clientID and then the number of points that they have accrued
        new_list_to_save = [] # this holds the serverSide playerID and then the number of points they ahve accrued.
        for player in self.points:
            new_points = [0 for _ in range(self.max_iterations)]
            curr_points = 0
            for curr_round in self.points[player]:
                if curr_round <= target_round: # catastrophically stupid idea
                    print("These are what the curr games look like ", self.points[player][curr_round])
                    for curr_game in self.points[player][curr_round]:
                        print("these are the entries that are causing it to crash \n", player, " ", curr_round, " ", curr_game, " ")
                        print("and here is the key thats causing the brick ", self.points[player][curr_round][curr_game])
                        if curr_game == "new_points" or curr_game == "avg_points":
                            continue
                        if self.points[player][curr_round][curr_game]["stag"] == True:
                            curr_points += STAG_POINTS
                            new_points[curr_game-1] = STAG_POINTS
                        if self.points[player][curr_round][curr_game]["hare"] != False:
                            curr_points += HARE_POINTS / self.points[player][curr_round][curr_game]["hare"]
                            new_points[curr_game-1] = HARE_POINTS / self.points[player][curr_round][curr_game]["hare"]
                else:
                    break

            avg_points = 0
            if curr_points > 0:
                avg_points = ( curr_points / target_round ) / self.max_iterations # need some nesting there lol.
                avg_points = round(avg_points, 2) # round that fetcher to 2 decimals.

            send_tuple = (self.client_usernames[int(player)], avg_points)
            new_list_to_send.append(send_tuple)
            save_tuple = (player, new_points) # this saves the play by play. maybe.
            new_list_to_save.append(save_tuple)

        sorted_points = sorted(new_list_to_send, key=lambda x: x[1], reverse=True)
        # don't bother sorting the new_list_to_save, that doesn't even make sense
        print("here is self points post update 208 ", self.points)
        return sorted_points, new_list_to_save

        # so now we have the number of current points that they have, but we want to add a new points thing in here somewhere, and apparently it needs to be here. thats dookie.




    # fairly straightforward. Takes in hte new points and sends them out.
    def send_leaderboard(self, new_points_dict):
        print("Aight do we get in here first off ")
        print("And if we do, what is the new points dict \n", new_points_dict)
        time.sleep(2)  # lets everyone see the leaderboard
        message = {
            "LEADERBOARD": new_points_dict,
        }
        new_message = json.dumps(message).encode()
        for client in self.connected_clients:
            self.connected_clients[client].send(new_message)
        time.sleep(2)  # lets everyone see the leaderboard

    def append_average_points(self, current_round):
        print("here are the points to send ", self.points_to_send, " and here are the points to save ", self.points_to_save)
        for tuple in self.points_to_send:
            client_id = self.user_name_to_client_id_dict[tuple[0]]
            self.points[client_id][current_round]["avg_points"] = tuple[1]
        for tuple in self.points_to_save:
            client_id = tuple[0]
            games_list = tuple[1]
            for i, game in enumerate(games_list): # i starts at 0, games start at 1. yeah its dumb...
                self.points[client_id][current_round][i+1]["new_points"] = game


    def save_stuff_small(self):
        desktop_path = os.path.expanduser("~/Desktop")
        folder_path = os.path.join(desktop_path, "stag_hare_jsons")
        top_level_path = "stag_hare_top_level.json"

        file_path_1 = os.path.join(folder_path, top_level_path)
        unique_file_path_1 = self.get_unique_filename(file_path_1)

        # tells us which hunter has which name for the high level dict.
        self.hunter_names = {}
        for index, name in enumerate(self.client_usernames):
            new_name = str(index)
            self.hunter_names[new_name] = self.client_usernames[name]

        with open(unique_file_path_1, "w") as f:
            json.dump(self.hunter_names, f, indent=4)
            json.dump(self.points, f, indent=4)


    def get_unique_filename(self, file_path):
        if not os.path.exists(file_path):
            return file_path
        else:
            base, extension = os.path.splitext(file_path)
            counter = 1
            while os.path.exists(f"{base}_{counter}{extension}"):
                counter += 1
            return f"{base}_{counter}{extension}"

# I bet this was useful at some point and I neatly side stepped it.
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.int64):
            return int(obj)  # Convert np.int64 to native Python int
        return super(NumpyEncoder, self).default(obj)
