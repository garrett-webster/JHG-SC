import json
import os
from datetime import datetime
from operator import truediv


class JHGLogger():
    def __init__(self, jhg_sim):
        self.jhg_sim = jhg_sim
        self.big_boy_data = {}
        self.big_boy_data["Popularity"] = {}
        self.big_boy_data["Influence"] = {}
        self.big_boy_data["T"] = {}


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
        T, popularity, influence = self.jhg_sim.individual_round_deets_for_logger()
        self.big_boy_data["Popularity"][round_num] = popularity.tolist()
        self.big_boy_data["Influence"][round_num] = influence.tolist()
        self.big_boy_data["T"][round_num] = T.tolist()

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
        end_game_params["low"] = 10
        end_game_params["high"] = 30
        end_game_params["runtimeType"]  = "time"
        game_params["end_game_criteria"] = end_game_params
        # popularity function params:
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

        # fetch it I don't like it. you know where to find it if you need it.


