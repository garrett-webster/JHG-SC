# this brother doesn't even think, he just votes greediest, then takes his second option. testing / edgecases, not really for actual use.


class secondChoiceGreedy():
    def __init__(self, self_id):
        self.self_id = self_id
        self.type = "G"
        self.number_type = 5

    def set_chromosome(self, chromosome):
        self.chromosome = chromosome

    def get_number_type(self):
        return self.number_type

    def get_vote(self, current_options_matrix, previous_votes=None, cycle=0, max_cycle=3):
        current_row = current_options_matrix[self.self_id]
        temp_row = current_row[:] # make a copy for the fetcher
        first_vote = temp_row.index(max(temp_row)) # take the first vote
        temp_row[first_vote] = float("-inf") # make the first vote smallest so we don't use it again
        second_vote = temp_row.index(max(temp_row)) # grab the second vote
        if current_row[second_vote] < 0:
            second_vote = -1
        return second_vote

