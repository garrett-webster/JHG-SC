from Server.jhg_sim import JHG_simulator
from legacy.outDated.jhg_tools.jhgLogger import JHGLogger
import time

class JHGManager:
    def __init__(self, connection_manager, num_humans, num_players, num_bots, total_order, tokens_per_player, jhg_bot_types, addAgents):
        self.current_round = 1
        self.connection_manager = connection_manager
        self.num_players = num_players
        self.jhg_sim = JHG_simulator(num_humans, num_players, total_order, tokens_per_player, jhg_bot_types, True, addAgents)
        self.num_bots = num_bots
        self.currentLogger : JHGLogger = JHGLogger(self.jhg_sim)
        self.alpha = self.jhg_sim.sim.engine.alpha
        self.total_order = total_order
        self.num_humans = num_humans

    def play_jhg_round(self, round_num, is_last_jhg_round):
        # time.sleep(5) # this only goes in when we are tesing with a lot of people I think
        # this section of code (next 11 lines or so) exist only to grab any and all instances of player input for JHG engine.
        print("We are now expecting client input. This might be done in a different thread")
        client_input = None
        time.sleep(1) # IDK just see if this helps

        if self.num_humans > 0:
            while True:
                self.connection_manager.flush_all_client_sockets()  # lets give this a whirl.
                client_input = self.connection_manager.get_responses()  # Gets responses of type "JHG"

                try:
                    first_key = next(iter(client_input))
                    client_input[first_key]["ALLOCATIONS"]
                    break
                except KeyError:
                    print("Error processinging client_input: ", client_input)

        # only thing that actually matters for offline play. just run the new round. (don't use round num - 1 ig)
        # time.sleep(3) ## WARNING: PUT THIS BACK IN BEFORE PLAY TESTS
        current_popularity = self.jhg_sim.execute_round(client_input, round_num)

        # go ahead and grab everything we need and send it out ot the relavent clients.
        # Creates a 2d array where each row corresponds to the allocation list of the player with the associated id
        allocations_matrix = self.jhg_sim.get_T()
        sent_dict, received_dict = self.get_sent_and_received(allocations_matrix)
        unique_messages = [received_dict, sent_dict]
        init_pop_influence = (1 - self.alpha) ** round_num * 100
        self.connection_manager.distribute_message("JHG_OVER", round_num, list(current_popularity),
                                                   self.jhg_sim.get_influence().tolist(), init_pop_influence, is_last_jhg_round,
                                                   unique_messages=unique_messages)


        return self.jhg_sim.get_influence()


    def get_sent_and_received(self, allocations_matrix):
        sent_dict = {}
        received_dict = {}

        for client_id in self.connection_manager.clients.keys():
            sent = [0 for _ in range(self.num_players)]
            received = [0 for _ in range(self.num_players)]
            for player in range(self.num_players):
                sent[player] = allocations_matrix[client_id][player]
                received[player] = allocations_matrix[player][client_id]
            sent_dict[client_id] = sent
            received_dict[client_id] = received

        return sent_dict, received_dict


    def get_highest_popularity_player(self):
        return self.jhg_sim.get_highest_popularity_player()

    def get_influence_matrix(self):
        return self.jhg_sim.get_influence()

    def get_sim(self):
        return self.jhg_sim

    def get_popularity_array(self, total_order):
        return self.jhg_sim.get_popularities()
