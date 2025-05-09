# Sean's Smartest Greedy Bot - for now. capable of switching and recognizing majorities. tiebreaksers still result in abstaining bc it doesn't have an idea of
# social awareness. might be worth implmenenting in a later bot.
from PyQt6.uic import compileUiDir


class somewhatMoreAwarenessGreedy:
    def __init__(self, self_id):
        self.self_id = self_id
        self.type = "BG"
        self.chromosome = None
        self.risk_adversity = "MAX"
        self.number_type = 6
        # so RISK adversity is MAX (1) and High (0). It's not implemented yet.

    def set_chromosome(self, chromosome):
        self.chromosome = chromosome

    def get_number_type(self):
        return self.number_type

    # here is what teh scturecture is going to look like. store an array, and at that index store the value of what they ahve voted for.
    def get_vote(self, current_options_matrix, previous_votes=None):
        # this first part is exactly the saem as the betterGreedy - for an initial guess, we just have to use something. Pure probability is a go

            matrix = self.initialize_matrix(current_options_matrix)
            self.normalize_rows(matrix)

            cause_sums = None
            if previous_votes:
                cause_sums = self.apply_previous_votes(matrix, previous_votes)
                self.normalize_rows(matrix)

            col_probs = self.get_column_probabilities(matrix)
            our_row = current_options_matrix[self.self_id]
            risk_aversion = self.chromosome[0]
            majority_factor = self.chromosome[1]

            new_row = self.calculate_vote_row(our_row, col_probs, cause_sums, risk_aversion, majority_factor)
            return self.choose_best_vote(new_row, cause_sums)

        # if not previous_votes or len(previous_votes) == 0:
        #     # get the column sums
        #     num_cols = len(mutable_matrix[0])
        #     col_sums = [sum(mutable_matrix[row][col] for row in range(len(mutable_matrix))) for col in range(num_cols)]
        #
        #     # normalize those fetchers as well
        #     col_total = sum(col_sums)
        #     col_probs = [val / col_total for val in col_sums]
        #
        #     # create new value row, based off of the probability, utility and oru risk aversion factor.
        #     our_row = current_options_matrix[self_id] # this onle considers our row.
        #     new_row = [0]  # offset column 0
        #     risk_aversion = self.chromosome[0]
        #     for i, val in enumerate(our_row):
        #         if val > 0:
        #
        #             new_prob = col_probs[i + 1] ** risk_aversion # scalable risk stuff.
        #             new_row.append(new_prob * val)
        #
        #         else:
        #             new_row.append(0)
        #
        #
        #     # return the cause that has the highest value, adn then adjsut for the off by one error.
        #     return new_row.index(max(new_row)) - 1
        #
        # else: # this is where the fun begins
        #     if previous_votes:
        #
        #         self_id = self.self_id
        #         mutable_matrix = [[max(val + 1, 0) for val in [0] + row] for row in current_options_matrix]
        #
        #         # normalize, row by row
        #         for row in mutable_matrix:
        #             total = sum(row)
        #             if total > 0:
        #                 for i in range(len(row)):
        #                     row[i] /= total
        #
        #         # the previous vote information would likely be considered here - go through, and if they actually voted for it, add a 1 to it normalized and then renormalize it.
        #         keys = []
        #         for vote in previous_votes:
        #             keys.append(vote)
        #         player_dict = {}
        #         for player in previous_votes[keys[0]]:
        #             player_dict[player] = [] # make it a list
        #
        #         for key in keys:
        #             for player in previous_votes[key]:
        #                 player_dict[player].append(previous_votes[key][player])
        #
        #         cause_sums = {} # normalise this
        #         for i in range(len(current_options_matrix[0])+1):
        #             cause_sums[i] = 0
        #
        #         for key in player_dict: # just unfold the fetcher
        #             for i in range(len(player_dict[key])): # i is the player number
        #                 index = player_dict[key][i] + 1 # off by one error - negative one exists.
        #                 mutable_matrix[key][index] += 1 # so we add one to the value that they voted for
        #                 if self.self_id != key:
        #                     cause_sums[index] += 1
        #
        #
        #         for key in cause_sums:
        #             cause_sums[key] = cause_sums[key] / len(player_dict[next(iter(player_dict.keys()))]) # does this work? noramlize the normal votes
        #
        #         # normalize AGAIN for fun.
        #         for row in mutable_matrix:
        #             total = sum(row)
        #             if total > 0:
        #                 for i in range(len(row)):
        #                     row[i] /= total
        #
        #
        #         # get the column sums
        #         num_cols = len(mutable_matrix[0])
        #         col_sums = [sum(mutable_matrix[row][col] for row in range(len(mutable_matrix))) for col in range(num_cols)]
        #
        #         # normalize those fetchers as well
        #         col_total = sum(col_sums)
        #         col_probs = [val / col_total for val in col_sums]
        #
        #         # create new value row, based off of the probability, utility and oru risk aversion factor.
        #         our_row = current_options_matrix[self_id]
        #         new_row = [0]  # offset column 0
        #         risk_aversion = self.chromosome[0]
        #         majority_factor = self.chromosome[1]
        #         # if self.self_id == 5: # getting player 6
        #         #     print("Stop here")
        #         for i, val in enumerate(our_row):
        #             if val > 0:
        #                 new_prob = col_probs[i + 1] ** risk_aversion  # scalable risk stuff.
        #                 # this is trying to account for
        #                 if cause_sums[i+1] + 1 > len(player_dict) // 2:
        #                     new_row.append(new_prob * val  * majority_factor)
        #                 else:
        #                     new_row.append(new_prob * val)
        #
        #             else:
        #                 new_row.append(0)
        #
        #
        #         new_probability_sums = []
        #         for i in range(len(new_row)):
        #             expected_value = new_row[i] * cause_sums[i]
        #             new_probability_sums.append(expected_value)
        #
        #         new_vote = new_probability_sums.index(max(new_probability_sums)) - 1
        #
        #
        #         return new_vote




    def initialize_matrix(self, current_options_matrix): # creates padding and allows for 0 to be an option
        return [[max(val+1, 0) for val in [0] + row] for row in current_options_matrix]

    def normalize_rows(self, matrix):
        for row in matrix:
            total = sum(row)
            if total > 0:
                for i in range(len(row)):
                    row[i] /= total

    def get_column_probabilities(self, matrix):
        num_cols = len(matrix[0])
        col_sums = [sum(matrix[row][col] for row in range(len(matrix))) for col in range(num_cols)]
        total = sum(col_sums)
        return [val / total for val in col_sums]

    def apply_previous_votes(self, matrix, previous_votes):
        player_dict = {player: [] for player in previous_votes[next(iter(previous_votes))]}
        for key in previous_votes:
            for player in previous_votes[key]:
                player_dict[player].append(previous_votes[key][player])

        cause_sums = {i : 0.0 for i in range(len(matrix[0]))} # make sure it starts as a float, not an int.
        for key in player_dict:
            for i, vote in enumerate(player_dict[key]):
                index = vote + 1
                matrix[key][index] += 1
                if key != self.self_id:
                    cause_sums[index] += 1

        length = len(player_dict[next(iter(player_dict))])
        for key in cause_sums:
            cause_sums[key] = cause_sums[key] / length
        return cause_sums

    def calculate_vote_row(self, our_row, col_probs, cause_sums, risk_aversion, majority_factor):
        new_row = [0]
        for i, val in enumerate(our_row):
            if val > 0:
                new_prob = col_probs[i + 1] ** risk_aversion
                if cause_sums and cause_sums[i + 1] + 1 > len(our_row) // 2:
                    new_row.append(new_prob * val * majority_factor)
                else:
                    new_row.append(new_prob * val)
            else:
                new_row.append(0)
        return new_row

    def choose_best_vote(self, new_row, cause_sums=None):
        if cause_sums:
            expected_values = [new_row[i] * cause_sums.get(i, 0) for i in range(len(new_row))]
            return expected_values.index(max(expected_values)) - 1
        else:
            return new_row.index(max(new_row)) - 1