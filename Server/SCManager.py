import time

from Server.social_choice_sim import Social_Choice_Sim
from Server.options_creation import generate_two_plus_one_groups
from offlineSimStuff.variousGraphingTools.simLogger import simLogger # this logs stuff
import copy

def create_empty_vote_matrix(num_players):
    return [[0 for _ in range(num_players)] for _ in range(num_players)]


class SCManager:
    def __init__(self, connection_manager, num_humans, num_players, num_bots, sc_group_option, vote_cycles, sc_logging, total_order):
        self.connection_manager = connection_manager
        self.round_num = 1
        self.save_dict = {}
        self.big_dict = {}
        self.utilities = {i: 0 for i in range(num_humans)}
        # num_humans, bot_type
        # so the arguments here are total_players, likely type bot and group option, if I had to guess.
        scenario = "../JHG-SC/offlineSimStuff/scenarioIndicator/somewhatMoreAwareGreedy"
        chromosomes = "../JHG-SC/offlineSimStuff/chromosomes/highestFromTesting"
        self.sc_sim = Social_Choice_Sim(num_players, 3, num_humans, 3, 0, chromosomes, scenario, "")
        self.sc_groups = generate_two_plus_one_groups(num_players, sc_group_option)
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
        self.current_logger = simLogger(self.sc_sim) # go ahead and prep it anyway.
        self.total_order = total_order # keeps track of which are players and which are bots.

    def init_next_round(self):
        # Initialize the round
        self.sc_sim.start_round() # I don't want there to be groups. A mi no me gusta. for now.
        self.current_options_matrix = self.sc_sim.get_current_options_matrix()
        self.options_history[self.round_num] = self.current_options_matrix
        self.player_nodes = self.sc_sim.get_player_nodes()
        self.causes = self.sc_sim.get_causes()
        self.all_nodes = self.causes + self.player_nodes

        self.connection_manager.distribute_message("SC_INIT", self.round_num, self.current_options_matrix,
                                                   [node.to_json() for node in self.all_nodes],
                                                   self.current_options_matrix)

    def play_social_choice_round(self):
        # Run the voting and collect the votes
        player_votes = self.run_sc_voting()
        # this is the line where we get the bot votes as well.
        previous_votes = {}
        zero_idx_votes, one_idx_votes = self.compile_sc_votes(player_votes, self.round_num, self.vote_cycles, previous_votes) # no clue what cycle this is or why this runs.
        self.sc_sim.set_final_votes(zero_idx_votes)
        # this is weird garrett stuff Imma not touch it.
        self.update_vote_effects(zero_idx_votes, self.current_options_matrix,
                                 self.round_num)  # Tracks the effects of each player's vote on everyone else


        # Calculate the winning vote
        winning_vote, new_utilities = self.sc_sim.return_win(zero_idx_votes)
        print("did we have a winning vote ?", winning_vote)
        print("These are the utilities ", new_utilities)

        self.sc_sim.save_results()
        self.sc_sim.set_rounds(self.round_num) # should set it to the last number of rounds before calculation. I hope this works.
        new_utilities = copy.copy(self.sc_sim.get_new_utilities())
        new_utilities = {str(k): sum(v) for k,v in new_utilities.items()}
        print("here are the new utilities ", new_utilities)


        self.connection_manager.distribute_message("SC_OVER", self.round_num, winning_vote, new_utilities,
                                                   self.positive_vote_effects_history,
                                                   self.negative_vote_effects_history, zero_idx_votes,
                                                   self.current_options_matrix)

        time.sleep(.5)  # Without this, messages get sent out of order, and the sc_history gets screwed up.
        if self.sc_logger:
            print("this is round ", self.round_num)
            self.current_logger.add_round_to_sim(self.round_num)
        self.round_num += 1
        self.init_next_round()

    def run_sc_voting(self):
        player_votes = {}
        is_last_cycle = False
        previous_votes = {}

        for cycle in range(self.vote_cycles):
            player_votes.clear()
            # Waits for a vote from each client
            while len(player_votes) < self.connection_manager.num_clients:
                responses = self.connection_manager.get_responses()
                for response in responses.values():
                    player_votes[response["CLIENT_ID"]] = response["FINAL_VOTE"]

            zero_idx_votes, one_idx_votes = self.compile_sc_votes(player_votes,
                                                                  self.round_num, cycle, previous_votes)
            previous_votes[cycle] = zero_idx_votes
            if cycle == self.vote_cycles - 1: is_last_cycle = True
            self.connection_manager.distribute_message("SC_VOTES", zero_idx_votes, cycle + 1, is_last_cycle)

        return player_votes

    def compile_sc_votes(self, player_votes, round_num, cycle, previous_votes):
        bot_votes = self.sc_sim.get_votes(previous_votes, round_num, cycle)

        all_votes = {**bot_votes, **player_votes}
        all_votes_list = [option_num + 1 if option_num != -1 else -1 for option_num in
                          all_votes.values()]  # Convert 0-based votes to 1-based for display, but leave voters of -1 as they are
        self.options_votes_history[round_num] = all_votes  # Saves the history of votes
        if cycle < self.vote_cycles:
            print("recording for cycle " , cycle)
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
