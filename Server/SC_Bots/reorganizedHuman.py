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
        self.social_lubrication = None
        self.bad_vote = None # if we have a bad situation, we wnat our vote to be consistent between cycles. hold on to it.

    def set_chromosome(self, chromosome): # allows me to set the chromosome at will.
        self.chromosome = chromosome

    def get_number_type(self): # used for logging.
        return self.number_type


    # returns the bots vote given the current option matrix and previous votes.
    def get_vote(self, current_options_matrix, previous_votes, cycle=0, max_cycle=3):
        matrix = self.initialize_matrix(current_options_matrix)  # creates no negatives w/ a positive shift
        self.normalize_rows(matrix)  # normalizes the rows and creates a probability distro.
        col_probs = [sum(col) for col in zip(*matrix)]  # how likely everything is to pass given what they like.
        total = sum(col_probs)
        col_probs = [val / total for val in col_probs]
        choice_list, choice_matrix = self.create_choice_matrix(current_options_matrix)
        total = sum(choice_list)
        choice_list = [val / total for val in choice_list]
        #print("this is the col probs ", col_probs, "\nand this is the choice ", choice_matrix)
        cause_sums = None  # used for generating bayseian prior - otherwise alwyas have col sums
        print("these are the col probs", col_probs)
        our_row = current_options_matrix[self.self_id]
        risk_aversion = self.chromosome[0]  # how likely we are to stay selfish
        majority_factor = self.chromosome[1]  # how much we care about majorities.
        stickiness_factor = self.chromosome[3]


        if len(previous_votes) == 0:  # if we have nothing passed in, we need to pass it in as SOMETHING.
            previous_votes = {}  # create an empty dict

            previous_votes[-1] = {}  # create spot for baysian prior.
            new_votes = {}  # clean new vote placement.

            # create bayseian prior (only for cycle 0)
            for i, player in enumerate(
                    current_options_matrix):  # can cycle through every vote, will disregard our own later.
                player_vote = self.calculate_vote_row(player, col_probs, cause_sums, risk_aversion, majority_factor, current_options_matrix, None)
                current_vote = player_vote.index(max(player_vote)) - 1  # get rid of selecting the best vote, just select what we like most.
                new_votes[i] = current_vote

            previous_votes[-1] = new_votes  # slap them in previous votes regardless.
            print("Here ar ethe expected previous votes ", previous_votes)

        cause_sums = self.apply_previous_votes(matrix, previous_votes)  # get the cause sums given our padded matrix and previous votes

        print(self.self_id, " and the cause sums ", cause_sums)
        if self.identify_outgroup(current_options_matrix, cause_sums, cycle, col_probs, max_cycle):
            #print(self.self_id, " has entered negative voting phase")
            return self.get_vote_negative(our_row, col_probs, cause_sums, risk_aversion, majority_factor, current_options_matrix, cycle, max_cycle, choice_list, choice_matrix)
        else:
            #print(self.self_id, "has entered positive voting phase")
            return self.get_vote_positive(our_row, col_probs, cause_sums, risk_aversion, majority_factor, current_options_matrix, cycle, max_cycle, previous_votes[cycle-1])

    def get_vote_negative(self, our_row, col_probs, cause_sums, risk_aversion, majority_factor, current_options_matrix, cycle, max_cycle, choice_list, choice_matrix):
        # so the cause sums show us what people are CURRENTLY voting for, I think I can use that and the choice matrix for more effective posturing.
        posturing_optimism = self.chromosome[2]

        posturable_cause = self.find_posturable_causes(col_probs, cause_sums, choice_list, current_options_matrix, choice_matrix) # can I run the same algorithm to find other outgroup players? Saber.

        current_winner = max(cause_sums, key=cause_sums.get)
        majority_vote = cause_sums[current_winner]
        new_cause_sums = copy.deepcopy(cause_sums)
        new_cause_sums[current_winner] = 0  # want to find second largers
        second_largest_cause = max(new_cause_sums, key=new_cause_sums.get)
        second_largest_vote = cause_sums[second_largest_cause]
        single_player_influence = 1 / len(current_options_matrix)

        # ok second problem, we only want to do the non posturing stuff, we want to make sure that stick to it.

        if majority_vote > second_largest_vote * posturing_optimism: # if there is no conceivable posturing to be done
            print("Negative no posture ", self.self_id, " and ", cycle)
            if self.bad_vote is not None:
                temp_bad_vote = self.bad_vote  # gives a way to return that vote while clearing the buffer.
                if cycle == max_cycle - 1:  # clear the buffer so we stay consistent.
                    self.bad_vote = None
                return temp_bad_vote
            else:
                random_number = random.random() # there are 2 possible strats, and for now its a coin flip.
                if random_number >= 0.5: # play greedy, least negative option, even if that cuase is winning.
                    self.bad_vote = current_options_matrix[self.self_id].index(max(current_options_matrix[self.self_id])) # return the least negative option.
                else:
                    winning_votes = [0,1,2,3] # return a random vote that isn't the winnign one.
                    winning_votes.remove(current_winner)
                    self.bad_vote = random.choice(winning_votes) - 1 # off by one error
                    self.bad_vote = current_options_matrix[self.self_id].index(max(current_options_matrix[self.self_id])) # return the least negative option.

                temp_bad_vote = self.bad_vote # gives a way to return that vote while clearing the buffer.
                if cycle == max_cycle - 1:  # clear the buffer so we stay consistent.
                    self.bad_vote = None
                return temp_bad_vote

        else: # try and get people to vote for the second most likely cause.
            # now I need to make sure that my vote isn't actually causing anything to pass, SO
            if cause_sums[current_winner] + single_player_influence < 0.5: # even with our vote, won't pass (safe?)
                return posturable_cause
            else:
                return -1 # with our vote, would pass, so abstain instead.

    def find_posturable_causes(self, col_probs, cause_sums, choice_list, current_option_matrix, choice_matrix):
        current_winner = max(cause_sums, key=cause_sums.get)
        first_tier_swingers = [] # no negatives, just happy go lucky kinda guys
        second_tier_swingers = [] # 1 negative, will swing between 2 options
        possible_swing_probabilities = [0] * ((len(current_option_matrix[0]))+1)
        for i, row in enumerate(current_option_matrix):
            curr_negatives = 0
            for val in row:
                if val <= 0: curr_negatives += 1 # consider 0 to be negative --> its not a useful option for them, and is not particuarly swingable.
            if curr_negatives == 0:
                first_tier_swingers.append(i)
            if curr_negatives == 1:
                second_tier_swingers.append(i)

        for player in first_tier_swingers: # consider all possible options, weighted
            #print("this is the player number ", player)
            player_choices = copy.deepcopy(choice_matrix[player])
           # print(" and this is the player choices ", player_choices)
            # next up, define their possible choices
            # remove their min option
            max_indicies = sorted(range(len(player_choices)), key=lambda i: player_choices[i], reverse=True)[:1]
            for index in max_indicies:
                if index != 0 and current_option_matrix[player][index-1] > 0: # make sure they aren't abstaining and that both of those options are positive for them
                    possible_swing_probabilities[index] += (1 / (len(player_choices)-1) * player_choices[index]) # so 33% times their normalized probability.

        for player in second_tier_swingers:
            player_choices = copy.deepcopy(choice_matrix[player])
            max_indicies = sorted(range(len(player_choices)), key=lambda i: player_choices[i], reverse=True)[:2]
            for index in max_indicies: # ok that should work much better acftually.
                if index != 0 and current_option_matrix[player][index-1] > 0: # this shouldn't actually do anything, actually.
                    possible_swing_probabilities[index] += (1 / ((len(player_choices)-2) * player_choices[index]))  # so 50% times their normalized probability.

            # they only have 2 optins to swing between, so they are more likley to swing to their other two options.

        total_sum = sum(possible_swing_probabilities)
        if total_sum > 0:
            possible_swing_probabilities = [val / total_sum for val in possible_swing_probabilities]

        possible_votes = []
        possible_swings = sorted(range(len(possible_swing_probabilities)), key=lambda i: possible_swing_probabilities[i], reverse=True)[:2] # only the  two best options
        for possible_vote in possible_swings: # ok so now that I have them, I shoudl really check if
            if possible_vote != 0 and possible_vote != current_winner: # abstaining is literally 0% fun, so don't consider it
                possible_votes.append(possible_vote)
        #print("these ar ethe possible swing votes for player ", self.self_id, possible_votes, "\n from considering ", first_tier_swingers, second_tier_swingers)
        if possible_votes:
            return possible_votes[0] - 1 # remember there is a off by one error.
        else:
            return -1

    def create_choice_matrix(self, current_options_matrix):
        current_options_matrix = [[0] + row for row in current_options_matrix] # append a 0 to it
        choice_list = [0] * len(current_options_matrix[0])
        choice_matrix = {}
        for i, row in enumerate(current_options_matrix):
            min_val = min(row) # lets avoid clamping for now IG.
            adjusted_row = [x - min_val for x in row]
            total = sum(adjusted_row)
            if total == 0:
                normalized_row = [0 for _ in adjusted_row]
            else:
                normalized_row = [x / total for x in adjusted_row]
            choice_matrix[i] = normalized_row
            choice_list = [choice_list[i] + normalized_row[i] for i in range(len(choice_list))]
        return choice_list, choice_matrix

    # our row --> our row from current_options_matrix, col_probs is probabiliyt of each cause passing from options matrix, cuase_sums represents the average votes per cause, risk_aversion adn marjoity factor
    # are chromosome stuffs, current_optinos matrix is there for fun and the cycle and max cycle are for social lubrication disabiling.
    def get_vote_positive(self, our_row, col_probs, cause_sums, risk_aversion, majority_factor, current_options_matrix, cycle, max_cycle, previous_votes_list):
        if self.self_id == 2 and cycle == 1:
            print("stop here bustert")
        new_row = self.calculate_vote_row(our_row, col_probs, cause_sums, risk_aversion,
                                          majority_factor, current_options_matrix, previous_votes_list)  # creates expected values list.
        print(self.self_id, " and their new row ", new_row)
        current_vote = new_row.index(max(new_row))-1 # get rid of selecting the best vote, just select what we like most.
        if current_vote == -1 and max(current_options_matrix[self.self_id]) >= 0:  # if we can create some social lubrication here
            if self.social_lubrication == None:
                self.social_lubrication = random.choice([True, False])
            if self.social_lubrication:
                current_vote = current_options_matrix[self.self_id].index(max(current_options_matrix[self.self_id]))
        if cycle == max_cycle -1: # if its the last round, turn it back off.
            self.social_lubrication = None
        return current_vote

    # I think I have simplified the outgroup to just "hey sucks for you"
    def identify_outgroup(self, current_options_matrix, cause_sums, cycle, col_probs, max_cycle):
        cur_negatives = 0
        for val in current_options_matrix[self.self_id]:
            if val < 0:
                cur_negatives += 1
        if cur_negatives == len(current_options_matrix[self.self_id]):
            return True
        else:
            return False



    def initialize_matrix(self, current_options_matrix): # completely changed this to better deal with negatives.
        flat = [val for row in current_options_matrix for val in row] # flatten the matrix so its easier to work with
        global_min = min(flat) # find the smallest number (likely -10 or -9)
        shift = -global_min if global_min < 0 else 0 # create the shift as the inverse of that number
        return [ # create the new, padded matrix with the shift and a new 0 entry as well, that is then also shifted.
            [val + shift for val in [0] + row]
            for row in current_options_matrix
        ]


    def normalize_rows(self, matrix): # create probability distribution
        for row in matrix:
            total = sum(row)
            if total > 0:
                for i in range(len(row)):
                    row[i] /= total
        return matrix

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

    def apply_previous_votes(self, matrix, previous_votes): # using evidence and baysiean prior, effect our numbers as such.
        player_dict = {player: [] for player in previous_votes[next(iter(previous_votes))]} # creates a player dict that records the lsit of votes
        for key in previous_votes: # populated dictionary with all votes
            for player in previous_votes[key]:
                player_dict[player].append(previous_votes[key][player])

        #print("these are the previous votes ", previous_votes)
        cause_sums = {i : 0.0 for i in range(len(matrix[0]))} # make sure it starts as a float, not an int.
        # if self.self_id == 0 and cycle == 1:
        #     print("Stop here on cycle 1")
        for key in player_dict: # go through and make sure that teh cause sums are all given an additional number for every vote
            for i, vote in enumerate(player_dict[key]):
                index = vote + 1
                if key != self.self_id:
                    cause_sums[index] += 1

        length = len(player_dict[next(iter(player_dict))]) # could I hard code this? yes. Did I? nope.
        for key in cause_sums: # normalize the length of the list so we cna understand its average votes per round.
            # probably beleive their first vote more? maybe? IDK. I want to use a relavancy bias and more
            cause_sums[key] = cause_sums[key] / length
        return cause_sums

    # where the magic happens - given our real utilities, col probs, the cuase_sums and our two chromosome factors, create an expected value list.
    # take in our utilities from the current option matrix, the likelyhood of each cause passing, our risk aversion and majority factor stuff, and go
    # this is the meat of our positive votes - all fine tunings either happen in here or in the chromosome.
    def calculate_vote_row(self, our_row, col_probs, cause_sums, risk_aversion, majority_factor, current_options_matrix, previous_votes_list):
        new_row = [0] # just create an empty row with a zero spot.
        total_voters = len(current_options_matrix) # canNOT be hardcoded. that will make everything blow up.
        my_influence = 1 / total_voters # how much our vote affects majoirty math.
        for i, val in enumerate(our_row): # our row is the players row within current option matrix.
            if val > 0: # if the value is non negative, then we cna be allowed to consider it.
                #new_prob = col_probs[i+1] ** (1 / risk_aversion) # higher risk aversion means we care more about passing than actual value.
                new_prob = col_probs[i+1] *  risk_aversion # higher risk aversion means we care more about passing than actual value.
                if cause_sums: # if we have some prior information
                    # that plus is to say, "if we throw our vote this way, how many votes will there be?". to counteract the previous if self.self_id stuff we saw earlier.
                    alignment_ratio = (cause_sums[i + 1]) / total_voters # consider how alinged we are with overall majority and if we tip it or not. no top means no jump
                    if alignment_ratio < 0.5 < alignment_ratio + my_influence: # if jumping actually changes the scale, we jump ship.
                        bonus = alignment_ratio ** (1/majority_factor) # take how alinged we are, and then apply that as a bonus to that new row.
                    else:
                        if previous_votes_list[self.self_id] == i: # if this is the same thing that we voted for last time, give it just a little bump. makes tie breakers stickier. maybe.
                            print("We should have alighted upon a previous vote ", self.self_id, " and vote ", previous_votes_list[self.self_id])
                            bonus = (alignment_ratio + my_influence) #* self.chromosome[3] # want to givne players a reason to stay where they are, to prevent slippage.
                        else:
                            bonus = alignment_ratio # Lets just see what this does.
                    new_row.append(new_prob * val * bonus) # append that new probability to teh list.
                else: # for bayseian prior, assume greedier behavior and go from there.
                    new_row.append(new_prob * val)
            else:
                new_row.append(0) # I probably need to reconsider exactly how this logic should work, but vote positive implies
                                    # it has good options that could pass, that we are much more interestd in what could pass that is good for us.
        return new_row # return that new row and let us ponder on it.

    def choose_best_vote(self, new_row, cause_sums=None):

        if cause_sums: # if we have prior information
            # consider the probability of that cuase passing with the expected value
            expected_values = [new_row[i] * cause_sums.get(i, 0) for i in range(len(new_row))]
            print(self.self_id, " and here are the expected values ", expected_values)
            return expected_values.index(max(expected_values)) - 1 # off by one error
        else: # no prior information, just return the greedy solution.
            return new_row.index(max(new_row)) - 1


    def choose_best_vote_bayseian(self, new_row, cause_sums=None): # literally no difference, just for debugging purposes.
        if cause_sums: # if we have prior information
            # consider the probability of that cuase passing with the expected value
            expected_values = [new_row[i] * cause_sums.get(i, 0) for i in range(len(new_row))]
            return expected_values.index(max(expected_values)) - 1 # off by one error
        else: # no prior information, just return the greedy solution.
            return new_row.index(max(new_row)) - 1