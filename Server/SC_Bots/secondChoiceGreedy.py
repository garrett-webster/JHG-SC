# this brother doesn't even think, he just votes greedy. haven't implemented him yet though, at least in here. THere is a basic implementation under
# the SOcial choice sim under get vote. just repurpose the code under this umbrella and go from there.
import math


class secondChoiceGreedy():
    def __init__(self, self_id):
        self.self_id = self_id
        self.type = "G"

    def set_chromosome(self, chromosome):
        self.chromosome = chromosome

    def get_vote(self, current_options_matrix, previous_votes=None):
        current_row = current_options_matrix[self.self_id]
        temp_row = current_row[:] # make a copy for the fetcher
        first_vote = temp_row.index(max(temp_row)) # take the first vote
        temp_row[first_vote] = float("inf") # make the first vote smallest so we don't use it again
        second_vote = temp_row.index(max(temp_row)) # grab the second vote
        current_vote = second_vote if current_row[second_vote] >= 0 else -1 # grab the current vote, unless its less than zero, then do nothing.

        return current_vote # return it


