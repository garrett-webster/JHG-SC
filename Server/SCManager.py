import random
import time

import numpy as np

from Server.Engine.completeBots.geneagent3 import GeneAgent3
from Server.social_choice_sim import Social_Choice_Sim

from Server.Engine.completeBots.completeSocialWelfare import SocialWelfare
from Server.Engine.completeBots.humanagent import HumanAgent
from Server.Engine.completeBots.jakecat import JakeCAT
from Server.Engine.completeBots.improvedJakeCate import ImprovedJakeCat
from Server.Engine.completeBots.projectCat import ProjectCat
from Server.Engine.completeBots.antiCat import AntiCat


import copy

def create_empty_vote_matrix(num_players):
    return [[0 for _ in range(num_players)] for _ in range(num_players)]


class SCManager:
    def __init__(self, connection_manager, num_humans, options_generator, num_players, num_bots, sc_group_option, vote_cycles, total_order, utility_per_player, bots):
        self.connection_manager = connection_manager
        self.round_num = 1
        self.save_dict = {}
        self.big_dict = {}
        self.utilities = {i: 0 for i in range(num_humans)}
        # num_humans, bot_type
        # so the arguments here are total_players, likely type bot and group option, if I had to guess.
        scenario = "../JHG-SC/offlineSimStuff/scenarioIndicator/cheetahAttempt"
        chromosomes = "../JHG-SC/offlineSimStuff/chromosomes/experiment"
        allocation_scenario = "../JHG-SC/offlineSimStuff/allocations_scenarios/social_welfare"
        #print("this is the total ordering ", total_order)
        self.sc_sim = Social_Choice_Sim(num_players, 3, num_humans, options_generator, 3, 0, chromosomes, scenario, "", total_order, allocation_scenario, utility_per_player)
        self.sc_sim.bot_ovveride(bots)
        #self.sc_groups = generate_two_plus_one_groups(num_players, sc_group_option)
        self.num_players = num_players
        self.num_bots = num_bots
        self.vote_cycles = vote_cycles

        # Tracking the SC game over time
        self.options_history = {}
        self.options_votes_history = {}
        # Tracks how the vote of every player would have affected each player had that cause passed
        self.vote_effects = create_empty_vote_matrix(num_players)
        self.vote_effects_history = {}
        self.positive_vote_effects_history = create_empty_vote_matrix(num_players)
        self.negative_vote_effects_history = create_empty_vote_matrix(num_players)

        self.total_order = total_order # keeps track of which are players and which are bots.

    def play_sc_round(self, influence_matrix, possible_peeps, curr_round, curr_sc_round, indexes):
        if influence_matrix is not None:
            new_influence = influence_matrix
        else:
            new_influence = self.sc_sim.get_influence_matrix

        current_options_matrix, peeps = self.server_side_options_matrix(possible_peeps.tolist(), curr_round, new_influence)
        self.init_next_round((current_options_matrix, indexes))
        self.sc_sim.start_round((current_options_matrix, peeps))  # this might be screwing stuff up honestly....
        self.current_options_matrix = current_options_matrix
        self.play_social_choice_round(curr_round, new_influence, current_options_matrix)
        self.sc_sim.set_rounds(curr_sc_round)


    def init_next_round(self, options_and_peeps=None):
        # Initialize the round
        self.sc_sim.start_round(options_and_peeps) # make sure this actually gets hard set.
        self.current_options_matrix = self.sc_sim.current_options_matrix
        self.options_history[self.round_num] = self.current_options_matrix
        self.player_nodes = self.sc_sim.get_player_nodes()
        self.causes = self.sc_sim.get_causes()
        self.all_nodes = self.causes + self.player_nodes

        self.connection_manager.distribute_message("SC_INIT", self.round_num, self.current_options_matrix,
                                                   [node.to_json() for node in self.all_nodes],
                                                   self.current_options_matrix)



    def play_social_choice_round(self, curr_round, influence_matrix, current_options_matrix):
        # first we gotta GET the new current options matrix. thats a pain.
        # Run the voting and collect the votes
        player_votes = self.run_sc_voting(curr_round, influence_matrix)

        # this is the line where we get the bot votes as well.
        previous_votes = {}
        # always start from cycle 0, don't use the max one. methinks.
        zero_idx_votes, one_idx_votes = self.compile_sc_votes(player_votes, curr_round, 0, previous_votes, influence_matrix) # no clue what cycle this is or why this runs.
        self.sc_sim.set_final_votes(zero_idx_votes)
        # this is weird garrett stuff Imma not touch it.
        self.update_vote_effects(zero_idx_votes, current_options_matrix,
                                 curr_round)  # Tracks the effects of each player's vote on everyone else


        # Calculate the winning vote
        self.sc_sim.current_options_matrix = current_options_matrix # maybe??
        if curr_round == 9:
            pass
        winning_vote, new_utilities = self.sc_sim.return_win(zero_idx_votes)
        print("this is the winning vote we are passing over ", winning_vote)
        # if winning_vote != -1:
        #     winning_vote -= 1
        # #print("did we have a winning vote ?", winning_vote)
        # #print("These are the utilities ", new_utilities)
        # print("this is what we are sending over as the winning vote ", winning_vote)
        self.sc_sim.save_results()
        self.sc_sim.set_rounds(self.round_num) # should set it to the last number of rounds before calculation. I hope this works.
        new_utilities = copy.copy(self.sc_sim.get_new_utilities())
        new_utilities = {str(k): sum(v) for k,v in new_utilities.items()}
        #print("here are the new utilities ", new_utilities)


        self.connection_manager.distribute_message("SC_OVER", self.round_num, winning_vote, new_utilities,
                                                   self.positive_vote_effects_history,
                                                   self.negative_vote_effects_history, zero_idx_votes,
                                                   self.current_options_matrix, self.sc_sim.get_influence_matrix())

        time.sleep(.5)  # Without this, messages get sent out of order, and the sc_history gets screwed up.


    def run_sc_voting(self, curr_sc_round, influence_matrix):
        player_votes = {}
        is_last_cycle = False
        previous_votes = {}

        for cycle in range(self.vote_cycles):
            player_votes.clear()
            # Waits for a vote from each client
            while len(player_votes) < self.connection_manager.num_clients:
                responses = self.connection_manager.get_responses()
                for response in responses.values():
                    try:
                        player_votes[response["CLIENT_ID"]] = response["FINAL_VOTE"]
                    except KeyError:
                        print("SOMEONE SHOULDN't BE ALLOWED TO TOUCH THIS YET. FIX THAT")


            zero_idx_votes, one_idx_votes = self.compile_sc_votes(player_votes,
                                                                  curr_sc_round, cycle, previous_votes, influence_matrix)
            previous_votes[cycle] = zero_idx_votes

            if cycle == self.vote_cycles - 1: is_last_cycle = True
            self.connection_manager.distribute_message("SC_VOTES", zero_idx_votes, cycle + 1, is_last_cycle)

        return player_votes

    def compile_sc_votes(self, player_votes, round_num, cycle, previous_votes, influence_matrix):
        bot_votes = self.sc_sim.get_votes(previous_votes, round_num, cycle, self.vote_cycles, influence_matrix)

        all_votes = {**bot_votes, **player_votes} # player votes being second is MANDATORY.
        all_votes_list = [option_num + 1 if option_num != -1 else -1 for option_num in
                          all_votes.values()]  # Convert 0-based votes to 1-based for display, but leave voters of -1 as they are
        self.options_votes_history[round_num] = all_votes  # Saves the history of votes
        if cycle < self.vote_cycles:
            self.sc_sim.record_votes(all_votes, cycle)
        return all_votes, all_votes_list

    def update_vote_effects(self, all_votes, current_options_matrix, round_num):
        round_vote_effects = create_empty_vote_matrix(self.num_players)
        for i in range(self.num_players):
            selected_vote = all_votes[i]  # Which option the ith player voted for
            if selected_vote != -1:
                for j in range(self.num_players):
                    vote_effect = current_options_matrix[j][selected_vote]
                    self.vote_effects[j][i] += vote_effect  # The effect of the ith player's vote on the jth player
                    round_vote_effects[i][j] = vote_effect

                    if vote_effect > 0:
                        self.positive_vote_effects_history[i][j] += vote_effect
                    elif vote_effect < 0:
                        self.negative_vote_effects_history[i][j] += vote_effect
        self.vote_effects_history[str(round_num)] = round_vote_effects

    def get_bot_votes(self):
        self.sc_sim.get_votes()

    def finish_results(self, filename):
        self.current_logger.finish_json(filename)

    def get_highest_utility_player(self):
        return self.sc_sim.get_highest_utility_player()

    def server_side_options_matrix(self, peeps, curr_round, influence_matrix):
        player_peeps = []
        bot_peeps = []
        total_order_index = []
        actual_total_order_index = []
        for peep in peeps:  # find all player peeps first
            actual_total_order_index.append(self.total_order.index(peep))
            if peep[0] == "B":
                bot_peeps.append(peep)
            else:
                player_peeps.append(peep), total_order_index.append(self.total_order.index(peep))  # actual client ID.

        # here we have the client creation stuff
        self.connection_manager.distribute_message("SC_OPTIONS_CREATE", total_order_index,
                                                   actual_total_order_index)  # reset all the utilities and whatnot, just in case.
        print("prolly makes it here")
        client_input = self.connection_manager.get_responses()
        player_columns = {}
        for client_id, response in client_input.items():
            try:
                player_columns[self.total_order[client_id]] = (response["UTILITIES"])
            except KeyError:
                print("Error processing client_input (yes where you think it is): ", client_input)
        print("betcha it crashes BEFORE this one ")
        allocation_bots = self.sc_sim.allocation_bots
        new_v = self.sc_sim.new_v

        if isinstance(allocation_bots[0], GeneAgent3) or isinstance(allocation_bots[0], SocialWelfare) or isinstance(allocation_bots[0], AntiCat):  # make sure he is in there too
            if new_v is not None:
                T_prev = new_v  # constructs the previous, like, received matrix. kind of.
            else:
                T_prev = [[0 for _ in range(self.num_players)] for _ in range(self.num_players)]  # 2d nxn array filled w/ zeros.

            T_prev = np.array(T_prev)
            new_columns = []
            extra_data = {}
            for i in range(self.num_players):
                extra_data[i] = None  # we never use government or anything.
            # go ahead and queyr everyone and then organize it later.
            for i in range(len(allocation_bots)):
                new_columns.append(allocation_bots[i].play_round(
                    i,
                    curr_round,
                    T_prev[:, i],  # should be a 9x9 ndarray (from numFpy)
                    self.sc_sim.results_sums,
                    np.array(influence_matrix),
                    extra_data,  # yes this is blank. no I don't know why.
                    True,  # this indicates that it is happening within the SC testbed.
                ))
            final_columns = {}
            for bot, i in enumerate(bot_peeps): # fingers crossed this ends up where we want it to go
                final_columns[i] = new_columns[bot]
            for player, i in enumerate(player_peeps):
                final_columns[i] = player_columns[i]
            total_columns = []
            for peep in peeps:
                total_columns.append(final_columns[peep])
                # we gotta hope this works
            total_columns = (np.array(total_columns).transpose()).tolist()
            print("here are the total columns and the peeps ", total_columns, " " , peeps)

            return total_columns, peeps  # this should be the new current options matix. maybe.

