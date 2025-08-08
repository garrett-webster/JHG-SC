import copy
import math
import random
from collections import Counter
from pathlib import Path
import numpy as np

from Server.Engine.completeBots.geneagent3 import GeneAgent3
from Server.Engine.completeBots.humanagent import HumanAgent
from Server.Node import Node
from Server.SC_Bots.legacyBots.humanAttempt2 import humanAttempt2
from Server.OptionGenerators.options_creation import generate_two_plus_one_groups
from Server.SC_Bots.Greedy import GreedyBot
from Server.SC_Bots.SocialWelfare import SocialWelfareBot
from Server.SC_Bots.Random import RandomBot
from Server.SC_Bots.legacyBots.somewhatMoreAwareGreedy import somewhatMoreAwarenessGreedy
from Server.SC_Bots.optimalHuman import optimalHuman
from Server.SC_Bots.legacyBots.reorganizedHuman import reorganizedHuman
from Server.SC_Bots.possibleCheetahBot import cheetahBot
from Server.allocation_bots.socialWelfare import SocialWelfare
from Server.allocation_bots.random import Random

NUM_CAUSES = 3 # if its ever not this a LOT of math breaks, so just leave it be.

class Social_Choice_Sim:
    def __init__(self, total_players, num_causes, num_humans, options_generator, cycle=0, round=0, chromosomes="",
                 scenario="", group="", total_order=None, allocation_scenario="", utility_per_player=3):
        self.options_generator = options_generator
        if total_order == None:  # generating it non server side
            self.total_order = self.create_total_order(total_players, num_humans)
        else:  # if created with server, spoon feed it.
            self.total_order = total_order
        # just a bunch of base setters.
        self.utility_per_player = utility_per_player
        self.bot_index_dict = {}
        self.total_players = total_players
        self.num_humans = num_humans
        self.num_bots = total_players - num_humans
        self.num_causes = num_causes
        self.cycle = cycle  # set these for graphing and logging purposes, we usually set these round by round and cycle by cycle for logging purposes.
        self.round = round
        self.rad = 5  # used for graphing the dots on the board.

        self.players = self.create_players()  # ??? This might be used for multiplayer functionality.
        self.outer_points = []
        self.causes_rads = []
        self.causes = self.create_cause_nodes()  # graphing stuff.

        self.player_nodes = []  # also graphing stuff.
        self.bot_type = self.set_bot_list(scenario)

        self.chromosome_string = ""  # holds the file name of the chromosome baering file.
        self.chromosomes = self.set_chromosomes(
            chromosomes)  # self.chromosomes contains the full list of all chromosomes.

        # sets the scenario
        self.scenario_string = Path(scenario).name

        # create the bots, first getting number and type from scenario and then setting the chromosomes from the chromsomes.
        self.bot_type = self.set_bot_list(scenario)
        self.allocation_bot_type = self.set_bot_list(allocation_scenario)
        #self.bots = self.create_bots(self.total_order)  # make sure to pull this from the right spot.
        self.bots = self.use_gene_bots() # the hope is that I just use all of em and call it a day.
        #self.allocation_bots = self.create_allocation_bots(self.total_order) # old code, want to try something new
        self.allocation_bots = self.bots # use the same bot for both.
        self.bot_list_as_string = self.create_bot_list_as_string(self.bots)
        # self.allocation_bot_list_as_string = self.create_bot_list_as_string(self.allocation_bots)
        ## turn this one back one when you are not using the Gene3 agent bots, as those are initalized with chromosomes.
        # self.set_bot_chromosomes(self.chromosomes)  # no chromosomes for allocaiton bots.
        self.total_types = self.create_total_types()

        # group stuff - all used under set group, and then there are defualts just in case.
        self.group = -1  # doesn't exist, let me know it hasn't been set.
        self.sc_groups = -1  # no group exists, can ignore.
        self.group_option = group

        # the bread and butter of the sim. set under start round.
        self.current_options_matrix = {}

        # holds all the results from all the games we have played with this current sim
        self.results = {}  # holds all of our results from long term simulations before graphing.
        self.results_sums = [10] * total_players  # holds the SUM of all player results, so we can easily access and return them as necessary.
        self.cooperation_score = 0
        self.num_rounds = -1  # used in various spots for graphing and whatnot. not terribly important.
        self.current_results = []  # holds the results from the last "return win" call, which we can access later.
        self.results = self.create_results()  # dict key: player id, attribute: list of all utility changes per round.
          # holds EVERYONE. now we gotta do a significant amount of refactoring.
        self.choice_matrix = [0] * (self.num_causes + 1)
        self.last_option = 0
        # self.all_numbers_matrix = [0] * 21
        self.all_votes = {}

        self.winning_probability = []

        self.alpha = 0.2  # whatever we are hard coding this fetcher. I'll work with it more later.
        # this is a 3 dimensional list of lists. we have a list for every round, and within that we have a list of lists that represents a 2d vector.
        # not sure if this will help. lets find out.
        self.I = {0: [[0 for _ in range(total_players)] for _ in
                      range(total_players)]}  # square matrix of 0's for all player relations
        # this needs to be a square matrix for reasons. thats cool I guess.
        # self.v = [[0 for _ in range(total_players)] for _ in range(total_players)]  # represents the change in utility at that round.
        self.peeps = None  # just so we have it around
        self.new_v = None
        self.extra_data = {
            i: {
                j: None for j in range(len(total_order))
            } for i in range(len(total_order))
        }
        self.most_recent_influence = None # keep this fetcher around somewhere.

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
            self.results[i] = [10]  # just throw in all the utilites
        return self.results

    def set_chromosome(self, chromosomes):
        self.chromosome_string = Path(chromosomes).name
        return self.chromosome_string

    # here is the offender. this is the thing we have to rework.
    def create_total_types(self):
        if self.total_order is None:
            return self.bot_type # assume only bots if no total order. never used.
        self.total_types = [self.bot_type[0] for _ in range(self.num_bots)]
        if len(self.total_types) != len(self.total_order): # the only way this happens is becuase we are missing human players
            for i, player in enumerate(self.total_order):
                if player[0] == "P":
                    self.total_types.insert(i, -1)
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
        self.bot_index_dict = {}
        if total_order is not None:
            for index, object in enumerate(total_order):
                if object.startswith("B"):
                    bot_indexes.append(index)
                    # make sure this is doing whta you think its doing.
                    self.bot_index_dict[object] = index

        if len(self.bot_type) != self.num_bots:
            # lets fix this logic right here and now.
            self.bot_type = [self.bot_type[0]] * self.num_bots

        for i, bot_type in enumerate(self.bot_type):
            current_index = bot_indexes.pop(0)
            # print("this the bot index that we are adding ", current_index)
            bots_array.append(self.match_bot_type(bot_type, current_index))

        return bots_array

    def create_allocation_bots(self, total_order):
        bots_array = []
        bot_indexes = []
        self.allocation_bots_index = {}
        if total_order is not None:
            for index, object in enumerate(total_order):
                if object.startswith("B"):
                    bot_indexes.append(index)
                    # make sure this is doing whta you think its doing.
                    self.allocation_bots_index[object] = index

        if len(self.allocation_bot_type) != self.num_bots:
            # lets fix this logic right here and now.
            self.allocation_bot_type = [self.allocation_bot_type[0]] * self.num_bots

        for i, bot_type in enumerate(self.allocation_bot_type):
            current_index = bot_indexes.pop(0)
            # print("this the bot index that we are adding ", current_index)
            bots_array.append(self.match_allocation_bot_type(bot_type, current_index))

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

        return new_bot  # the matched bot that we were looking for.

    def match_allocation_bot_type(self, bot_type, index):
        new_bot = None
        bot_type = int(bot_type)
        if bot_type == 0:
            new_bot = (Random(index, self.utility_per_player))
        if bot_type == 1:
            new_bot = (SocialWelfare(index, self.utility_per_player))

        return new_bot  # the matched bot that we were looking for.

    # ovverides the other bots to make sure that I can use the same bot for both - important for the genetic algorithm.
    def bot_ovveride(self, bots):
        self.bots = bots
        self.allocation_bots = bots
        self.total_types = self.create_total_types() # make this cause we need it now


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
        self.current_options_matrix = self.options_generator.generateOptions()
        return self.current_options_matrix  # because why not

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
        #print("this is the current coop score ", self.cooperation_score, " and here is the current round ", self.num_rounds)

    def set_coop_score(self, coop_score):
        self.cooperation_score = coop_score

    def get_group(self):
        return self.group

    def get_votes(self, previous_votes=None, round=0, cycle=0,
                  max_cycle=3, influence=None):  # generic get votes for all bot types. Not optimized for a single chromosome
        # print("this is the round we are dealing with ", round, " and this is the self.I we are dealing with ", self.I)
        if influence == None: influence = self.I[round]
        self.round = round
        self.cycle = cycle
        all_votes = {}
        bot_indexes = []
        # print("here is the len of total types (Expect 8, not 9) ", len(self.total_types))
        for i, thing in enumerate(self.total_types):
            all_votes[i] = -1  # just assume they are all abstaining
            if thing != -1:
                bot_indexes.append(i)

        bot_votes = {}
        final_votes = None
        extra_data = {""}
        # print("here is the len of self.bots (should be 8, not 9 )", len(self.bots))
        for i, bot in enumerate(self.bots):
            # print("this is the bot id ", bot.self_id, " an dthis is the i index ", i)
            # print("this is the cycle we are working with ", cycle, " and the round ", round)
            if isinstance(bot, GeneAgent3):
                if cycle == 0:
                    votes_put_in = None
                else:
                    votes_put_in = previous_votes[cycle-1]
                # ok what the FETCH should received be. I think just its list in V is probably the way to go.
                recieved = self.reconcile_received(i, votes_put_in) # gotta figure out if we HAVE recieved anything yet. could use a round=0check.
                final_votes = bot.get_vote(i, round, recieved, self.results_sums, np.array(influence), extra_data, self.current_options_matrix)
            elif isinstance(bot, HumanAgent):
                continue # he doesn't get to vote :(
            else:
                final_votes = bot.get_vote(self.current_options_matrix, previous_votes, cycle, max_cycle)
            all_votes[bot_indexes.pop(0)] = final_votes

        self.most_recent_influence = influence
        self.final_votes = all_votes

        return all_votes

    def reconcile_received(self, agent, previous_votes):
        # if the game is just starting or the first round, we will have no room with which to think, thus 0's.
        solid_received = self.new_v[agent] if self.new_v is not None else [0 for _ in range(self.total_players)]  # this SHOULD? work better.
        # only problem - this completely fails to take into account previous cycles, which is odd. might need to save a new v per cycle and average it as we go.
        new_received = self.calculate_v_given_options_and_votes(self.current_options_matrix, previous_votes)[agent]
        # print("Here is the solid received ", solid_received, " and here is the new_received ", new_received)
        new_v = []
        for i in range(len(new_received)):
            new_v.append((solid_received[i] + new_received[i]) / 2) # make this part of the agent chromosome at some point, for right now its just there.
        # print("this is the new v ", new_v)
        return new_v

    # this exists of necessity of needing to add player votes to this fetcher. Bot votes only are easy, but we need player votes as well.
    def record_votes(self, current_votes, cycle_number):
        self.all_votes[cycle_number] = current_votes

    # tallies if there is a winning vote and does a bunch of stuff with it for tracking purposes.
    def return_win(self, all_votes):
        self.current_results = []
        total_votes = all_votes
        # self.final_votes = all_votes
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

        if winning_vote != -1:  # if its -1, then nothing happend. NOT the last entry in the fetcher. that was a big bug that flew under the radar.
            for i in range(len(total_votes)):
                self.current_results.append(self.current_options_matrix[i][winning_vote])
            self.add_coop_score()
        else:
            for i in range(len(total_votes)):
                self.current_results.append(0)

        choice_list = self.create_choice_matrix(self.current_options_matrix)
        self.winning_probability.append(choice_list[winning_vote + 1])

        # creates the new utilty effort matrix based on the actual votes. Doesn't matter what actually won, just what you voted for in the end.
        # this fetcher right here contains using the actual player votes to decide the new v. the below version is going to use the winning vote.
        new_v = []
        current_options_matrix_columns = list(zip(*self.current_options_matrix))  # get the columns.
        for plyr_idx in range(self.total_players):
            if all_votes[plyr_idx] == -1:
                new_v.append([0 for _ in range(
                    self.total_players)])  # if abstain, 0's across the board. probably. I might rework this later.
            else:
                new_v.append(
                    current_options_matrix_columns[all_votes[plyr_idx]])  # add the column of what they did to the new v.

        self.new_v = new_v
        self.calculate_influence_matrix(new_v, self.round)
        return winning_vote, self.current_results

    # version uses the wining vote rather than the attempted vote. swapping them out to see if it makes a difference.
    # worried this version de-teeths them in a way that flattens their possible animosity
    # new_v = []
    # current_options_matrix_columns = list(zip(*self.current_options_matrix))  # get the columns.
    # for plyr_idx in range(self.total_players):
    #     if winning_vote == -1:
    #         new_v.append([0 for _ in range(
    #             self.total_players)])  # if abstain, 0's across the board. probably. I might rework this later.
    #     else:
    #         new_v.append(current_options_matrix_columns[winning_vote])  # add the column of what they did to the new v.
    #
    # self.new_v = new_v
    # self.calculate_influence_matrix(new_v, self.round)
    # return winning_vote, self.current_results

    def calculate_v_given_options_and_votes(self, current_options_matrix, previous_votes):
        if not previous_votes: # nothing to go off of, early return.
            return [[0 for _ in range(self.total_players)] for _ in range(self.total_players)]

        new_v = []
        current_options_matrix_columns = list(zip(*current_options_matrix))  # get the columns.
        # print("these are the previous votes we are dealing with ", previous_votes)
        for plyr_idx in range(self.total_players):
            if previous_votes[plyr_idx] == -1:
                new_v.append([0 for _ in range(
                    self.total_players)])  # if abstain, 0's across the board. probably. I might rework this later.
            else:
                new_v.append(current_options_matrix_columns[
                                 previous_votes[plyr_idx]])  # add the column of what they did to the new v.
        return new_v

    # this one has one goal. is there a winning vote.
    def return_win_without_silly(self, all_votes):
        self.current_results = []
        total_votes = all_votes
        winning_vote_count = Counter(total_votes.values()).most_common(1)[0][1]
        winning_vote = Counter(total_votes.values()).most_common(1)[0][0]

        if not (winning_vote_count > len(total_votes) // 2):
            winning_vote = -1

        if winning_vote != -1:  # if its -1, then nothing happend. NOT the last entry in the fetcher. that was a big bug that flew under the radar.
            for i in range(len(total_votes)):
                self.current_results.append(self.current_options_matrix[i][winning_vote])
        else:
            for i in range(len(total_votes)):
                self.current_results.append(0)

        return winning_vote, self.current_results  # literally just returns who won. thats it.

    def calculate_influence_matrix(self, new_v, curr_round):
        new_index = len(self.I)  # lets see if this works any better.
        self.I[new_index] = [[0 for _ in range(self.total_players)] for _ in
                             range(self.total_players)]  # initalize it w/ something.
        for i in range(self.total_players):
            for j in range(self.total_players):
                self.I[new_index][i][j] = self.alpha * new_v[i][j] + (1 - self.alpha) * self.I[new_index - 1][i][j]
        return self.I[new_index]  # swap it from rounds based to an index based approach.

    def get_influence_matrix(self):
        last_key = next(reversed(self.I.keys()))
        return self.I[last_key]  # because fetch it, we never need the entire thing.

    def set_choice_matrix(self, new_choice_matrix):
        self.choice_matrix = new_choice_matrix

    def get_last_option(self):
        return self.last_option

    def save_results(self):
        for player in range(len(self.current_results)):
            self.results_sums[player] += self.current_results[player]  # should keep a running total.
            self.results[player].append(self.current_results[player])


    def get_results_per_round(self):
        sums_per_round = [[0 for _ in range(self.num_rounds)] for _ in range(self.total_players)]
        for bot in self.results:
            sums_per_round[bot] = []
            current_sum = 0
            for i, new_sum in enumerate(self.results[bot]):
                current_sum += new_sum
                sums_per_round[bot].append(current_sum)

        return sums_per_round

    def get_average_utility_per_round(self):
        average_utility_per_round = []
        sums_per_round = self.get_results_per_round()
        inverted_sums_per_round = list(zip(*sums_per_round))
        for i, player in enumerate(inverted_sums_per_round):
            average_utility_per_round.append(sum(player) / len(player))

        return average_utility_per_round




    def get_new_utilities(self):
        return self.results

    # SUM: sets up the bot list with a current file. Will override any potential single types as those seem to be more important. will likely be refactored.
    def set_bot_list(self, current_file):
        if current_file != "":
            with open(current_file, "r") as file:
                for line in file:
                    if line.startswith("#"):
                        continue  # skip the comment lines
                    bot_types = [int(x) for x in line.strip().split(",")]
                    break  # stop when teh numbers are over.

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
    def start_round(self, options_and_peeps=None):
        if options_and_peeps is not None:
            self.current_options_matrix = options_and_peeps[0]
            self.peeps = options_and_peeps[1]
        else:
            self.current_options_matrix = self.create_options_matrix()  # cause we have to create groups.

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

    # takes a bunch of data and turns it into a josn that we can use
    def record_individual_round(self):
        (all_nodes, all_votes, winning_vote_list, current_options_matrix, types_list, scenario, group, curr_round, cycle,
         chromosome, influence_matrix, results_sums, results, peeps) = self.prepare_graph()
        total_data = {
            "types_list": types_list,
            "all_nodes": all_nodes,
            "all_votes": copy.deepcopy(all_votes),
            "winning_vote": winning_vote_list,
            "current_options_matrix": current_options_matrix,
            "scenario": scenario,
            "group": group,
            "curr_round": curr_round,
            "cycle": cycle,
            "chromosome": chromosome,
            "influence_matrix": influence_matrix,
            "results_sums": copy.copy(results_sums),
            "results": results,
            "peeps": peeps
        }
        return total_data # WHEE

    def prepare_graph(self):
        self.create_player_nodes()
        current_nodes = self.compile_nodes()
        current_node_json = []
        for node in current_nodes:
            current_node_json.append(node.to_json())

        winning_vote_list = {}  # key is the cycle, and the attribute is the winning vote of that cycle.
        for cycle in self.all_votes:
            winning_vote_list[cycle], _ = self.return_win_without_silly(self.all_votes[cycle])

        group = self.get_group()
        # so now what we do instead is that we take in a winning vote list cycle by cycle and spit it out as necessary.
        # --- supplemental information required for allocations and more advanced graph --- #

        total_data = {
            "all_nodes": list(current_node_json),
            "all_votes": self.all_votes,
            "winning_vote_list": winning_vote_list,
            "current_options_matrix": self.current_options_matrix,
            "types_list": self.total_types,
            "scenario_string": self.scenario_string,
            "group": group,
            "curr_round": self.round,
            "cycle": self.cycle,
            "chromosome string": self.chromosome_string,
            "influence_matrix": self.get_influence_matrix(),
            "results_sums": self.results_sums,
            "results": self.results,
            "peeps": self.peeps,
        }

        #return current_node_json, self.all_votes, winning_vote_list, self.current_options_matrix, self.total_types, self.scenario_string, group, self.round, self.cycle, self.chromosome_string, self.get_influence_matrix(), self.results_sums, self.results, self.peeps
        return total_data



    def get_results(self):
        # print("Aight were is the zero, its gotta be under num_rounds right?") literally zero clue whawt this print statement was supposed to be for.
        cooperation_score = self.cooperation_score / (self.num_rounds+1) if self.num_rounds > 0 else 0  # how often a cause passed (bc rounds start form 0 we have to add one)
        return self.results, cooperation_score, self.total_types, self.num_rounds, self.scenario_string, self.group, self.chromosome_string, self.results_sums, self.most_recent_influence

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

    def use_gene_bots(self):
        num_agents = self.total_players
        popSize = 60
        player_idxs = list(np.arange(0, num_agents))
        theFolder = "Server/Engine"
        theGen = 199
        num_gene_copies = 3
        thePopulation = []
        fnombre = r"C:\Users\Sean\Documents\GitHub\OtherGarrettStuff\JHG-SC\offlineSimStuff\geneticStuff\SCResults\theGenerations\gen_1.csv"
        fp = open(fnombre, "r")

        for i in range(0, popSize):
            line = fp.readline()
            words = line.split(",")

            thePopulation.append(GeneAgent3(words[0], num_gene_copies, self.utility_per_player))
            thePopulation[i].count = float(words[1])
            thePopulation[i].relativeFitness = float(words[2])

        plyrs = []
        for i in range(0, len(player_idxs)):
            plyrs.append(thePopulation[player_idxs[i]])
        players = np.array(plyrs)
        agents = list(players)
        initial_pops = [10 for _ in range(num_agents)]
        poverty_line = 0
        forcedRandom = False

        players = [
            *agents
        ]

        alpha_min, alpha_max = 0.20, 0.20
        beta_min, beta_max = 0.5, 1.0
        keep_min, keep_max = 0.95, 0.95
        give_min, give_max = 1.30, 1.30
        steal_min, steal_max = 1.6, 1.60

        num_players = len(players)

        game_params = {
            "num_players": num_players,
            "alpha": alpha_min,  # np.random.uniform(alpha_min, alpha_max),
            "beta": beta_min,  # np.random.uniform(beta_min, beta_max),
            "keep": keep_min,  # np.random.uniform(keep_min, keep_max),
            "give": give_min,  # np.random.uniform(give_min, give_max),
            "steal": steal_min,  # np.random.uniform(steal_min, steal_max),
            "poverty_line": poverty_line,
            "base_popularity": np.array(initial_pops)
        }

        for a in agents:  # sets the game params for all users.
            a.setGameParams(game_params, forcedRandom)

        return players # this SHOUDL do the trick.

    ########################################################################
    ###--- NODE CREATION FOR FRONT END. NOT USEFUL FOR GENETIC STUFF. ---###
    ########################################################################

    def create_cause_nodes(self):
        displacement = (2 * math.pi) / NUM_CAUSES  # need an additional "0" cause.
        causes = []
        for i in range(NUM_CAUSES):  # 3 is the number of causes
            new_x = math.cos(displacement * i) * self.rad
            new_y = math.sin(displacement * i) * self.rad
            causes.append(Node(new_x, new_y, "CAUSE", "Cause " + str(i + 1), False))
            self.causes_rads.append(i * displacement)

        causes.append(Node(0, 0, "Cause", ".", False))
        return causes  # no need to return the midpoints

    # This has now been completely refactored, so thats nice. Read the comments.
    def safe_normalize(self, values):
        total = sum(values)
        return [v / total for v in values] if total != 0 else values

    # take in our values, and our negatives, if we are using one negative or two negatives, and our starting position radians.
    def compute_flipped_coordinates(self, values, negatives, flip_type, causes_rads):
        index_of_interest = 0  # just so it has a starting point
        inner_magnitude = 0  # just as an initialization
        spin_components = []  # magnitudes of the other 2 vectors we will need

        if flip_type == 1:  # one negativce, use the positive vectors for spin and negative for magnitude
            for idx in range(3):  # hard coded for 3, could change
                if negatives[idx] == 1:  # find the negative and track it
                    index_of_interest = idx
                    inner_magnitude = abs(values[idx])
                else:  # append the fetcher to our list
                    spin_components.append(values[idx])
            spin_components = self.safe_normalize(spin_components)  # normalize them so caring matters
            outer_magnitude = spin_components[0] - spin_components[1]  # get it as a number between 0 and 1 for spin
            new_rads = (
                                   outer_magnitude * math.pi) / 6  # pi/3 for whole range -1 to 1, so pi/6 for indivudal components also pay attention to negative.
            base_rads = causes_rads[
                            index_of_interest] - math.pi  # subtract because we are coming from the wrong direction
            final_mag = 5 + 0.5 * inner_magnitude  # how powered the vector is from the center

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
            final_mag = 10 - 0.5 * inner_magnitude  # notice the minus 10 instead of the polus 10 here.

        if base_rads <= -math.pi or base_rads >= 0:  # we are in the top half of the circle, requires counter clockwise
            final_rads = base_rads - new_rads
        else:  # we are in the bottom half of the circle, requires clockwise.
            final_rads = base_rads + new_rads  # calcualte new poisition

        x = final_mag * math.cos(final_rads)  # x and y components fo the new vector
        y = final_mag * math.sin(final_rads)
        return x, y  # return the new vector as a tuple.

    # funciton to create the player nodes positions based on teh current optiosn matrix.
    def create_player_nodes(self):
        player_nodes = []
        for i in range(self.total_players):  # iterate through all players
            current_x, current_y = 0, 0  # gotta start somewhere
            curr_values = self.current_options_matrix[i]  # get our row bc thats all we care about
            curr_negatives = [1 if v < 0 else 0 for v in curr_values]  # keeps track of how many negs and where they are
            num_negatives = sum(curr_negatives)  # to prevent constant reaccessing
            all_negatives_flag = False  # incase we need to up transparency

            if num_negatives == 0:  # normal case, no modificatinos
                norm_matrix = self.normalize_current_options_matrix()
                current_x, current_y = self.normal_coordinates_generation(i, norm_matrix)

            elif num_negatives == 3:  # normal case flipped over origin; set flag as well.
                all_negatives_flag = True
                norm_matrix = self.normalize_current_options_matrix()
                current_x, current_y = self.normal_coordinates_generation(i, norm_matrix)
                current_x *= -1
                current_y *= -1

            elif num_negatives in (1, 2):  # silly billy logic. we need to flip outside unit circle and go from there
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
            position_x = (
                        (position_x * abs(normalized_current_options_matrix[player_id][cause_index])) / (2 * self.rad))
            position_y = (
                        (position_y * abs(normalized_current_options_matrix[player_id][cause_index])) / (2 * self.rad))
            curr_x += position_x
            curr_y += position_y
        return curr_x, curr_y



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
                new_options_matrix.append(row)  # all zeros, just chill
        return new_options_matrix

    def create_choice_matrix(self, current_options_matrix):
        current_options_matrix = [[0] + row for row in current_options_matrix]  # append a 0 to it
        choice_list = [0] * len(current_options_matrix[0])
        for i, row in enumerate(current_options_matrix):
            min_val = min(row)  # lets avoid clamping for now IG.
            adjusted_row = [x - min_val for x in row]
            total = sum(adjusted_row)
            if total == 0:
                normalized_row = [0 for _ in adjusted_row]
            else:
                normalized_row = [x / total for x in adjusted_row]
            choice_list = [choice_list[i] + normalized_row[i] for i in range(len(choice_list))]
        total = sum(choice_list)
        if total != 0: choice_list = [val / total for val in choice_list]
        return choice_list

    def get_winning_probabilities(self):
        return self.winning_probability

    def get_highest_utility_player(self):
        # this is going to be a problem. I need to create a current scoreborad, that should be heplful.
        if len(self.results_sums) == 0:  # no utility? thats fine, pick a random player
            return self.total_order[random.randint(0, self.total_players - 1)]
        else:  # utility time. return the highest.
            return self.total_order[
                self.results_sums.index(max(self.results_sums))]  # return the index of the highest utility player.

    # this functin is used for simulation purposes ONLY. should never be called with live players.
    def let_others_create_options_matrix(self, bot_peeps, curr_round, influence_matrix):

        indexes = [] # this gest used regardless.
        for peep in bot_peeps:
            indexes.append(bot_peeps.index(peep) + 1)

        if isinstance(self.allocation_bots[0], GeneAgent3):
            if self.new_v is not None:
                T_prev = self.new_v # constructs the previous, like, received matrix. kind of.
            else:
                T_prev = [[0 for _ in range(self.total_players)] for _ in range(self.total_players)] # 2d nxn array filled w/ zeros.

            T_prev = np.array(T_prev)
            new_columns = []
            extra_data = {}
            for i in range(self.total_players):
                extra_data[i] = None # we never use government or anything.
            # go ahead and queyr everyone and then organize it later.
            for i in range(len(self.allocation_bots)):
                new_columns.append(self.allocation_bots[i].play_round(
                    i,
                    curr_round,
                    T_prev[:, i], # should be a 9x9 ndarray (from numpy)
                    self.results_sums,
                    np.array(influence_matrix),
                    extra_data, # yes this is blank. no I don't know why.
                ))
            total_columns = []
            for peep in bot_peeps:
                peep_index = peep[1]
                total_columns.append(new_columns[int(peep_index)])
            current_options_matrix = np.transpose(total_columns).tolist()
            return current_options_matrix, indexes

        else:
            list_of_columns = []
            for peep in bot_peeps:
                list_of_columns.append(self.allocation_bots[self.bot_index_dict[peep]].create_column(self.total_players))
            current_options_matrix = np.transpose(list_of_columns).tolist()


            self.current_options_matrix = current_options_matrix
            return current_options_matrix, indexes


    def get_game_deets(self):
        cooperation_score = self.cooperation_score / (self.num_rounds+1) if self.num_rounds > 0 else 0  # as a percent, how often we cooperated. (had a non negative cause pass)
        sc_bot_type = 0 # don't return anything here rn.
        results = self.results # do I actually need this?
        results_sums = self.results_sums
        num_rounds = self.num_rounds
        cv, sums_per_round = self.get_sums_per_round_and_cv()
        influence = self.most_recent_influence
        #utility_per_round = list(zip(*self.get_results_per_round()))
        utility_per_round = self.get_results_per_round()
        avg_utility_per_round = self.get_average_utility_per_round()
        avg_rise = (avg_utility_per_round[-1]-10) / num_rounds

        total_data = {
            "cooperation_score": cooperation_score,
            "avg_rise": avg_rise,
            "results": results,
            "result_sums": results_sums,
            "num_rounds": num_rounds,
            "sums_per_round": sums_per_round,
            "cv": cv,
            "influence": influence,
            "utility_per_round": utility_per_round,
            "avg_utility_per_round": avg_utility_per_round,
        }

        #return cooperation_score, avg_rise, results, results_sums, num_rounds, sums_per_round, cv, influence, utility_per_round, avg_utility_per_round
        return total_data


    def get_sums_per_round_and_cv(self):
        results = self.results
        num_rounds = self.num_rounds
        sums_per_round = {}
        for bot in results:
            sums_per_round[bot] = []
            current_sum = 0
            for i, new_sum in enumerate(results[bot]):
                current_sum += new_sum
                sums_per_round[bot].append(current_sum)

        new_list = []
        for bot in sums_per_round:
            new_list.append(sums_per_round[bot][num_rounds - 1])
        std = np.std(new_list)
        mean = np.mean(new_list)
        cv = std / abs(mean)  # measures distribution bet  ter than, say, std or mean on their own.
        return cv, sums_per_round