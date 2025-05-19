# ok so the biggest thing I think I noticed was that we need to implement tie breakers, and there were a few weird edge cases.
# so the biggest difference between humans and bots right now is their macro knoweldge of how things will impact other players
# even if an option is better for them adn they can get it to pass, they are more likely to pick the one that is better for society as a whole
# sometimes. Its really hard for me to tell. I am rapidly begininning to understand more acutely why gathering human data is the hardest fetching part of this thing.

import math
import random


class HumanAttempt1:
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
        rand_num = random.random()

        if previous_votes == None:
            # make default

        if previous_votes: # if there are previous votes to consider
            # if rand_num < 1.0:
            #     #print("silly time")
            #     last_key = list(previous_votes.keys())[-1]
            #     new_dict = {}
            #     for key in previous_votes:
            #         if key != last_key:
            #             new_dict[key] = previous_votes[key]
            #     previous_votes = new_dict
            #
            #     if previous_votes:
            cause_sums = self.apply_previous_votes(matrix, previous_votes)
            self.normalize_rows(matrix)
            # else:
            #     pass
            #     #print("noT silly time. ")

        col_probs = self.get_column_probabilities(matrix)
        our_row = current_options_matrix[self.self_id]
        risk_aversion = self.chromosome[0]
        majority_factor = self.chromosome[1]

        new_row = self.calculate_vote_row(our_row, col_probs, cause_sums, risk_aversion, majority_factor)
        current_vote = self.choose_best_vote(new_row, cause_sums)



        if current_vote == -1 and max(current_options_matrix[self.self_id]) >= 0: # if we can create some social lubrication here
            # at no cost to ourselves, we can select the 0 option and increase the rate of passing. this happened sometimes within human play.
            return current_options_matrix[self.self_id].index(max(current_options_matrix[self.self_id]))
        return current_vote


    def initialize_matrix(self, current_options_matrix): # completely changed this to better deal with negatives.
        flat = [val for row in current_options_matrix for val in row]
        global_min = min(flat)
        shift = -global_min if global_min < 0 else 0
        return [
            [val + shift for val in [0] + row]
            for row in current_options_matrix
        ]

    def normalize_rows(self, matrix):
        for row in matrix:
            total = sum(row)
            if total > 0:
                for i in range(len(row)):
                    row[i] /= total

    def get_column_probabilities(self, matrix):
        num_cols = len(matrix[0])
        col_sums = [sum(matrix[row][col] for row in range(len(matrix))) for col in range(num_cols)]

        min_sum = min(col_sums)
        if min_sum < 0:  # we have a negative number here....
            col_sums = [val + min_sum for val in col_sums]

        total = sum(col_sums)
        normalized_columns = [val / total for val in col_sums]
        return normalized_columns

    def apply_previous_votes(self, matrix, previous_votes):
        player_dict = {player: [] for player in previous_votes[next(iter(previous_votes))]}
        for key in previous_votes:
            for player in previous_votes[key]:
                player_dict[player].append(previous_votes[key][player])

        cause_sums = {i : 0.0 for i in range(len(matrix[0]))} # make sure it starts as a float, not an int.
        for key in player_dict:
            for i, vote in enumerate(player_dict[key]):
                index = vote + 1
                if key != self.self_id:
                    cause_sums[index] += 1

        length = len(player_dict[next(iter(player_dict))])
        for key in cause_sums:
            cause_sums[key] = cause_sums[key] / length
        return cause_sums

    def smooth_majority_bonus(self, ratio, majority_factor): # this is a sigmoid return to help us smooth out majorities. Works, just didn't help in teh case that I wanted it to.
        steepness = 10
        s = 1 / (1 + math.exp(-steepness * (ratio - 0.5)))
        return 1 + (majority_factor - 1) * s

    def calculate_vote_row(self, our_row, col_probs, cause_sums, risk_aversion, majority_factor):
        new_row = [0]
        total_voters = len(our_row)

        for i, val in enumerate(our_row): # our row is the players row within current option matrix.
            if val > 0:
                new_prob = col_probs[i + 1] ** risk_aversion
                if cause_sums:
                    alignment_ratio = cause_sums[i + 1] / total_voters
                    bonus = self.smooth_majority_bonus(alignment_ratio, majority_factor)
                    new_row.append(new_prob * val * bonus)
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