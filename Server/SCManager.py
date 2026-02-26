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

# this is garrett code. Yo no touchy.
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
        self.sc_sim = Social_Choice_Sim(num_players, 3, num_humans, options_generator, 0, self.round_num, total_order, False)
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
        self.allocations = False # just look that over super quick.

    # this is the runner, and what main window and server will actually call.
    def play_sc_round(self, influence_matrix, possible_peeps, curr_round, curr_sc_round, indexes, captain_model, highest_pop_player):
        if influence_matrix is not None: # just incase we are playing SC on its own.
            new_influence = influence_matrix
        else:
            new_influence = self.sc_sim.get_influence_matrix
        # not a refactor per se, but made the code much more readable.
        current_options_matrix = self.init_next_round(possible_peeps, curr_round, new_influence, captain_model, highest_pop_player) # gets the current options matrix and starts SC_init
        self.play_social_choice_round(curr_round, new_influence, current_options_matrix, curr_sc_round, captain_model, highest_pop_player) # actually does the voting and whatnot.
        print("SC ROUND FINISHED")

    # starts the next round, prepares the packet and gets the new options matrix. gets all ducks in a row.
    def init_next_round(self, possible_peeps, curr_round, new_influence, captain_model, highest_pop_player):
        captain = -1 if not captain_model else self.total_order.index(highest_pop_player)


        # Initialize the round
        if self.allocations:
            options_and_peeps = self.server_side_options_matrix(possible_peeps.tolist(), curr_round, new_influence, captain)
        else:
            options_and_peeps = None

        self.sc_sim.start_round(options_and_peeps) # make sure this actually gets hard set.
        self.current_options_matrix = self.sc_sim.current_options_matrix
        print("This is the current options matrix ", self.current_options_matrix)
        self.options_history[self.round_num] = self.current_options_matrix
        self.player_nodes = self.sc_sim.get_player_nodes()
        self.causes = self.sc_sim.get_causes()
        self.all_nodes = self.causes + self.player_nodes

        # captain mode stuff. if not captain mode, captain is -1. else, captain gets a silly label :)


        self.connection_manager.distribute_message("SC_INIT", self.round_num, self.current_options_matrix,
                                                   [node.to_json() for node in self.all_nodes],
                                                   self.current_options_matrix, captain)
        return self.current_options_matrix


    # ...yeah the naming convention isn't great but IDK what else to call it.
    def play_social_choice_round(self, curr_round, influence_matrix, current_options_matrix, curr_sc_round, captain_model, highest_pop_player):

        # Run the voting and collect the votes
        zero_idx_votes, one_idx_votes = self.run_sc_voting(curr_round, influence_matrix, captain_model, highest_pop_player)
        self.sc_sim.set_final_votes(zero_idx_votes)
        self.update_vote_effects(zero_idx_votes, current_options_matrix,
                                 curr_round)  # Tracks the effects of each player's vote on everyone else

        # TODO make it so that background math isn't needed with the captain model
        # Calculate the winning vote
        self.sc_sim.current_options_matrix = current_options_matrix # maybe??

        winning_vote, new_utilities = self.sc_sim.return_win(zero_idx_votes) # actually runs the backround math
        # print("here is the winning vote ", winning_vote)
        self.sc_sim.save_results() # just gets all our ducks in a row.
        new_utilities = copy.copy(self.sc_sim.get_new_utilities())
        new_utilities = {str(k): sum(v) for k,v in new_utilities.items()}

        self.connection_manager.distribute_message("SC_OVER", self.round_num, winning_vote, new_utilities,
                                                   self.positive_vote_effects_history,
                                                   self.negative_vote_effects_history, zero_idx_votes,
                                                   self.current_options_matrix, self.sc_sim.get_influence_matrix())

        time.sleep(.5)  # Without this, messages get sent out of order, and the sc_history gets screwed up.
        self.sc_sim.set_rounds(curr_sc_round)  # last thing we do, thats da rule.

    # get the bot votes and the player votes, let everyone know what was happening last time.
    def run_sc_voting(self, curr_sc_round, influence_matrix, captain_model, highest_pop_player):
        player_votes = {}
        is_last_cycle = False
        previous_votes = {}
        zero_idx_votes = {}
        one_idx_votes = {}
        captain = -1
        is_last_cycle = False

        # just go ahead and run this always.
        highest_pop_index = self.total_order.index(highest_pop_player)
        captain = -1 if not captain_model else highest_pop_index  # if there is no captain, -1. else, captain time.

        # so if the captain model is not acgive
        # just do everything normally. simple as.

        # ok here me out
        #
        captain_vote = False

        for cycle in range(1): # ONLY DO ONE VOTE CYCLE!! VERY IMPORTANT!!!
            player_votes.clear()
            self.connection_manager.flush_all_client_sockets()  # lets give this a whirl.


            while len(player_votes) < self.connection_manager.num_clients:
                responses = self.connection_manager.get_responses()
                # print("these are hte responses I am getting ", responses)
                for response in responses.values():
                    try:
                        # print("this is the len of respones ", len(player_votes))
                        player_votes[response["CLIENT_ID"]] = response["FINAL_VOTE"]
                        print("this is what the highest pop index looks like ", highest_pop_index)
                        print("this is what the client ID looks like ", response["CLIENT_ID"])

                        if str(highest_pop_index) in player_votes: # if we have the captains vote
                            print("CAPTAINS VOTE ACCEPTED")
                            captain_vote = True
                            break # we can break early and go from there. # prolly need to make sure it gets padded correctly
                            # but it SHOULD be fine.


                    except KeyError:
                        pass
                        # print("here are all keys being processed:  client_id", response["CLIENT_ID"], "vote ",  response["FINAL_VOTE"], "and the id ", player_votes[str(highest_pop_index)])
                        print("SOMEONE SHOULDN't BE ALLOWED TO TOUCH THIS YET. FIX THAT")
                if captain_vote:
                    print("we have dribbled down. breaking .... ")

            # combines bots and player votes and saves the appropraite votes to all they spots
            print("we have escaped this darn place.... how quaint...")

            zero_idx_votes, one_idx_votes = self.compile_sc_votes(player_votes,
                                                                  curr_sc_round, cycle, previous_votes, influence_matrix, captain_model)

            previous_votes[cycle] = zero_idx_votes
            # send out the stubbins
            if cycle == self.vote_cycles - 1: is_last_cycle = True
            highest_pop_index = self.total_order.index(highest_pop_player)
            captain = -1 if not captain_model else highest_pop_index  # if there is no captain, -1. else, captain time.
            self.connection_manager.distribute_message("SC_VOTES", zero_idx_votes, cycle + 1, is_last_cycle, captain)




            captain_vote = zero_idx_votes[highest_pop_index]
            captain = -1 if not captain_model else highest_pop_index  # if there is no captain, -1. else, captain time.

            zero_idx_votes = {i: -1 for i in range(len(zero_idx_votes))}
            one_idx_votes = [-1 for _ in range(len(one_idx_votes))]
            zero_idx_votes[highest_pop_index] = captain_vote
            one_idx_votes[highest_pop_index] = captain_vote  # not sure if that will work but we can try.

            self.connection_manager.distribute_message("SC_VOTES", zero_idx_votes, cycle + 1, is_last_cycle, captain)

        # zero clue why this is what we are returning Imma be so real
        return zero_idx_votes, one_idx_votes # no reason to ask for these again, only ask for em once.

    # just combines them and updates the backround history.
    def compile_sc_votes(self, player_votes, round_num, cycle, previous_votes, influence_matrix, captain_model):
        bot_votes = self.sc_sim.get_votes(previous_votes, round_num, cycle, self.vote_cycles, influence_matrix)

        all_votes = {**bot_votes, **player_votes} # player votes being second is MANDATORY.
        all_votes_list = [option_num + 1 if option_num != -1 else -1 for option_num in
                          all_votes.values()]  # Convert 0-based votes to 1-based for display, but leave voters of -1 as they are
        self.options_votes_history[round_num] = all_votes  # Saves the history of votes
        if cycle < self.vote_cycles:
            self.sc_sim.record_votes(all_votes, cycle)
        return all_votes, all_votes_list

    # Garrett code I no touchy.
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

    # this just runs getting the optison matrix, but from the server. distribut the poacket and whatnot.
    def server_side_options_matrix(self, peeps, curr_round, influence_matrix, captain):
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
                                                   actual_total_order_index, captain)  # reset all the utilities and whatnot, just in case.
        client_input = self.connection_manager.get_responses()
        player_columns = {}
        for client_id, response in client_input.items():
            try:
                player_columns[self.total_order[client_id]] = (response["UTILITIES"])
            except KeyError:
                print("Error processing client_input (yes where you think it is): ", client_input)

        # copied as much as I could directly from the sim, these are a little uggly but they work.
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
            return total_columns, peeps  # this should be the new current options matix. maybe.



