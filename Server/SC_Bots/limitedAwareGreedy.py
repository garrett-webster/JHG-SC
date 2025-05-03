import copy
from collections import Counter
import numpy as np
from pyqtgraph.examples.colorMapsLinearized import previous


class limitedAwarenessGreedy:
    def __init__(self, self_id):
        self.self_id = self_id
        self.type = "BG"
        self.chromosome = None
        self.risk_adversity = "MAX"
        # so RISK adversity is MAX (1) and High (0). It's not implemented yet.

    def set_chromosome(self, chromosome):
        self.chromosome = chromosome

    # here is what teh scturecture is going to look like. store an array, and at that index store the value of what they ahve voted for.
    def get_vote(self, current_options_matrix, previous_votes=None):
        # this first part is exactly the saem as the betterGreedy - for an initial guess, we just have to use something.
        if not previous_votes or len(previous_votes) == 0:
            self_id = self.self_id
            mutable_matrix = [[max(val + 1, 0) for val in [0] + row] for row in current_options_matrix]

            # normalize, row by row
            for row in mutable_matrix:
                total = sum(row)
                if total > 0:
                    for i in range(len(row)):
                        row[i] /= total



            # get the column sums
            num_cols = len(mutable_matrix[0])
            col_sums = [sum(mutable_matrix[row][col] for row in range(len(mutable_matrix))) for col in range(num_cols)]

            # normalize those fetchers as well
            col_total = sum(col_sums)
            col_probs = [val / col_total for val in col_sums]

            # create new value row, based off of the probability, utility and oru risk aversion factor.
            our_row = current_options_matrix[self_id] # this onle considers our row.
            new_row = [0]  # offset column 0
            risk_aversion = self.chromosome[0]
            for i, val in enumerate(our_row):
                if val > 0:
                    #new_row.append(col_probs[i + 1] * val) # straight expected value.
                    new_prob = col_probs[i + 1] ** risk_aversion # scalable risk stuff.
                    new_row.append(new_prob * val)

                else:
                    new_row.append(0)


            # return the cause that has the highest value, adn then adjsut for the off by one error.
            return new_row.index(max(new_row)) - 1

        else: # this is where the fun begins
            if previous_votes:
                pass # no switching info, so just modify the probabilities like we have expected.
                    # if the votes are unusual, we might have to cooperate differently.
                    # for testing purposes, I might have the random bot always make the SAME decision so that they can be infulenced by the others.
                self_id = self.self_id
                mutable_matrix = [[max(val + 1, 0) for val in [0] + row] for row in current_options_matrix]

                # normalize, row by row
                for row in mutable_matrix:
                    total = sum(row)
                    if total > 0:
                        for i in range(len(row)):
                            row[i] /= total

                # the previous vote information would likely be considered here - go through, and if they actually voted for it, add a 1 to it normalized and then renormalize it.
                for vote in previous_votes:
                    pass

                # get the column sums
                num_cols = len(mutable_matrix[0])
                col_sums = [sum(mutable_matrix[row][col] for row in range(len(mutable_matrix))) for col in range(num_cols)]

                # normalize those fetchers as well
                col_total = sum(col_sums)
                col_probs = [val / col_total for val in col_sums]

                # create new value row, based off of the probability, utility and oru risk aversion factor.
                our_row = current_options_matrix[self_id]
                new_row = [0]  # offset column 0
                risk_aversion = self.chromosome[0]
                for i, val in enumerate(our_row):
                    if val > 0:
                        # new_row.append(col_probs[i + 1] * val) # straight expected value.
                        new_prob = col_probs[i + 1] ** risk_aversion  # scalable risk stuff.
                        new_row.append(new_prob * val)

                    else:
                        new_row.append(0)

                return new_row.index(max(new_row)) - 1

















