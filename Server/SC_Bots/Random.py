import random
# I literally just want to see what happens when people play randomly. I am expecting a lot of nothing to happen.
# low cooperation score, 0 slope at the end, low covariance as well (especialyl over repeated games)

class RandomBot():
    def __init__(self, self_id):
        self.self_id = self_id
        self.type = "R"
        self.type = 0

    def set_chromosome(self, chromosome): # doesn't actually get used, just for conveience sake
        self.chromosome = chromosome

    def get_number_type(self):
        return self.number_type

    def get_vote(self, current_options_matrix, previous_votes=None):
        total_options = len(current_options_matrix[0]) # how many cuases are there w/ abstaining. Before they couldn't vote for cause 3.
        final_vote = random.randint(0, total_options) # so this is inclusive of upper limit,
        final_vote -= 1 # off my one error.
        return final_vote
