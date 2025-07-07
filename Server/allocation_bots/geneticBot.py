class GeneticBot:
    def __init__(self, new_id, utility_per_player):
        self.number_type = 1  # used for logging purposes.
        self.self_id = new_id
        self.utility_per_player = utility_per_player

    def get_number_type(self):  # used for logging.
        return self.number_type

    def create_column(self, total_players):
        # so we have a couple of options on how we decide to represent this.

        new_column = [self.utility_per_player] * total_players # bit of a jump here but whatever. allocates everything evenly. never tested actually, kinda curious to see hwwat happens.
        # get rid of all the random stuff, Just want a utility score.
        return new_column