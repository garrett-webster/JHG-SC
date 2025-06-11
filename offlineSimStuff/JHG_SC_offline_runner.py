# so this allows me to run the fetcher and create visualizations based off of scenarios and whatnot.
import copy
import random

from Server.social_choice_sim import Social_Choice_Sim
from Server.JHGManager import JHG_simulator
from tqdm import tqdm

from offlineSimStuff.variousGraphingTools.sc_tools.causeNodeGraphVisualizer import causeNodeGraphVisualizer
from Server.OptionGenerators.generators import generator_factory


# starts the sim, could make this take command line arguments
# takes in a bot type, a number of rounds, and then runs it and plots the results. plans for expansion coming soon.
def run_trial(sc_sim, jhg_sim, num_rounds, num_cycles, create_graphs, group, total_order):
    # ok so what do I actually want to happen in here
    # i need to run as many rounds as I want of JHG and SC-sim
    # i could allow for differing rounds? I will probably initalize that and pass it into run trial
    # num cycles is also important,
    # not sure how I am going to easily create the JHG graphs, or the tokens allocations. I will ahve to figure it out.
    # but lets start with running a single round of JHG with da bots, then a single round of SC_sim, and then graphing all of it.
    # should be fun.
    # sc_sim.set_round(num_rounds)
    sc_sim.set_group(group)
    for curr_round in tqdm(range(0, num_rounds)):
        jhg_sim.execute_round(None, curr_round) # no client input, thats crazy talk here. run a JHG round.
        influence_matrix = jhg_sim.get_influence_matrix() # need this for friend recognition and whatnot.
        possible_peeps = generate_peeps(sc_sim, jhg_sim, total_order) # people who are needed to create the matrix
        # should I make this, you know, an entirely different bot? having them in the same file feels wrong becuase they are doing differen things.
        current_options_matrix = sc_sim.let_others_create_options_matrix(possible_peeps, influence_matrix) # actually creates the matrix
        sc_sim.start_round(current_options_matrix)

        bot_votes = {}
        for cycle in range(num_cycles):
            bot_votes[cycle] = sc_sim.get_votes(bot_votes, curr_round, cycle, num_cycles)
            sc_sim.record_votes(bot_votes[cycle], cycle)

        if create_graphs:
            graph_nodes(sc_sim)
        sc_sim.save_results()

    return sc_sim, jhg_sim



def generate_peeps(sc_sim, jhg_sim, total_order):
    highest_utility = sc_sim.get_highest_utility_player()
    highest_pop = jhg_sim.get_highest_popularity_player()
    if highest_utility == highest_pop:
        pass # well fetch, what DO we do here? let them create it twice?
    possible_players = copy.deepcopy(total_order)
    for player in {highest_utility, highest_pop}: # lets me use a set to make sure that I only erase it once. This should allow for both to be the same thing in the list and have the same player make 2 things.
        if player in possible_players:
            possible_players.remove(player)
    random_player = random.choice(possible_players)
    peeps = [highest_utility, highest_pop, random_player]
    return peeps


def graph_nodes(sim):
    currVisualizer = causeNodeGraphVisualizer()
    currVisualizer.create_graph_with_sim(sim)


def create_sim(total_players, scenario=None, chromosomes=None, group="", total_order=None):

    cycle = -1 # a negative cycle indicates to me that this is a test - that, or something is really really wrong.
    curr_round = -1
    num_causes = 3

    generator = generator_factory(2, total_players, 5, 10, -10, 3, None, None)
    sc_sim = Social_Choice_Sim(total_players, num_causes, num_humans, generator, cycle, curr_round, chromosomes, scenario, group, total_order)
    return sc_sim

def create_jhg_sim(num_humans, num_players, total_order):
    jhg_sim = JHG_simulator(num_humans, num_players, total_order)
    return jhg_sim


def create_total_order(total_players, num_humans):
    total_order = []
    num_bots = total_players - num_humans
    total_order = []
    for bot in range(num_bots):
        total_order.append("B" + str(bot))
    for human in range(num_humans):
        total_order.append("P" + str(human))
    return total_order


if __name__ == "__main__":
    num_rounds = 3
    num_cycles = 3
    num_players = 9
    num_humans = 0
    create_graphs = True
    total_groups = ["", 0, 1, 2]
    chromosomes_directory = "testChromosome"
    group = ""
    # these paths are relative to the file location, so as long as you don't move the file it can and will run from anywhere.
    scenario = "scenarioIndicator/cheetahAttempt"
    chromosome = "chromosomes/experiment"
    total_order = create_total_order(num_players, num_humans)

    current_jhg_sim = create_jhg_sim(num_humans, num_players, total_order)
    current_sc_sim = create_sim(num_players, scenario, chromosome, group, total_order)
    sc_sim, jhg_sim = run_trial(current_sc_sim, current_jhg_sim, num_rounds, num_cycles, create_graphs, group, total_order)
    # probs_list = sc_sim.get_winning_probabilities()
    # print("Average winning probs ", sum(probs_list) / num_rounds)
    # print("min winning probs ", min(probs_list))
    # print("max winning probs ", max(probs_list))
    # print("median winning probs ", statistics.median(probs_list))
    # print("here was the winning probability ", sum(updated_sim.get_winning_probabilities()) / num_rounds)
    #current_visualizer = longTermGrapher()
    #current_visualizer.draw_graph_from_sim(updated_sim)


    big_boy_json = {}
