# same as optimal human, but now we are going to use a negative strategy as well.
import random
import copy

class reorganizedHuman:
    def __init__(self, self_id):
        self.self_id = self_id # the id of ourself in realtion to other bots.
        self.type = "BG" # used for graphing purposes
        self.chromosome = None # used as a default holder, will be assinged later.
        self.risk_adversity = "MAX" # never used, actually.
        self.number_type = 6 # used for logging purposes.

    def set_chromosome(self, chromosome): # allows me to set the chromosome at will.
        self.chromosome = chromosome

    def get_number_type(self): # used for logging.
        return self.number_type




    # returns the bots vote given the current option matrix and previous votes.
    def get_vote(self, current_options_matrix, previous_votes=None, cycle=0, max_cycle=3):
        matrix = self.initialize_matrix(current_options_matrix)  # creates no negatives w/ a positive shift
        self.normalize_rows(matrix)  # normalizes the rows and creates a probability distro.
        col_probs = [sum(col) for col in zip(*matrix)]  # how likely everything is to pass given what they like.

        cause_sums = None  # used for generating bayseian prior - otherwise alwyas have col sums

        our_row = current_options_matrix[self.self_id]
        risk_aversion = self.chromosome[0]  # how likely we are to stay selfish
        majority_factor = self.chromosome[1]  # how much we care about majorities.

        if previous_votes is None:  # if we have nothing passed in, we need to pass it in as SOMETHING.
            previous_votes = {}  # create an empty dict

        previous_votes[-1] = {}  # create spot for baysian prior.
        new_votes = {}  # clean new vote placement.

        # create bayseian prior
        for i, player in enumerate(
                current_options_matrix):  # can cycle through every vote, will disregard our own later.
            player_vote = self.calculate_vote_row(player, col_probs, cause_sums, risk_aversion, majority_factor)
            current_vote = self.choose_best_vote_bayseian(player_vote, cause_sums)
            new_votes[i] = current_vote

        previous_votes[-1] = new_votes  # slap them in previous votes regardless.

        cause_sums = self.apply_previous_votes(matrix, previous_votes)  # get the cause sums given our padded matrix and previous votes


        print("player ", self.self_id, " cause sums ", cause_sums)
        if self.identify_outgroup(current_options_matrix, cause_sums):
            return self.get_vote_negative(our_row, col_probs, cause_sums, risk_aversion, majority_factor, current_options_matrix, cycle, max_cycle)
        else:
            return self.get_vote_positive(our_row, col_probs, cause_sums, risk_aversion, majority_factor, current_options_matrix)

    def get_vote_negative(self, our_row, col_probs, cause_sums, risk_aversion, majority_factor, current_options_matrix, cycle, max_cycle):
        # so the cuase sums are what kind of dictate if something is going to pass I think
        current_winner = max(cause_sums, key=cause_sums.get)
        majority_vote = cause_sums[current_winner]
        new_cause_sums = copy.deepcopy(cause_sums)
        new_cause_sums[current_winner] = 0 # want to find second largers
        second_largest_cause = max(new_cause_sums, key=new_cause_sums.get)
        second_largest_vote = cause_sums[second_largest_cause]
        if cycle == max_cycle - 1: # if its the end of the line, vote for nothing
            return -1  # final vote, so we are going to cast no vote and try to cause nothing to pass.

        if majority_vote >= second_largest_vote * 2: # if there is no conceivable posturing to be done
            return random.randrange(0, 2) # return a random causal vote, frustration reigns supreme in this guys mind.
        else: # try and get people to vote for the second most likely cause.
            return second_largest_cause - 1 # posture towards second most likely cause, and off by one error.



    def get_vote_positive(self, our_row, col_probs, cause_sums, risk_aversion, majority_factor, current_options_matrix):
        new_row = self.calculate_vote_row(our_row, col_probs, cause_sums, risk_aversion,
                                          majority_factor)  # creates expected values list.
        current_vote = self.choose_best_vote(new_row, cause_sums)  # pick the best vote from our expected values

        # print("this is the id ", self.self_id, " and this is the curr option row ", current_options_matrix[self.self_id], " and our current vote ", current_vote)
        # social lubrication! if there is an opportunity to help the world, go for it. creates optimal results.
        if current_vote == -1 and max(
                current_options_matrix[self.self_id]) >= 0:  # if we can create some social lubrication here
            # at no cost to ourselves, we can select the 0 option and increase the rate of passing. this happened sometimes within human play.
            return current_options_matrix[self.self_id].index(max(current_options_matrix[self.self_id]))
        return current_vote

    def identify_outgroup(self, current_options_matrix, cause_sums, previous_votes):
        pass # the purpose of this function is to allow us to realize if we are part of an "outgroup"
        if self.self_id == 3 or self.self_id == 8:
            print("STOP HERE CHEIF")
        # I think the easiest way to od this is to
        # find the indexes of the best 2 options, or the most popular options
        # from there, if one fo THOSE is greater than or equal to 0, we can do a positive vote and go from there
        # however, if neither of the 2 best options are within our best interest, we are going to go for the connivign option.
        # so an example of this edgecase can be found in round 16, wherein the human players 4 and 9 were both voting for cause 2, a
        # and becuase of this, they did seem to successfully commit players 2,3,5,6 to vote for cause 2 and lose the majority.
        # so lets see if we can't replicate some of that behavior here.
        current_winner = max(cause_sums, key=cause_sums.get)
        new_cause_sums = copy.deepcopy(cause_sums)
        new_cause_sums[current_winner] = 0  # want to find second largers
        second_largest_cause = max(new_cause_sums, key=new_cause_sums.get)
        possibleReturnBig = current_options_matrix[self.self_id][current_winner-1]
        possibleReturnSmall = current_options_matrix[self.self_id][second_largest_cause-1]
        if possibleReturnBig > 0 and possibleReturnSmall > 0:
            return False # we are part of a main group, don't worry about it
        else:
            print("OUTGROUP DETECTED, OPINION REJECTED!")
            return True #


    def initialize_matrix(self, current_options_matrix): # completely changed this to better deal with negatives.
        flat = [val for row in current_options_matrix for val in row] # flatten the matrix so its easier to work with
        global_min = min(flat) # find the smallest number (likely -10 or -9)
        shift = -global_min if global_min < 0 else 0 # create the shift as the inverse of that number
        return [ # create the new, padded matrix with the shift and a new 0 entry as well.
            [val + shift for val in [0] + row]
            for row in current_options_matrix
        ]

    def normalize_rows(self, matrix): # create probability distribution
        for row in matrix:
            total = sum(row)
            if total > 0:
                for i in range(len(row)):
                    row[i] /= total

    def get_our_row(self, current_options_matrix):
        shift = max(-min(current_options_matrix[self.self_id]), 0)
        our_row = [val + shift for val in current_options_matrix[self.self_id]]
        return our_row

    def get_column_probabilities(self, matrix): # get probability distribution based on liklihood of passing. may want to rework into choice matrix. Worth looking at later.

        scores = [0] * len(matrix[0])
        for row in matrix:
            # this should do what I wanted to do better.
            shift = max(-min(row), 0)
            row = [var + shift for var in row]
            total = sum(row)
            row = [var / total for var in row]
            for index in range(len(row)):
                scores[index] += row[index]


        return scores # we have significantly shifted the math here. wild.

        # num_cols = len(matrix[0]) # this is the old code. want to see somethind.
        # col_sums = [sum(matrix[row][col] for row in range(len(matrix))) for col in range(num_cols)]
        #
        # min_sum = min(col_sums) # find the min and shift it up
        # min_sum = -min_sum if min_sum < 0 else 0 # old bug was here. fix that.
        # if min_sum < 0:  # we have a negative number here....
        #     col_sums = [val + min_sum for val in col_sums]
        # # just normalizing the col sums here. Reason teh above bug didn't matter - normalization made it all equal anyway.
        # total = sum(col_sums)
        # normalized_columns = [val / total for val in col_sums]
        # return normalized_columns

    def apply_previous_votes(self, matrix, previous_votes): # using evidence and baysiean prior, effect our numbers as such.
        player_dict = {player: [] for player in previous_votes[next(iter(previous_votes))]} # creates a player dict that records the lsit of votes
        for key in previous_votes: # populated dictionary with all votes
            for player in previous_votes[key]:
                player_dict[player].append(previous_votes[key][player])

        cause_sums = {i : 0.0 for i in range(len(matrix[0]))} # make sure it starts as a float, not an int.
        # if self.self_id == 0 and cycle == 1:
        #     print("Stop here on cycle 1")
        for key in player_dict: # go through and make sure that teh cause sums are all given an additional number for every vote
            for i, vote in enumerate(player_dict[key]):
                index = vote + 1
                if key != self.self_id:
                    if index == 4:
                        print("stop here")
                    cause_sums[index] += 1

        length = len(player_dict[next(iter(player_dict))]) # could I hard code this? yes. Did I? nope.
        for key in cause_sums: # normalize the length of the list so we cna understand its average votes per round.
            cause_sums[key] = cause_sums[key] / length
        return cause_sums

    # where the magic happens - given our real utilities, col probs, the cuase_sums and our two chromosome factors, create an expected value list.
    def calculate_vote_row(self, our_row, col_probs, cause_sums, risk_aversion, majority_factor):
        new_row = [0] # just create an empty row with a zero spot.
        total_voters = len(our_row) # canNOT be hardcoded. that will make everything blow up.

        for i, val in enumerate(our_row): # our row is the players row within current option matrix.
            if val > 0: # if the value is non negative, then we cna be allowed to consider it.
                #new_prob = col_probs[i + 1] ** risk_aversion # create our new probbaility given our risk aversion and likelihood of cause passing.
                new_prob = col_probs[i + 1] * risk_aversion # create our new probbaility given our risk aversion and likelihood of cause passing.
                if cause_sums: # if we have some prior information
                    alignment_ratio = cause_sums[i + 1] / total_voters # consider how alinged we are with overall majority
                    if alignment_ratio > 0.55:
                        bonus = alignment_ratio * majority_factor # just a linear relationship - considered sigmoid but it didn't make a difference.
                    else:
                        bonus = 0.5
                    new_row.append(new_prob * val * bonus) # append that new probability to teh list.
                else: # ironically, used only in the best guess creation thing.
                    new_row.append(new_prob * val)
            else:
                new_row.append(0) # if a negative value, then just return a 0. no reason to vote for it.

        return new_row # return that new row and let us ponder on it.

    def choose_best_vote(self, new_row, cause_sums=None):

        if cause_sums: # if we have prior information
            # consider the probability of that cuase passing with the expected value
            expected_values = [new_row[i] * cause_sums.get(i, 0) for i in range(len(new_row))]
            return expected_values.index(max(expected_values)) - 1 # off by one error
        else: # no prior information, just return the greedy solution.
            return new_row.index(max(new_row)) - 1


    def choose_best_vote_bayseian(self, new_row, cause_sums=None):
        if cause_sums: # if we have prior information
            # consider the probability of that cuase passing with the expected value
            expected_values = [new_row[i] * cause_sums.get(i, 0) for i in range(len(new_row))]
            return expected_values.index(max(expected_values)) - 1 # off by one error
        else: # no prior information, just return the greedy solution.
            return new_row.index(max(new_row)) - 1