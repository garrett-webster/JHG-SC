


class greeddywMDP:
    def __init__(self, self_id):
        self.self_id = self_id
        self.type = "BG"
        self.chromosome = None
        self.risk_adversity = "MAX"
        self.number_type = 7

    def set_chromosome(self, chromosome):
        self.chromosome = chromosome

    def get_number_type(self):
        return self.number_type

    # here is what teh scturecture is going to look like. store an array, and at that index store the value of what they ahve voted for.
    def get_vote(self, current_options_matrix, previous_votes=None, cycle=0, max_cycle=3):
        # this first part is exactly the saem as the betterGreedy - for an initial guess, we just have to use something. Pure probability is a go
        if not previous_votes or len(previous_votes) == 0:
            new_row = self.standard_guess(current_options_matrix)
            # return cause with the highest expected outcome, then adjust for 1 off error.
            return new_row.index(max(new_row)) - 1

        else: # this is where the fun begins. we can do some funny suff.
            new_vote = -1 # so we have a default, just in case.
            if previous_votes:
                # avengers assemble
                self_id = self.self_id
                mutable_matrix, player_dict, cause_sums = self.formulate_guess(current_options_matrix, previous_votes)


                if len(player_dict[next(iter(player_dict.keys()))]) == 1:
                    new_vote = self.basic_but_better_vote(mutable_matrix, player_dict, cause_sums, current_options_matrix)

            return new_vote # gotta return this sooner or later

    def standard_guess(self, current_options_matrix):
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
        our_row = current_options_matrix[self_id]  # this onle considers our row.
        new_row = [0]  # offset column 0
        risk_aversion = self.chromosome[0]
        for i, val in enumerate(our_row):
            if val > 0:
                # new_row.append(col_probs[i + 1] * val) # straight expected value.
                new_prob = col_probs[i + 1] ** risk_aversion  # scalable risk stuff.
                new_row.append(new_prob * val)

            else:
                new_row.append(0)

        return new_row

    def formulate_guess(self, current_options_matrix, previous_votes):

        mutable_matrix = [[max(val + 1, 0) for val in [0] + row] for row in current_options_matrix]

        # normalize, row by row
        for row in mutable_matrix:
            total = sum(row)
            if total > 0:
                for i in range(len(row)):
                    row[i] /= total

        # the previous vote information would likely be considered here - go through, and if they actually voted for it, add a 1 to it normalized and then renormalize it.
        keys = []
        for vote in previous_votes:
            keys.append(vote)
        player_dict = {}
        for player in previous_votes[keys[0]]:
            player_dict[player] = []  # make it a list

        for key in keys:
            for player in previous_votes[key]:
                player_dict[player].append(previous_votes[key][player])

        cause_sums = {}  # normalise this
        for i in range(len(current_options_matrix[0]) + 1):
            cause_sums[i] = 0  # off by one error

        return mutable_matrix, player_dict, cause_sums

    def basic_but_better_vote(self, mutable_matrix, player_dict, cause_sums, current_options_matrix):

        for key in player_dict:  # just unfold the fetcher
            for i in range(len(player_dict[key])):  # i is the player number
                index = player_dict[key][i] + 1  # off by one error - negative one exists.
                mutable_matrix[key][index] += 1  # so we add one to the value that they voted for
                cause_sums[index] += 1

        # if len(player_dict[next(iter(player_dict.keys()))]) > 1:
        # print("aight stop here")

        for key in cause_sums:
            cause_sums[key] = cause_sums[key] / len(
                player_dict[next(iter(player_dict.keys()))])  # does this work? noramlize the normal votes

        # where anything over

        # so now we SHOULD have the average number of votes per cause, but I might want to consider just the smaller ones.
        # if (self.self_id == 5 or self.self_id == 6 or self.self_id == 4):
        # print("here are the cuase sums, ", cause_sums, " for agent ", self.self_id)

        # normalize AGAIN for fun.
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
        our_row = current_options_matrix[self.self_id]
        new_row = [0]  # offset column 0
        risk_aversion = self.chromosome[0]
        for i, val in enumerate(our_row):
            if val > 0:
                # new_row.append(col_probs[i + 1] * val) # straight expected value.
                new_prob = col_probs[i + 1] ** risk_aversion  # scalable risk stuff.
                new_row.append(new_prob * val)

            else:
                new_row.append(0)

        # if (self.self_id == 5 or self.self_id == 6 or self.self_id == 4):
        # print("here are the row probabilites, ", new_row, " for agent ", self.self_id)

        new_probability_sums = []
        for i in range(len(new_row)):
            expected_value = new_row[i] * cause_sums[i]
            new_probability_sums.append(expected_value)

        new_vote = new_probability_sums.index(max(new_probability_sums)) - 1