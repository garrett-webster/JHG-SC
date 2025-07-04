import random

class Random():
    def __init__(self, new_id, utility_per_player=3):
        self.number_type = 0  # used for logging purposes.
        self.self_id = new_id
        self.utility_per_player = utility_per_player

    def get_number_type(self):  # used for logging.
        return self.number_type

    def create_column(self, total_players):
        new_column = [0] * total_players
        for i in range(total_players):
            new_column[i] = random.randint(-1, 4)
        return new_column