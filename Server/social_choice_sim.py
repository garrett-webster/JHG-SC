import copy
import math
import random
from collections import Counter
from pathlib import Path

import numpy as np


from Server.options_creation import generate_two_plus_one_groups_options_best_of_three, generate_two_plus_one_groups
from Server.SC_Bots.Greedy import GreedyBot
from Server.SC_Bots.betterGreedy import betterGreedy
from Server.SC_Bots.SocialWelfare import SocialWelfareBot
from Server.SC_Bots.Random import RandomBot
from Server.SC_Bots.limitedAwareGreedy import limitedAwarenessGreedy
from Server.Node import Node
from Server.SC_Bots.secondChoiceGreedy import secondChoiceGreedy
from Server.SC_Bots.somewhatMoreAwareGreedy import somewhatMoreAwarenessGreedy

NUM_CAUSES = 3


class Social_Choice_Sim:
    def __init__(self, total_players, num_causes, num_humans, cycle=0, round=0, chromosomes="", scenario="", group=""):
        # just a bunch of base setters.
        self.total_players = total_players
        self.num_humans = num_humans
        self.num_bots = total_players - num_humans
        self.num_causes = num_causes
        self.cycle = cycle # set these for graphing and logging purposes, we usually set these round by round and cycle by cycle for logging purposes.
        self.round = round
        self.rad = 5  # used for graphing the dots on the board.


        self.players = self.create_players() # ??? This might be used for multiplayer functionality.
        self.causes = self.create_cause_nodes() # graphing stuff.
        self.player_nodes = [] # also graphing stuff.

        self.chromosome_string = "" # holds the file name of the chromosome baering file.
        self.chromosomes = self.set_chromosomes(chromosomes) # self.chromosomes contains the full list of all chromosomes.

        # sets the scenario
        self.scenario_string = Path(scenario).name

        # create the bots, first getting number and type from scenario and then setting the chromosomes from the chromsomes.
        self.bot_type = self.set_bot_list(scenario)
        self.bots = self.create_bots()
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




    def create_results(self):
        self.results = {}
        for i in range(self.total_players):  # total_players
            self.results[i] = []  # just throw in all the utilites
        return self.results


    def set_chromosome(self, chromosomes):
        self.chromosome_string = Path(chromosomes).name
        return self.chromosome_string


    def create_total_types(self):
        self.total_types = self.bot_type
        if self.total_players != self.num_humans or self.total_players != self.num_bots: # if there is a mistmatch
            for player in range(self.total_players - self.num_bots):
                self.total_types.insert(0, -1)
        return self.total_types


    def set_group(self, group_option):
        if group_option == "":
            self.group = -1
            self.sc_groups = -1
        else:
            self.group = group_option
            self.sc_groups = generate_two_plus_one_groups(self.total_players, group_option)



    def create_bots(self):
        bots_array = []

        if len(self.bot_type) != self.num_bots:
            print("THERE HAS BEEN AN ERROR!! WAAAH")
            return # early return, blow everything up.
        else:
            for i, bot_type in enumerate(self.bot_type):
                bots_array.append(self.match_bot_type(bot_type, i))

        return bots_array

    def match_bot_type(self, bot_type, i):
        new_bot = None
        bot_type = int(bot_type)
        if bot_type == 0:
            new_bot = (RandomBot(i))
        if bot_type == 1:
            new_bot = (SocialWelfareBot(i))
        if bot_type == 2:
            new_bot = (GreedyBot(i))
        if bot_type == 3:
            new_bot = (betterGreedy(i))
        if bot_type == 4:
            new_bot = (limitedAwarenessGreedy(i))
        if bot_type == 5:
            new_bot = (secondChoiceGreedy(i))
        if bot_type == 6:
            new_bot = (somewhatMoreAwarenessGreedy(i))


        return new_bot # the matched bot that we were looking for.

    def create_players(self):
        players = {}
        for i in range(self.total_players):
            players[str(i)] = 0
        return players


    def set_bot_chromosomes(self, chromosomes):
        if len(chromosomes) != len(self.bot_type):
            print("WRONG WRONG WRONG")
        else:
            for i in range(len(self.bots)):
                self.bots[i].set_chromosome(chromosomes[i])


    def apply_vote(self, winning_vote):
        for i in range(self.total_players):
            self.players[str(i)] += self.current_options_matrix[i][int(winning_vote)]


    def create_options_matrix(self):
        if self.sc_groups != -1:
            self.current_options_matrix = generate_two_plus_one_groups_options_best_of_three(self.sc_groups)
        else: # so we have to generate noise to try and "mimic" the other stuff.
            self.current_options_matrix = [[random.randint(-8, 8) for _ in range(self.num_causes)] for _ in range(self.total_players)]
            noise_matrix = [[random.choice([-2, 2]) for _ in range(self.num_causes)] for _ in range(self.total_players)]
            self.current_options_matrix = [
                [original + noise for original, noise in zip(row, noise_row)]
                for row, noise_row in zip(self.current_options_matrix, noise_matrix)
            ]
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


    def get_votes(self, previous_votes=None, round=0, cycle=0): # generic get votes for all bot types. Not optimized for a single chromosome
        self.round = round
        self.cycle = cycle

        bot_votes = {}

        final_votes = None
        for i, bot in enumerate(self.bots):
                final_votes = bot.get_vote(self.current_options_matrix, previous_votes)
                bot_votes[i] = final_votes

        self.final_votes = bot_votes

        return bot_votes


    def return_win(self, all_votes):
        self.current_results = []
        total_votes = all_votes
        #self.final_votes = all_votes
        winning_vote_count = Counter(total_votes.values()).most_common(1)[0][1]
        winning_vote = Counter(total_votes.values()).most_common(1)[0][0]
        if not (winning_vote_count > len(total_votes) // 2):
            winning_vote = -1

        if winning_vote != -1: # if its -1, then nothing happend. NOT the last entry in the fetcher. that was a big bug that flew under the radar.
            for i in range(len(total_votes)):
                self.current_results.append(self.current_options_matrix[i][winning_vote])
            self.add_coop_score()
        else:
            for i in range(len(total_votes)):
                self.current_results.append(0)

        return winning_vote, self.current_results

    def save_results(self):
        for player in range(len(self.current_results)):
            self.results[player].append(self.current_results[player])



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
        if sc_groups != None:
            self.sc_groups = sc_groups
        self.current_options_matrix = self.create_options_matrix()
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

        current_cooperation_score = copy.copy(self.cooperation_score)
        winning_vote, _ = self.return_win(self.final_votes)
        self.set_coop_score(current_cooperation_score)  # reset it bc the above does silly things.

        group = self.get_group()

        return current_node_json, self.final_votes, winning_vote, self.current_options_matrix, self.total_types, self.scenario_string, group, self.round, self.cycle, self.chromosome_string

    def get_results(self):
        cooperation_score = self.cooperation_score / self.num_rounds  # as a percent, how often we cooperated. (had a non negative cause pass)
        return self.results, cooperation_score, self.total_types, self.num_rounds, self.scenario_string, self.group, self.chromosome_string

    def get_everything_for_logger(self):
        self.create_player_nodes()
        current_nodes = self.compile_nodes()
        current_node_json = []
        for node in current_nodes:
            current_node_json.append(node.to_json())

        current_cooperation_score = copy.copy(self.cooperation_score)
        winning_vote, _ = self.return_win(self.final_votes)
        self.set_coop_score(current_cooperation_score)  # reset it bc the above does silly things.
        cooperation_score = self.cooperation_score / self.num_rounds  # as a percent, how often we cooperated. (had a non negative cause pass)


        return current_node_json, self.final_votes, winning_vote, self.current_options_matrix, self.results, cooperation_score, self.total_types, self.num_rounds, self.scenario_string, self.group, self.cycle, self.round

    def create_bot_list_as_string(self, bots_list):
        bots_as_string = []
        for bot in bots_list:
            bots_as_string.append(str(bot.get_number_type()))
        return bots_as_string


    ###--- NODE CREATION FOR FRONT END. NOT USEFUL FOR GENETIC STUFF. ---###


    def create_cause_nodes(self):
        displacement = (2 * math.pi) / NUM_CAUSES # need an additional "0" cause.
        causes = []
        for i in range(NUM_CAUSES): #3 is the number of causes
            new_x = math.cos(displacement * i) * self.rad
            new_y = math.sin(displacement * i) * self.rad
            causes.append(Node(new_x, new_y, "CAUSE", "Cause " + str(i+1)))
        return causes


    def create_player_nodes(self):
        normalized_current_options_matrix = self.current_options_matrix

        player_nodes = []
        for i in range(self.total_players): # i is the player index
            if i == 1:
                pass
            player_index = i
            current_x = 0 # https://www.youtube.com/watch?v=r7l0Rq9E8MY
            current_y = 0
            curr_negatives = []
            for cause_index in range(NUM_CAUSES):  # completely populate this fetcher first.
                # keep track of negatives
                if (self.current_options_matrix[i][cause_index]) < 0:
                    curr_negatives.append(1)
                else:
                    curr_negatives.append(0)

            for cause_index in range(NUM_CAUSES):
                # create the new positions (onyl use teh abs so the flips scale correctly.
                position_x, position_y = (self.causes[cause_index].get_x()), self.causes[
                    cause_index].get_y()  # get the strength based on where they are
                position_x = ((position_x * abs(normalized_current_options_matrix[i][cause_index])) / (
                            2 * self.rad))  # normalize it to the circle
                position_y = ((position_y * abs(normalized_current_options_matrix[i][cause_index])) / (
                            2 * self.rad))  # normalize it to the circle

                current_x += position_x
                current_y += position_y

            # so this should sum everything up.
            # lets make a novel edge case and test it from there.

            if sum(curr_negatives) == 0: # if there are no negatives.
                pass # do nothing, we are in the right spot.

            if sum(curr_negatives) == 1: # flip over unaffected line
                dots_of_interest = []
                for i, value in enumerate(curr_negatives):
                    if value == 0:
                        dots_of_interest.append(i) # need the index, might have to do a range thing.
                point_1_x, point_1_y = round(self.causes[dots_of_interest[0]].get_x(), 2), round(self.causes[dots_of_interest[0]].get_y(), 2)
                point_2_x, point_2_y = round(self.causes[dots_of_interest[1]].get_x(), 2), round(self.causes[dots_of_interest[1]].get_y(), 2)
                current_x, current_y = self.flip_point_over_line(current_x, current_y, point_1_x, point_1_y, point_2_x, point_2_y)

            if sum(curr_negatives) == 2: # flip over unaffectd point
                pass
                dot_of_interest = [i for i, value in enumerate(curr_negatives) if value == 0][0]

                point_x, point_y = self.causes[dot_of_interest].get_x(), self.causes[dot_of_interest].get_y()
                current_x, current_y = self.flip_point(current_x, current_y, point_x, point_y)

            if sum(curr_negatives) == 3: # flip over origin.
                current_x, current_y = self.flip_point(current_x, current_y, 0, 0) # we just flip over teh origin.

            player_nodes.append(Node(current_x, current_y, "PLAYER", "Player " + str(player_index+1)))
        return player_nodes


    def slope(self, x1, y1, x2, y2):
        if x2 - x1 == 0:
            return float('inf')
        return (y2 - y1) / (x2 - x1)


    def perpendicular_slope(self, m):
        if m == 0:
            return float('inf')
        if m == float('inf'):
            return 0.0
        else:
            return -1 / m


    # point 1 is the point we want to flip, point 2 is the point we are flipping over
    def flip_point(self, point_1_x, point_1_y, point_2_x, point_2_y):
        reflected_x = 2 * point_2_x - point_1_x
        reflected_y = 2 * point_2_y - point_1_y
        return reflected_x, reflected_y


    def flip_point_over_line(self, point_x, point_y, line_point1_x, line_point1_y, line_point2_x, line_point2_y):
        m = self.slope(line_point1_x, line_point1_y, line_point2_x, line_point2_y)
        m_perp = self.perpendicular_slope(m)

        if m == float('inf'):
            x_intersect = line_point1_x
            y_intersect = point_y
        elif m == (0):
            x_intersect = point_x
            y_intersect = line_point1_y
        else:
            x_intersect = (m * line_point1_x - m_perp * point_x - line_point1_y + point_y) / (m - m_perp)
            y_intersect = m * (x_intersect - line_point1_x) + line_point1_y

        x_reflected = 2 * x_intersect - point_x
        y_reflected = 2 * y_intersect - point_y

        return x_reflected, y_reflected


