import random
import time

import numpy as np

from Server.social_choice_sim import Social_Choice_Sim

import copy

def create_empty_vote_matrix(num_players):
    return [[0 for _ in range(num_players)] for _ in range(num_players)]


class SCManager:
    def __init__(self, connection_manager, num_humans, options_generator, num_players, num_bots, sc_group_option, vote_cycles, sc_logging, total_order):
        self.connection_manager = connection_manager
        self.round_num = 1
        self.save_dict = {}
        self.big_dict = {}
        self.utilities = {i: 0 for i in range(num_humans)}
        # num_humans, bot_type
        # so the arguments here are total_players, likely type bot and group option, if I had to guess.
        scenario = "../JHG-SC/offlineSimStuff/scenarioIndicator/cheetahAttempt"
        chromosomes = "../JHG-SC/offlineSimStuff/chromosomes/experiment"
        #print("this is the total ordering ", total_order)
        self.sc_sim = Social_Choice_Sim(num_players, 3, num_humans, options_generator, 3, 0, chromosomes, scenario, "", total_order)
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

        self.sc_logger = sc_logging
        self.total_order = total_order # keeps track of which are players and which are bots.

    def init_next_round(self, current_options_matrix):
        # Initialize the round
        self.sc_sim.start_round(current_options_matrix) # make sure this actually gets hard set.
        self.current_options_matrix = current_options_matrix
        self.options_history[self.round_num] = self.current_options_matrix
        self.player_nodes = self.sc_sim.get_player_nodes()
        self.causes = self.sc_sim.get_causes()
        self.all_nodes = self.causes + self.player_nodes

        self.connection_manager.distribute_message("SC_INIT", self.round_num, self.current_options_matrix,
                                                   [node.to_json() for node in self.all_nodes],
                                                   self.current_options_matrix)



    def play_social_choice_round(self, jhg_sim):
        # first we gotta GET the new current options matrix. thats a pain.
        peeps = self.generate_peeps(self.sc_sim, jhg_sim, self.total_order)
        #self.server_side_options_matrix(peeps, jhg_sim.get_influence())
        # Run the voting and collect the votes
        player_votes = self.run_sc_voting()
        # this is the line where we get the bot votes as well.
        previous_votes = {}
        print("Here is self.vote cycles, might be wrong", self.vote_cycles)
        # always start from cycle 0, don't use the max one. methinks.
        zero_idx_votes, one_idx_votes = self.compile_sc_votes(player_votes, self.round_num, 0, previous_votes) # no clue what cycle this is or why this runs.
        self.sc_sim.set_final_votes(zero_idx_votes)
        # this is weird garrett stuff Imma not touch it.
        self.update_vote_effects(zero_idx_votes, self.current_options_matrix,
                                 self.round_num)  # Tracks the effects of each player's vote on everyone else


        # Calculate the winning vote
        winning_vote, new_utilities = self.sc_sim.return_win(zero_idx_votes)
        #print("did we have a winning vote ?", winning_vote)
        #print("These are the utilities ", new_utilities)

        self.sc_sim.save_results()
        self.sc_sim.set_rounds(self.round_num) # should set it to the last number of rounds before calculation. I hope this works.
        new_utilities = copy.copy(self.sc_sim.get_new_utilities())
        new_utilities = {str(k): sum(v) for k,v in new_utilities.items()}
        #print("here are the new utilities ", new_utilities)


        self.connection_manager.distribute_message("SC_OVER", self.round_num, winning_vote, new_utilities,
                                                   self.positive_vote_effects_history,
                                                   self.negative_vote_effects_history, zero_idx_votes,
                                                   self.current_options_matrix)

        time.sleep(.5)  # Without this, messages get sent out of order, and the sc_history gets screwed up.
        if self.sc_logger:
            pass
            #print("this is round ", self.round_num)
            #self.current_logger.add_round_to_sim(self.round_num)
        self.round_num += 1
        # I don't know when we are going to want to generate this, but likely at the start of the next round.
        #self.init_next_round()

    def run_sc_voting(self):
        player_votes = {}
        is_last_cycle = False
        previous_votes = {}

        for cycle in range(self.vote_cycles):
            print("Cycle under run sc voting ", cycle)
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
                                                                  self.round_num, cycle, previous_votes)
            previous_votes[cycle] = zero_idx_votes
            if cycle == self.vote_cycles - 1: is_last_cycle = True
            self.connection_manager.distribute_message("SC_VOTES", zero_idx_votes, cycle + 1, is_last_cycle)

        return player_votes

    def compile_sc_votes(self, player_votes, round_num, cycle, previous_votes):
        print("Here is teh cycle that we are inputting here ", cycle)
        bot_votes = self.sc_sim.get_votes(previous_votes, round_num, cycle, self.vote_cycles)

        all_votes = {**bot_votes, **player_votes}
        all_votes_list = [option_num + 1 if option_num != -1 else -1 for option_num in
                          all_votes.values()]  # Convert 0-based votes to 1-based for display, but leave voters of -1 as they are
        self.options_votes_history[round_num] = all_votes  # Saves the history of votes
        if cycle < self.vote_cycles:
            #print("recording for cycle " , cycle)
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

    def server_side_options_matrix(self, peeps, influence_matrix):
        player_peeps = []
        bot_peeps = []
        total_columns = []
        player_columns = []
        total_order_index = []
        actual_total_order_index = []
        for peep in peeps: # find all player peeps first
            actual_total_order_index.append(self.total_order.index(peep))
            if peep[0] == "B": bot_peeps.append(peep)
            else: player_peeps.append(peep), total_order_index.append(self.total_order.index(peep)) # actual client ID.

        #total_columns.append(self.sc_sim.let_others_create_options_matrix(bot_peeps, influence_matrix))
        # now we have to get teh player input. I don't know how to handle this as well to be entirely honesty.
        if len(player_peeps) > 0:  # only enter this loop if there are clients to question.
            print("player peeps are non zero. engaging target.")
            self.connection_manager.distribute_message("SC_OPTIONS_CREATE", total_order_index, actual_total_order_index)  # reset all the utilities and whatnot, just in case.
            print("Starting to wait for lcient input....")
            client_input = self.connection_manager.get_responses()
            print("we are pretty sure we have recieved all client input. Doing math....")
            player_columns = {}
            for client_id, response in client_input.items():
                try:
                    player_columns[self.total_order[client_id]] = (response["UTILITIES"])
                except KeyError:
                    print("Error processing client_input (yes where you think it is): " , client_input)
        print("here are the client columns ", player_columns)

        bot_columns = []
        for bot in self.sc_sim.bots:
            bot_columns.append(bot.create_column(len(self.total_order)))

        final_columns = {}
        for bot, i in enumerate(bot_peeps):
            final_columns[i] = bot_columns[bot] # hopefully
        for player, i in enumerate(player_peeps):
            final_columns[i] = player_columns[i]

        # should do all the orginization of the final columns and leave it in the original peeps thing.
        for peep in peeps:
            total_columns.append(final_columns[peep])



        # we gotta hope this works
        print("Here is the total order ", self.total_order)
        print("Here are the total columns" , total_columns)
        total_columns = (np.array(total_columns).transpose()).tolist()

        return total_columns # this should be the new current options matix. maybe.

    def generate_peeps(self, sc_sim, jhg_sim, total_order):
        highest_utility = sc_sim.get_highest_utility_player()
        highest_pop = jhg_sim.get_highest_popularity_player()
        if highest_utility == highest_pop:
            pass  # well fetch, what DO we do here? let them create it twice?
        possible_players = copy.deepcopy(total_order)
        for player in {highest_utility,
                       highest_pop}:  # lets me use a set to make sure that I only erase it once. This should allow for both to be the same thing in the list and have the same player make 2 things.
            if player in possible_players:
                possible_players.remove(player)
        random_player = random.choice(possible_players)
        peeps = [highest_utility, highest_pop, random_player]
        return peeps