import json
import os
from datetime import datetime

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