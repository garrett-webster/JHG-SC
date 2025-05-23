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
    def get_vote(self, current_options_matrix, previous_votes=None, cycle=0, max_cycle=3):
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