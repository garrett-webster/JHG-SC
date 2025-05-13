import json
import os
from datetime import datetime
from operator import truediv

from fontTools.pens.basePen import NullPen

from Client.combinedLayout.colors import COLORS



class JHGLogger():
    def __init__(self, jhg_sim):
        self.jhg_sim = jhg_sim
        self.big_boy_data = {}
        # self.big_boy_data["Popularity"] = {}
        # self.big_boy_data["Influence"] = {}
        # self.big_boy_data["T"] = {}
        self.start_time = datetime.now()


    def record_individual_round(self):
        T, popularity, influence = self.jhg_sim.individual_round_deets_for_logger()
        total_data = {}
        total_data["T"] = T.tolist()
        total_data["popularity"] = popularity.tolist()
        total_data["influence"] = influence.tolist()
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")

        my_path = os.path.dirname(os.path.abspath(__file__))
        filename = "jhg_logs_repo/" + timestamp + ".json"
        file_path = os.path.join(my_path, filename)
        with open(file_path, "w") as file:
            json.dump(total_data, file, indent=4)

    def add_round_to_overview(self, round_num):
        # gonna keep with with round first, then key. just becuase, why not.
        T, popularity, influence = self.jhg_sim.individual_round_deets_for_logger()
        self.big_boy_data[round_num] = {}
        self.big_boy_data[round_num]["Popularity"] = popularity.tolist()
        self.big_boy_data[round_num]["Influence"] = influence.tolist()
        self.big_boy_data[round_num]["T"] = T.tolist()
        # self.big_boy_data["Popularity"][round_num] = popularity.tolist()
        # self.big_boy_data["Influence"][round_num] = influence.tolist()
        # self.big_boy_data["T"][round_num] = T.tolist()

    def conclude_overview(self):
        my_path = os.path.dirname(os.path.abspath(__file__))
        filename = "jhg_logs_repo/conclude.json"
        file_path = os.path.join(my_path, filename)
        with open(file_path, "w") as file:
            json.dump(self.big_boy_data, file, indent=4)



    def record_longer_vision(self, popularity_lists):
        file_path = r"C:\Users\Sean\Documents\GitHub\OtherGarrettStuff\JHG-SC\Server\jhg_logs_repo"
        file_name = datetime.now().strftime("%Y%m%d_%H%M%S") + " biggerBoy.json"
        file_path = os.path.join(file_path, file_name)
        for round in popularity_lists:
            popularity_lists[round] = popularity_lists[round].tolist()

        with open(file_path, "w") as file:
            json.dump(popularity_lists, file, indent=4)




    def write_official_version(self):


        total_data = {}
        total_data["status"] = "started"
        # set up the lobby dict
        lobby_dict = {}
        lobby_dict["code"] = "nan"
        lobby_dict["num_players"] = self.jhg_sim.num_players
        lobby_dict["num_observers"] = 0 # we don't have that functionality built in
        lobby_dict["creator_name"] = "None"
        lobby_dict["admins"] = []
        lobby_dict["playerNames"] = ""
        lobby_dict["game_started"] = True
        total_data["lobby"] = lobby_dict
        # set up game params
        game_params = {}
        game_params["length_of_round" ] = "125" # no clue what this is supposed to mean
        end_game_params = {}
        end_game_params["low"] = "Na"
        end_game_params["high"] = "Na"
        end_game_params["runtimeType"]  = "time"
        game_params["end_game_criteria"] = end_game_params
        total_data["gameParams"] = game_params
        # popularity function params:
        # ok SO these are set under the engine. these are the defualt values. as far as I am aware we never touch these in this version.
        popularity_function_params = {}
        popularity_function_params["alpha"] = 0.2
        popularity_function_params["beta"] = 0.5
        popularity_function_params["cGive"] = 1.3
        popularity_function_params["cKeep"] = 0.95
        popularity_function_params["cSteal"] = 1.6
        popularity_function_params["povertyLine"] = 0
        popularity_function_params["shouldUseNewUpdate"] = True
        total_data["popularityFunctionParams"] = popularity_function_params
        # set up da government params
        governemnt_params = {} # we never have a govermnet so IDK
        total_data["governmentParams"] = governemnt_params
        # set up a couple of other things
        total_data["name_set"] = "Nan" # we don't have any of these yet
        total_data["chatType"] = "none"
        total_data["messageType"] = "none"
        total_data["colorGroups"] = []
        # labels
        labels = {}
        labels["enabled"] = False
        labels["labelPools"] = {}
        total_data["labels"] = labels
        total_data["custom_params"] = {}
        # show
        show = {}
        show["roundLength"] = True
        show["gameLength"] = False
        show["chatType"] = False
        show["messageType"] = False
        show["nameSet"] = False
        show["initialSetup"] = True
        show["grouping"] = True
        show["labels"] = True
        show["pregame"] = False
        show["agents"] = True
        total_data["show"] = show
        total_data["advancedGameSetup"] = None
        total_data["preGame"] = None
        # allow edit
        allow_edit = {}
        allow_edit["roundLength"] = True
        allow_edit["gameLength"] = True
        allow_edit["chatType"] = True
        allow_edit["messageType"] = True
        allow_edit["initialSetup"] = True
        allow_edit["grouping"] = True
        allow_edit["labels"] = True
        allow_edit["advancedParams"] = True
        allow_edit["government"] = True
        allow_edit["visibilities"] = True
        allow_edit["colorGropuing"] = True
        allow_edit["pregame"] = True
        allow_edit["agents"] = True
        total_data["allow_edit"] = allow_edit
        total_data["creatorId"] = "Garrett"
        # end condition
        end_condition = {}
        end_condition["duration"] = "long" # BRRRR
        end_condition["runTypeTime"] = "time"
        total_data["end_condition"] = end_condition

        # player time. this is where stuff gets real.
        player_list = []
        for i in range(self.jhg_sim.num_players):
            new_player = {}
            new_player["name"] = str(i) # we don't technically have support for this
            new_player["permissionLevel"] = "regular"
            new_player["game_name"] = str(i)
            new_player["color"] = COLORS[i]
            new_player["hue"] = None
            new_player["avatar"] = None
            new_player["Icon"] = None
            player_list.append(new_player)


        total_data["players"] = player_list
        total_data["observers"] = [] # we don't even ahve this functionality built in yet.
        total_data["Transactions"] = {}

        # so after doing some play tests, I can conclude that its written from to
        # so row 10 spot 0 is from player 10 to player 0. this will be useful.
        num_tokens = self.jhg_sim.num_players * 2

        # literally zero clue if this works.
        all_rounds = {}
        for round in self.big_boy_data:
            current_transaction_matrix = self.big_boy_data[int(round)]["T"]
            current_round = {}
            for i in range(self.jhg_sim.num_players):
                allocations = {}
                for j in range(len(current_transaction_matrix[i])):
                    allocations[str(j)] = current_transaction_matrix[i][j] * num_tokens
                current_round[i] = allocations
            all_rounds[round] = current_round

        total_data["transactions"] = all_rounds

        total_data["voteData"] = None

        player_round_info = {} # literally no clue what this is supposed to do or how to populate it

        total_data["playerRoundInfo"] = player_round_info


        influences = {}
        for round in self.big_boy_data:
            current_round = {}
            for i, player in enumerate(self.big_boy_data[int(round)]["Influence"]):
                for individual in range(len(self.big_boy_data[int(round)]["Influence"][i])):
                    current_round[str(i)] = self.big_boy_data[int(round)]["Influence"][i]
            influences[str(round)] = current_round

        total_data["Influences"] = influences


        # lots of problems within this particualr loop.
        popularities = {}
        for round in range(len(self.big_boy_data[next(iter(self.big_boy_data))])-1):
            current_round = {}
            for i, player in enumerate(self.big_boy_data[int(round)]["Popularity"]):
                current_round[str(i)] = self.big_boy_data[int(round)]["Popularity"][i]

            popularities[str(round)] = current_round


        total_data["popularities"] = popularities

        total_data["groups"] = {} # we don't support that feature in this version. its just not there.

        total_data["start_date_time"] = self.start_time.strftime("%Y%m%d_%H%M%S")


        chat_info = {}
        chat_info["global"] = {} # nothing in there
        total_data["chatInfo"] = chat_info


        government_round_info = {}
        government_round_info["governmentPlayerNames"] = None
        government_round_info["round"] = 0
        government_round_info["playerVoteBallots"] = None
        government_round_info["customRoundInfo"] = {}

        total_data["governmentRoundInfo"] = government_round_info

        total_data["colorGroups"] = []

        my_path = os.path.dirname(os.path.abspath(__file__))
        file_name = "formalStyleConclusion.json"
        file_path = os.path.join(my_path, file_name)
        with open(file_path, "w") as outfile:
            json.dump(total_data, outfile, indent=4)










