import copy
import math
import random
from collections import Counter
from operator import index
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt


from Server.Node import Node
from Server.SC_Bots.humanAttempt2 import humanAttempt2
from Server.OptionGenerators.options_creation import generate_two_plus_one_groups_options_best_of_three, generate_two_plus_one_groups
from Server.SC_Bots.Greedy import GreedyBot
from Server.SC_Bots.SocialWelfare import SocialWelfareBot
from Server.SC_Bots.Random import RandomBot
from Server.SC_Bots.somewhatMoreAwareGreedy import somewhatMoreAwarenessGreedy
from Server.SC_Bots.optimalHuman import optimalHuman
from Server.SC_Bots.reorganizedHuman import reorganizedHuman
from Server.SC_Bots.possibleCheetahBot import cheetahBot

NUM_CAUSES = 3


class Social_Choice_Sim:
    def __init__(self, total_players, num_causes, num_humans, options_generator, cycle=0, round=0, chromosomes="", scenario="", group="", total_order=None):
        self.options_generator = options_generator
        if total_order == None: # generating it non server side
            self.total_order = self.create_total_order(total_players, num_humans)
        else: # if created with server, spoon feed it.
            self.total_order = total_order
        # just a bunch of base setters.

        self.total_players = total_players
        self.num_humans = num_humans
        self.num_bots = total_players - num_humans
        self.num_causes = num_causes
        self.cycle = cycle # set these for graphing and logging purposes, we usually set these round by round and cycle by cycle for logging purposes.
        self.round = round
        self.rad = 5  # used for graphing the dots on the board.


        self.players = self.create_players() # ??? This might be used for multiplayer functionality.
        self.outer_points = []
        self.causes_rads = []
        self.causes = self.create_cause_nodes() # graphing stuff.

        self.player_nodes = [] # also graphing stuff.

        self.chromosome_string = "" # holds the file name of the chromosome baering file.
        self.chromosomes = self.set_chromosomes(chromosomes) # self.chromosomes contains the full list of all chromosomes.

        # sets the scenario
        self.scenario_string = Path(scenario).name

        # create the bots, first getting number and type from scenario and then setting the chromosomes from the chromsomes.
        self.bot_type = self.set_bot_list(scenario)
        self.bots = self.create_bots(self.total_order) # make sure to pull this from the right spot.
        self.bot_list_as_string = self.create_bot_list_as_string(self.bots)
        self.set_bot_chromosomes(self.chromosomes)

        # group stuff - all used under set group, and then there are defualts just in case.
        self.group = -1 # doesn't exist, let me know it hasn't been set.
        self.sc_groups = -1 # no group exists, can ignore.
        self.group_option = group

        # the bread and butter of the sim. set under start round.
        self.current_options_matrix = {}

        # holds all the results from all the games we have played with this current sim
        self.results = {} # holds all of our results from long term simulations before graphing.
        self.cooperation_score = 0
        self.num_rounds = 0 # used in various spots for graphing and whatnot. not terribly important.
        self.current_results = [] # holds the results from the last "return win" call, which we can access later.
        self.results = self.create_results()  # dict key: player id, attribute: list of all utility changes per round.
        self.total_types = self.create_total_types() # holds EVERYONE. now we gotta do a significant amount of refactoring.
        self.choice_matrix = [0] * (self.num_causes + 1)
        self.last_option = 0
        # self.all_numbers_matrix = [0] * 21
        self.all_votes = {}
        self.winning_probability = []

    def create_total_order(self, total_players, num_humans):
        num_bots = total_players - num_humans
        new_list = []
        for bot in range(num_bots):
            new_list.append("B" + str(bot))
        for human in range(num_humans):
            new_list.append("P" + str(human))

        return new_list



    def create_results(self):
        self.results = {}
        for i in range(self.total_players):  # total_players
            self.results[i] = []  # just throw in all the utilites
        return self.results


    def set_chromosome(self, chromosomes):
        self.chromosome_string = Path(chromosomes).name
        return self.chromosome_string

    # here is the offender. this is the thing we have to rework.
    def create_total_types(self):
        if self.total_order is None:
            return self.bot_type
        self.total_types = self.bot_type
        if self.total_players != self.num_humans or self.total_players != self.num_bots: # if there is a mistmatch
            for index, player in enumerate(self.total_order):
                if player.startswith("P"):
                    self.total_types.insert(index, -1)
        #print("these are the new total types ", self.total_types)
        return self.total_types


    def set_group(self, group_option):
        if group_option == "":
            self.group = -1
            self.sc_groups = -1
        else:
            self.group = group_option
            self.sc_groups = generate_two_plus_one_groups(self.total_players, group_option)



    def create_bots(self, total_order):
        bots_array = []
        bot_indexes = []
        if total_order is not None:
            for index, object in enumerate(total_order):
                if object.startswith("B"):
                    bot_indexes.append(index)

        if len(self.bot_type) != self.num_bots:
            # lets fix this logic right here and now.
            self.bot_type = [self.bot_type[0]] * self.num_bots

        for i, bot_type in enumerate(self.bot_type):
            current_index = bot_indexes.pop(0)
            #print("this the bot index that we are adding ", current_index)
            bots_array.append(self.match_bot_type(bot_type, current_index))

        return bots_array

    # I am not changing this. I don't bother with it. It does what it does and I don't want to refactor all the stubbins.
    def match_bot_type(self, bot_type, index):
        new_bot = None
        bot_type = int(bot_type)
        if bot_type == 0:
            new_bot = (RandomBot(index))
        if bot_type == 1:
            new_bot = (SocialWelfareBot(index))
        if bot_type == 2:
            new_bot = (GreedyBot(index))
        if bot_type == 6:
            new_bot = (somewhatMoreAwarenessGreedy(index))
        if bot_type == 7:
            new_bot = (optimalHuman(index))
        if bot_type == 8:
            new_bot = (humanAttempt2(index))
        if bot_type == 9:
            new_bot = (reorganizedHuman(index))
        if bot_type == 10:
            new_bot = (cheetahBot(index))


        return new_bot # the matched bot that we were looking for.

    def create_players(self):
        players = {}
        for i in range(self.total_players):
            players[str(i)] = 0
        return players


    def set_bot_chromosomes(self, chromosomes):
        if len(chromosomes) != len(self.bots):
            chromosomes = [chromosomes[0]] * len(self.bots)


        for i in range(len(self.bots)):
            self.bots[i].set_chromosome(chromosomes[i])


    def apply_vote(self, winning_vote):
        for i in range(self.total_players):
            self.players[str(i)] += self.current_options_matrix[i][int(winning_vote)]


    def create_options_matrix(self):
        # if self.sc_groups != -1:
        #     self.current_options_matrix = generate_two_plus_one_groups_options_best_of_three(self.sc_groups)
        # else: # so we have to generate noise to try and "mimic" the other stuff.
        #     self.current_options_matrix = [[random.randint(-8, 8) for _ in range(self.num_causes)] for _ in range(self.total_players)]
        #     noise_matrix = [[random.randint(-2, 2) for _ in range(self.num_causes)] for _ in range(self.total_players)]
        #     self.current_options_matrix = [
        #         [original + noise for original, noise in zip(row, noise_row)]
        #         for row, noise_row in zip(self.current_options_matrix, noise_matrix)
        #     ]

        self.current_options_matrix = self.options_generator.generateOptions()
        return self.current_options_matrix # because why not

    def get_scenario(self):
        return self.scenario_string

    def get_chromosome(self):
        return self.chromosomes

    def get_causes(self):
        return self.causes


    def get_current_options_matrix(self):
        return self.current_options_matrix


    def get_player_nodes(self):
        return self.player_nodes


    def get_nodes(self):
        return self.player_nodes + self.causes


    def get_player_utility(self):
        return self.players

    def get_cycle(self):
        return self.cycle


    def get_bot_type(self):
        return self.bot_type

    def set_final_votes(self, zero_idx_votes):
        self.final_votes = zero_idx_votes


    def set_rounds(self, num_rounds):
        self.num_rounds = num_rounds

    def add_coop_score(self):
        self.cooperation_score = self.cooperation_score + 1

    def set_coop_score(self, coop_score):
        self.cooperation_score = coop_score


    def get_group(self):
        return self.group


    def get_votes(self, previous_votes=None, round=0, cycle=0, max_cycle=3): # generic get votes for all bot types. Not optimized for a single chromosome
        self.round = round
        self.cycle = cycle
        all_votes = {}
        bot_indexes = []
        for i, thing in enumerate(self.total_types):
            all_votes[i] = -1 # just assume they are all abstaining
            if thing != -1:
                bot_indexes.append(i)

        bot_votes = {}
        final_votes = None
        for i, bot in enumerate(self.bots):
            #print("this is the bot id ", bot.self_id, " an dthis is the i index ", i)
            final_votes = bot.get_vote(self.current_options_matrix, previous_votes, cycle, max_cycle)
            all_votes[bot_indexes.pop(0)] = final_votes

        self.final_votes = all_votes


        return all_votes

    # this exists of necessity of needing to add player votes to this fetcher. Bot votes only are easy, but we need player votes as well.
    def record_votes(self, current_votes, cycle_number):
        self.all_votes[cycle_number] = current_votes

    # tallies if there is a winning vote and does a bunch of stuff with it for tracking purposes.
    def return_win(self, all_votes):
        self.current_results = []
        total_votes = all_votes
        #self.final_votes = all_votes
        winning_vote_count = Counter(total_votes.values()).most_common(1)[0][1]
        winning_vote = Counter(total_votes.values()).most_common(1)[0][0]

        col_sums = [sum(col) for col in zip(*self.current_options_matrix)]
        col_sums.insert(0, 0)

        sorted_column_sums = sorted(col_sums, reverse=True)

        index = int(winning_vote) + 1
        self.choice_matrix[sorted_column_sums.index(col_sums[index])] += 1
        self.last_option = sorted_column_sums.index(col_sums[index])


        if not (winning_vote_count > len(total_votes) // 2):
            winning_vote = -1

        if winning_vote != -1: # if its -1, then nothing happend. NOT the last entry in the fetcher. that was a big bug that flew under the radar.
            for i in range(len(total_votes)):
                self.current_results.append(self.current_options_matrix[i][winning_vote])
            self.add_coop_score()
        else:
            for i in range(len(total_votes)):
                self.current_results.append(0)


        choice_list = self.create_choice_matrix(self.current_options_matrix)
        self.winning_probability.append(choice_list[winning_vote+1])


        return winning_vote, self.current_results

    # this one has one goal. is there a winning vote.
    def return_win_without_silly(self, all_votes):
        self.current_results = []
        total_votes = all_votes
        winning_vote_count = Counter(total_votes.values()).most_common(1)[0][1]
        winning_vote = Counter(total_votes.values()).most_common(1)[0][0]

        if not (winning_vote_count > len(total_votes) // 2):
            winning_vote = -1

        if winning_vote != -1: # if its -1, then nothing happend. NOT the last entry in the fetcher. that was a big bug that flew under the radar.
            for i in range(len(total_votes)):
                self.current_results.append(self.current_options_matrix[i][winning_vote])
        else:
            for i in range(len(total_votes)):
                self.current_results.append(0)

        return winning_vote, self.current_results # literally just returns who won. thats it.


    def set_choice_matrix(self, new_choice_matrix):
        self.choice_matrix = new_choice_matrix

    def get_last_option(self):
        return self.last_option

    def save_results(self):
        for player in range(len(self.current_results)):
            self.results[player].append(self.current_results[player])

    def get_new_utilities(self):
        return self.results



    # SUM: sets up the bot list with a current file. Will override any potential single types as those seem to be more important. will likely be refactored.
    def set_bot_list(self, current_file):
        if current_file != "":
            with open(current_file, "r") as file:
                for line in file:
                    if line.startswith("#"):
                        continue # skip the comment lines
                    bot_types = [int(x) for x in line.strip().split(",")]
                    break # stop when teh numbers are over.

        else:
            num_bots = self.total_players - self.num_humans
            bot_types = [2] * num_bots

        return bot_types

    def set_chromosomes(self, current_file):
        chromosomes_list = []
        if isinstance(current_file, str):

            if current_file != "":
                with open(current_file, "r") as file:
                    for line in file:
                        if line.startswith("#"):
                            continue
                        parts = line.strip().split(",")
                        if parts:  # make sure the line isn't empty
                            try:
                                parts_list = []
                                for i in range(1, len(parts)):
                                    parts_list.append(float(parts[i]))
                                chromosomes_list.append(parts_list)
                            except ValueError:
                                pass  # skip lines that don't have valid integers
            else:
                    chromosomes_list = [[1]] * self.num_bots

        else:
            chromosomes_list = current_file
        self.chromosome_string = Path(current_file).name
        return chromosomes_list

    # default to groups being None,
    def start_round(self, sc_groups=None):
        #if sc_groups != None:
            #self.sc_groups = sc_groups
        self.current_options_matrix = self.create_options_matrix() # cause we have to create groups.
        #     [
        #     [-4, -8,-2],
        #     [6,-7,1],
        #     [7,-5,0],
        #     [2,-7,1],
        #     [-2,2,8],
        #     [-4,-7,5],
        #     [-8,-2,-7],
        #     [1,-1,5],
        #     [-3,-1,-3],
        # ]
        # self.current_options_matrix = [
        #     [-3,5,10],
        #     [10,0,0],
        #     [10,0,0],
        #     [10,0,0],
        #     [10,0,0],
        #     [10,0,0],
        #     [10, 0, 0],
        #     [10, 0, 0],
        #     [10,0,0]]
        self.current_options_matrix = [
            [
                3,
                -1,
                -8
            ],
            [
                5,
                -5,
                -7
            ],
            [
                5,
                1,
                9
            ],
            [
                -7,
                -6,
                -4
            ],
            [
                2,
                -2,
                5
            ],
            [
                -2,
                7,
                -9
            ],
            [
                1,
                1,
                1
            ],
            [
                0,
                -6,
                -4
            ],
            [
                -1,
                4,
                -9
            ]
        ]
        # self.current_options_matrix = [
        #     [-2,2,-6],
        #     [-2,5,-4],
        #     [-9,1,-1],
        #     [-4,1,7],
        #     [7,5,4],
        #     [-2,-3,0],
        #     [-3,-1,-2],
        #     [-1,0,9],
        #     [-2,-3,-1]]

        self.set_new_options_matrix(self.current_options_matrix)
        self.player_nodes = self.create_player_nodes()

    def make_native_type(self, return_values):
        new_dict = {}
        for key, inner_dict in return_values.items():
            new_key = key.item() if isinstance(key, np.integer) else key
            new_inner_dict = {}
            for item, value in inner_dict.items():
                new_inner_dict[item] = value.item if isinstance(value, np.generic) else value
            new_dict[new_key] = new_inner_dict
        return new_dict

    def compile_nodes(self):
        player_nodes = self.get_player_nodes()
        causes = self.get_causes()
        all_nodes = causes + player_nodes
        return all_nodes

    def get_bot_votes(self, current_options_matrix):
        votes = {}
        for i, player in enumerate(self.players):
            if player.getType() != "Human":
                votes[str(i)] = player.getVote(current_options_matrix, i)
        return votes



    def prepare_graph(self):
        self.create_player_nodes()
        current_nodes = self.compile_nodes()
        current_node_json = []
        for node in current_nodes:
            current_node_json.append(node.to_json())

        winning_vote_list = {} # key is the cycle, and the attribute is the winning vote of that cycle.
        for cycle in self.all_votes:
            winning_vote_list[cycle], _ = self.return_win_without_silly(self.all_votes[cycle])


        group = self.get_group()
        # so now what we do instead is that we take in a winning vote list cycle by cycle and spit it out as necessary.
        return current_node_json, self.all_votes, winning_vote_list, self.current_options_matrix, self.total_types, self.scenario_string, group, self.round, self.cycle, self.chromosome_string

    def get_results(self):
        #print("Aight were is the zero, its gotta be under num_rounds right?") literally zero clue whawt this print statement was supposed to be for.
        cooperation_score = self.cooperation_score / self.num_rounds  # as a percent, how often we cooperated. (had a non negative cause pass)
        return self.results, cooperation_score, self.total_types, self.num_rounds, self.scenario_string, self.group, self.chromosome_string

    def get_everything_for_logger(self):
        self.create_player_nodes()
        current_nodes = self.compile_nodes()
        current_node_json = []
        for node in current_nodes:
            current_node_json.append(node.to_json())

        current_cooperation_score = copy.copy(self.cooperation_score)
        current_choice_matrix = copy.copy(self.choice_matrix)
        winning_vote, _ = self.return_win(self.final_votes)
        self.choice_matrix = current_choice_matrix
        self.set_coop_score(current_cooperation_score)  # reset it bc the above does silly things.
        cooperation_score = self.cooperation_score / self.num_rounds  # as a percent, how often we cooperated. (had a non negative cause pass)


        return current_node_json, self.final_votes, winning_vote, self.current_options_matrix, self.results, cooperation_score, self.total_types, self.num_rounds, self.scenario_string, self.group, self.cycle, self.round

    def create_bot_list_as_string(self, bots_list):
        bots_as_string = []
        for bot in bots_list:
            bots_as_string.append(str(bot.get_number_type()))
        return bots_as_string

    def set_new_options_matrix(self, new_optins_matrix):
        self.current_options_matrix = new_optins_matrix

    def set_player_nodes(self, new_options_matrix):
        self.current_options_matrix = new_options_matrix
        self.player_nodes = self.create_player_nodes()

    # def print_col_passing(self):
    #     total = sum(self.choice_matrix)
    #     normalized_list = [val / total for val in self.choice_matrix]
    #     print("ratio passing ", normalized_list)
    #
    #     total = sum(self.all_numbers_matrix)
    #     normalized_list = [val / total for val in self.all_numbers_matrix]
    #     print("number distro ", normalized_list)
    #     below_zero = sum(normalized_list[0:9])
    #     zero = normalized_list[10]
    #     above_zero = sum(normalized_list[11:20])
    #     print("here are below zero ", below_zero, " here are above zero ", above_zero, " and here is zero ", zero)
    #     #self.create_heat_map(normalized_list) # used to create a heatmap of number distro, probably deleteable.
    #
    #
    # def create_heat_map(self, data):
    #     array = np.array(data).reshape(3, 7)  # shape it however you want
    #
    #     # Create heatmap
    #     plt.figure(figsize=(8, 4))
    #     #sns.heatmap(array, annot=True, cmap="YlGnBu", cbar=True)
    #     plt.title("Heatmap of Number Distribution")
    #     plt.show()



    ###--- NODE CREATION FOR FRONT END. NOT USEFUL FOR GENETIC STUFF. ---###


    def create_cause_nodes(self):
        displacement = (2 * math.pi) / NUM_CAUSES # need an additional "0" cause.
        causes = []
        for i in range(NUM_CAUSES): #3 is the number of causes
            new_x = math.cos(displacement * i) * self.rad
            new_y = math.sin(displacement * i) * self.rad
            causes.append(Node(new_x, new_y, "CAUSE", "Cause " + str(i+1), False))
            self.causes_rads.append(i * displacement)
        for i in range(NUM_CAUSES): #3 is the number of causes
            new_x = math.cos(displacement * i) * self.rad * 2
            new_y = math.sin(displacement * i) * self.rad * 2
            self.outer_points.append(Node(new_x, new_y, "CAUSE", "Cause " + str(i+1), False))

        causes.append(Node(0,0,"Cause", ".", False))
        return causes # no need to return the midpoints

    # This has now been completely refactored, so thats nice. Read the comments.
    def safe_normalize(self, values):
        total = sum(values)
        return [v / total for v in values] if total != 0 else values

    # take in our values, and our negatives, if we are using one negative or two negatives, and our starting position radians.
    def compute_flipped_coordinates(self, values, negatives, flip_type, causes_rads):
        index_of_interest = 0 # just so it has a starting point
        inner_magnitude = 0 # just as an initialization
        spin_components = [] # magnitudes of the other 2 vectors we will need

        if flip_type == 1: # one negativce, use the positive vectors for spin and negative for magnitude
            for idx in range(3): # hard coded for 3, could change
                if negatives[idx] == 1: # find the negative and track it
                    index_of_interest = idx
                    inner_magnitude = abs(values[idx])
                else: # append the fetcher to our list
                    spin_components.append(values[idx])
            spin_components = self.safe_normalize(spin_components) # normalize them so caring matters
            outer_magnitude = spin_components[0] - spin_components[1] # get it as a number between 0 and 1 for spin
            new_rads = (outer_magnitude * math.pi) / 6 # pi/3 for whole range -1 to 1, so pi/6 for indivudal components also pay attention to negative.
            base_rads = causes_rads[index_of_interest] - math.pi # subtract because we are coming from the wrong direction
            final_mag = 5 + 0.5 * inner_magnitude # how powered the vector is from the center

        else:  # flip_type == 2 # Much the same as the flip type of 1, just with some stuff reversed.
            for idx in range(3):
                if negatives[idx] == 0:
                    index_of_interest = idx
                    inner_magnitude = abs(values[idx])
                else:
                    spin_components.append(values[idx])
            spin_components = self.safe_normalize(spin_components)
            outer_magnitude = spin_components[0] - spin_components[1]
            new_rads = (outer_magnitude * math.pi) / 6
            base_rads = causes_rads[index_of_interest]
            final_mag = 10 - 0.5 * inner_magnitude # notice the minus 10 instead of the polus 10 here.



        if base_rads <= -math.pi  or base_rads >= 0: # we are in the top half of the circle, requires counter clockwise
            final_rads = base_rads - new_rads
        else: # we are in the bottom half of the circle, requires clockwise.
            final_rads = base_rads + new_rads # calcualte new poisition

        x = final_mag * math.cos(final_rads) # x and y components fo the new vector
        y = final_mag * math.sin(final_rads)
        return x, y # return the new vector as a tuple.

    # funciton to create the player nodes positions based on teh current optiosn matrix.
    def create_player_nodes(self):
        player_nodes = []
        for i in range(self.total_players): # iterate through all players
            current_x, current_y = 0, 0 # gotta start somewhere
            curr_values = self.current_options_matrix[i] # get our row bc thats all we care about
            curr_negatives = [1 if v < 0 else 0 for v in curr_values] # keeps track of how many negs and where they are
            num_negatives = sum(curr_negatives) # to prevent constant reaccessing
            all_negatives_flag = False # incase we need to up transparency

            if num_negatives == 0:#  normal case, no modificatinos
                norm_matrix = self.normalize_current_options_matrix()
                current_x, current_y = self.normal_coordinates_generation(i, norm_matrix)

            elif num_negatives == 3: # normal case flipped over origin; set flag as well.
                all_negatives_flag = True
                norm_matrix = self.normalize_current_options_matrix()
                current_x, current_y = self.normal_coordinates_generation(i, norm_matrix)
                current_x *= -1
                current_y *= -1

            elif num_negatives in (1, 2): # silly billy logic. we need to flip outside unit circle and go from there
                current_x, current_y = self.compute_flipped_coordinates(
                    curr_values, curr_negatives, num_negatives, self.causes_rads
                )

            player_nodes.append(Node(current_x, current_y, "PLAYER", f"Player {i + 1}", all_negatives_flag))

        self.player_nodes = player_nodes
        return player_nodes


    # generates sum(curr_negs == 0 or 3) to have that dot within the simplex. Does leave a deadzone.
    def normal_coordinates_generation(self, player_id, normalized_current_options_matrix):
        curr_x = 0
        curr_y = 0
        for cause_index in range(NUM_CAUSES):
            position_x, position_y = (self.causes[cause_index].get_x()), self.causes[cause_index].get_y()
            position_x = ((position_x * abs(normalized_current_options_matrix[player_id][cause_index])) / (2 * self.rad))
            position_y = ((position_y * abs(normalized_current_options_matrix[player_id][cause_index])) / (2 * self.rad))
            curr_x += position_x
            curr_y += position_y
        return curr_x, curr_y

    # code for getting rid of the deadspots that we currently have. Not entirely tested; likely to have bugs.
    # def unit_circle_coordinates_generation(self, player_id, normalized_current_options_matrix):
    #     curr_x = 0
    #     curr_y = 0
    #
    #     for cause_index in range(NUM_CAUSES):
    #         weight = normalized_current_options_matrix[player_id][cause_index]
    #         base_x, base_y = self.causes[cause_index].get_x(), self.causes[cause_index].get_y()
    #
    #         # Normalize the cause vector
    #         length = math.sqrt(base_x ** 2 + base_y ** 2)
    #         if length == 0:
    #             continue  # Avoid division by zero
    #
    #         # Use the magnitude of the weight directly to scale outward
    #         norm_x = base_x / length
    #         norm_y = base_y / length
    #
    #         curr_x += norm_x * weight * self.rad
    #         curr_y += norm_y * weight * self.rad
    #
    #         magnitude = math.sqrt(curr_x ** 2 + curr_y ** 2)
    #         if magnitude > 10:
    #             curr_x = (curr_x / magnitude) * 5
    #             curr_y = (curr_y / magnitude) * 5
    #
    #     return curr_x, curr_y


    def normal_vector_generation(self, player_id, normalized_current_options_matrix, cause_index):
        curr_x = 0
        curr_y = 0
        position_x, position_y = (self.causes[cause_index].get_x()), self.causes[cause_index].get_y()
        position_x = ((position_x * (normalized_current_options_matrix[player_id][cause_index])) / (2 * self.rad))
        position_y = ((position_y * (normalized_current_options_matrix[player_id][cause_index])) / (2 * self.rad))
        curr_x += position_x
        curr_y += position_y
        return (curr_x, curr_y)

    def normalize_current_options_matrix(self):
        current_options_matrix = self.current_options_matrix
        new_options_matrix = []
        new_row = []
        for row in current_options_matrix:
            current_sum = 0
            for val in row:
                current_sum += abs(val)
            if current_sum != 0:
                new_row = [(val / current_sum) * 10 for val in row]
                new_options_matrix.append(new_row)
            else:
                new_options_matrix.append(row) # all zeros, just chill
        return new_options_matrix


    def create_choice_matrix(self, current_options_matrix):
        current_options_matrix = [[0] + row for row in current_options_matrix] # append a 0 to it
        choice_list = [0] * len(current_options_matrix[0])
        for i, row in enumerate(current_options_matrix):
            min_val = min(row) # lets avoid clamping for now IG.
            adjusted_row = [x - min_val for x in row]
            total = sum(adjusted_row)
            if total == 0:
                normalized_row = [0 for _ in adjusted_row]
            else:
                normalized_row = [x / total for x in adjusted_row]
            choice_list = [choice_list[i] + normalized_row[i] for i in range(len(choice_list))]
        total = sum(choice_list)
        choice_list = [val / total for val in choice_list]
        return choice_list

    def get_winning_probabilities(self):
        return self.winning_probability


