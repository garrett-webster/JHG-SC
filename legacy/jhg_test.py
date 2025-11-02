from Server.jhg_sim import JHG_simulator
from legacy.outDated import CompleteLogger
from offlineSimStuff.variousGraphingTools.completeVersions.completeGrapher import CompleteGrapher

# this doesn't really get used anymore. it was a useful proof of concept but can now be ignored.

def create_sim(num_humans, num_players, total_order, tokens_per_player, jhg_bot_type):
    jhg_sim = JHG_simulator(num_humans, num_players, total_order, tokens_per_player, jhg_bot_type)
    return jhg_sim

def run_trial(sim, num_rounds, create_graphs, current_logger):

    for curr_round in range(num_rounds):
        influence_matrix = run_jhg_stuff(sim, curr_round, current_logger, curr_round)

    current_logger.gather_ending_deets(0)
    return sim

def run_jhg_stuff(sim, curr_round, current_logger, curr_logger_round):
    sim.execute_round(None, curr_round)  # no client input, thats crazy talk here. run a JHG round.
    influence_matrix = sim.get_influence()  # need this for friend recognition and whatnot.
    current_logger.save_jhg_round(curr_round, curr_logger_round) # lets try not runing it wiht the logger.
    return influence_matrix


def create_total_order(total_players, num_humans):
    total_order = []
    num_bots = total_players - num_humans
    total_order = []
    for bot in range(num_bots):
        total_order.append("B" + str(bot))
    for human in range(num_humans):
        total_order.append("P" + str(human))
    return total_order



if __name__ == '__main__':
    num_players = 12
    num_humans = 0 # I Don't want any players. does that make this harder? Yes! I am gonna ignore that for now.
    create_graphs = True
    num_rounds = 20
    tokens_per_player = 2
    jhg_bot_type = 0 # use the geneagent bots
    current_logger = CompleteLogger()
    total_order = create_total_order(num_players, num_humans)
    current_sim = create_sim(num_humans, num_players, total_order, tokens_per_player, jhg_bot_type)
    current_logger.resetup(current_sim, None)
    updated_sim = run_trial(current_sim, num_rounds, create_graphs, current_logger)
    current_logger.gather_ending_deets(0)
    current_logger.create_big_boy_graphs(num_rounds, num_rounds * 0)

    curr_everything_grapher = CompleteGrapher()
    curr_everything_grapher.draw_long_term_graphs_given_logger(current_logger)