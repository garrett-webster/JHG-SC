# this brother doesn't even think, he just votes greediest. haven't implemented him yet though, at least in here. THere is a basic implementation under
# the SOcial choice sim under get vote. just repurpose the code under this umbrella and go from there.
import math


class GreedyBot():
    def __init__(self, self_id):
        self.self_id = self_id
        self.type = "G"
        self.number_type = 2

    def set_chromosome(self, chromosome):
        self.chromosome = chromosome

    def get_number_type(self):
        return self.number_type

    def get_vote(self, current_options_matrix, previous_votes=None, cycle=0, max_cycle=3):
        current_row = current_options_matrix[self.self_id]
        current_vote = current_row.index(max(current_row))
        if current_row[current_vote] < 0: # if our best option is less than 0, try to make nothing happen.
            current_vote = -1
        return current_vote
        # actually just being able to abstain is a good idea. that way it doesn't muck with anything else.


