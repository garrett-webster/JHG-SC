# ok so the biggest thing I think I noticed was that we need to implement tie breakers, and there were a few weird edge cases.
# so the biggest difference between humans and bots right now is their macro knoweldge of how things will impact other players
# even if an option is better for them adn they can get it to pass, they are more likely to pick the one that is better for society as a whole
# sometimes. Its really hard for me to tell. I am rapidly begininning to understand more acutely why gathering human data is the hardest fetching part of this thing.

# so there are a couple of values that I want to understand better
# cause sums - how many people on average voted for a particular cause, given bayesian prior and evidence as gathered
# col probs - probability distribution of each cause passing, given their total sums.
#

from collections import defaultdict

class optimalHuman:
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
    def get_vote(self, current_options_matrix, previous_votes=None):
        # shift the matrix so that we have all positive values (makes normalization eaiser)
        matrix = [[0] + row for row in current_options_matrix]  # pad with the zero at the front.
        #matrix = self.initialize_matrix(current_options_matrix)
        #self.normalize_rows(matrix) # sort of turns it into a probability distribution

        cause_sums = None # used for generating bayseian prior - otherwise alwyas have col sums

        col_probs = self.get_column_probabilities(matrix) # how likely each column is to pass
        our_row = current_options_matrix[self.self_id] # our actual base utility given the original matrix.
        risk_aversion = self.chromosome[0] # how likely we are to stay selfish
        majority_factor = self.chromosome[1] # how much we care about majorities.

        if previous_votes is None: # if we have nothing passed in, we need to pass it in as SOMETHING.
            previous_votes = {} # create an empty dict

        previous_votes[-1] = {} # create spot for baysian prior.
        new_votes = {} # clean new vote placement.

        # create bayseian prior
        for i, player in enumerate(current_options_matrix): # can cycle through every vote, will disregard our own later.
            player_vote = self.calculate_vote_row(player, col_probs, cause_sums, risk_aversion, majority_factor)
            current_vote = self.choose_best_vote(player_vote, cause_sums)
            new_votes[i] = current_vote

        previous_votes[-1] = new_votes # slap them in previous votes regardless.

        cause_sums = self.apply_previous_votes(matrix, previous_votes) # get the cause sums given our padded matrix and previous votes

        new_row = self.calculate_vote_row(our_row, col_probs, cause_sums, risk_aversion, majority_factor) # creates expected values list.
        current_vote = self.choose_best_vote(new_row, cause_sums) # pick the best vote from our expected values
        if self.self_id == 5:
            print("Here is the col probsn ", col_probs, " and here are the previous_votes ", previous_votes, " and here is teh cause sums ", cause_sums, " and here is the new row ", new_row, ". theres another thing thats hard to get to. ")

        # social lubrication! if there is an opportunity to help the world, go for it. creates optimal results.
        if current_vote == -1 and max(current_options_matrix[self.self_id]) >= 0: # if we can create some social lubrication here
            # at no cost to ourselves, we can select the 0 option and increase the rate of passing. this happened sometimes within human play.
            return current_options_matrix[self.self_id].index(max(current_options_matrix[self.self_id]))
        return current_vote


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

    def apply_previous_votes(self, matrix, previous_votes): # using evidence and baysiean prior, effect our numbers as such.
        player_dict = {player: [] for player in previous_votes[next(iter(previous_votes))]} # creates a player dict that records the lsit of votes
        for key in previous_votes: # populated dictionary with all votes
            for player in previous_votes[key]:
                player_dict[player].append(previous_votes[key][player])

        cause_sums = {i : 0.0 for i in range(len(matrix[0]))} # make sure it starts as a float, not an int.
        for key in player_dict: # go through and make sure that teh cause sums are all given an additional number for every vote
            for i, vote in enumerate(player_dict[key]):
                index = vote + 1
                if key != self.self_id:
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
                new_prob = col_probs[i + 1] ** risk_aversion # create our new probbaility given our risk aversion and likelihood of cause passing.
                if cause_sums: # if we have some prior information
                    alignment_ratio = cause_sums[i + 1] / total_voters # consider how alinged we are with overall majority
                    bonus = alignment_ratio * majority_factor # just a linear relationship - considered sigmoid but it didn't make a difference.
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