# social welfare bot - always picks whats best for everyone.

class SocialWelfareBot:
    def __init__(self, self_id):
        self.self_id = self_id
        self.type = "P"
        self.number_type = 1

    def set_chromosome(self, chromosome):
        self.chromosome = chromosome

    def get_number_type(self):
        return self.number_type

    def get_vote(self, current_options_matrix, previous_votes=None, cycle=0, max_cycle=3):

        options = {}


        self.num_players = len(current_options_matrix)
        self.num_causes = len(current_options_matrix[0])
        for col in range(len(current_options_matrix[0])): # want the cols not num rows.
            options[col] = 0

        for col in range(len(current_options_matrix[0])): # make the assumption that he is square.
            for row in range(len(current_options_matrix)):
                options[col] += current_options_matrix[row][col]


        cur_max = 0
        curr_best = -1 # make -1 an option for selection, that way we cna do funny things wid it.
        for col in options:
            if options[col] > cur_max:
                cur_max = options[col]
                curr_best = col

        #print('this is what we are voting for ', curr_best) # no reason to keep this around
        return curr_best