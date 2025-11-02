# so this allows me to run the fetcher and create visualizations based off of scenarios and whatnot.
import time
from Server.social_choice_sim import Social_Choice_Sim
from tqdm import tqdm
import numpy as np

from legacy.outDated import causeNodeGraphVisualizer
from Server.OptionGenerators.generators import generator_factory
from legacy.outDated import CompleteLogger
from offlineSimStuff.variousGraphingTools.completeVersions.completeGrapher import CompleteGrapher

# starts the sim, could make this take command line arguments
# takes in a bot type, a number of rounds, and then runs it and plots the results. plans for expansion coming soon.
def run_trial(sim, num_rounds, num_cycles, create_graphs, group, total_order, current_logger):
    # we need to get the groups, where we can have no groups or a variety of groups.

    start_time = time.time() # so we can calculate total time. not entirely necessary.
    sim.set_group(group)

    for curr_round in tqdm(range(num_rounds)): # do this outside the sim, could make it inside but I like it outside.
        sim.set_rounds(num_rounds)  # for graphing purposes
        sim.start_round() # creates the current current options matrix, makes da player nodes, sets up causes, etc.
        possible_peeps, indexes = generate_peeps(total_order,
                                                 sim)  # people who are needed to create the matrix
        influence_matrix = sim.get_influence_matrix()
        current_options_matrix, peeps = sim.let_others_create_options_matrix(possible_peeps.tolist(), # problem
                                                                                curr_round, sim.get_influence_matrix())  # actually creates the matrix
        bot_votes = {}
        for cycle in range(num_cycles):
            #print("*****************STARTING CYCLE " + str(cycle+1) + "************************")
            bot_votes[cycle] = sim.get_votes(bot_votes, curr_round, cycle, num_cycles)
            sim.record_votes(bot_votes[cycle], cycle)


        winning_vote, round_results = sim.return_win(bot_votes[num_cycles-1])  # is all votes, works here
        sim.save_results()
        current_logger.save_sc_round(curr_round, curr_round) # there is no reason


    current_logger.gather_ending_deets(0)
    return sim


def graph_nodes(sim):
    currVisualizer = causeNodeGraphVisualizer()
    currVisualizer.create_graph_with_sim(sim)


def create_sim(total_players, scenario=None, chromosomes=None, group="", total_order=None, allocation_scenario=None, utility_per_player=3):

    # SUM: this sets the bot list type, so we can have siutaions set up
    if scenario is None:
        scenario = r"C:\Users\Sean\Documents\GitHub\OtherGarrettStuff\JHG-SC\offlineSimStuff\scenarioIndicator\humanAttempt3"
    if chromosomes is None:
        chromosomes = r"C:/Users/Sean/Documents/GitHub/OtherGarrettStuff/JHG-SC/offlineSimStuff/chromosomes/highestFromTesting.csv"
    cycle = -1 # a negative cycle indicates to me that this is a test - that, or something is really really wrong.
    curr_round = -1
    total_players = 9
    num_causes = 3
    num_humans = 0
    generator = generator_factory(2, total_players, 5, 10, -10, 3, None, None)
    sim = Social_Choice_Sim(total_players, num_causes, num_humans, generator, cycle, curr_round, chromosomes, scenario, group, total_order, allocation_scenario, utility_per_player)
    return sim

def create_total_order(total_players, num_humans):
    total_order = []
    num_bots = total_players - num_humans
    total_order = []
    for bot in range(num_bots):
        total_order.append("B" + str(bot))
    for human in range(num_humans):
        total_order.append("P" + str(human))
    return total_order

def generate_peeps(total_order, sc_sim):
    popularity_array = [100 for _ in range(len(total_order))]
    total = sum(popularity_array)
    # this is easy bc this will always be positive
    normalized_popularity_array = [val / total for val in popularity_array]
    # THIS IS WORSE.
    utilities_array = sc_sim.results_sums
    global_shift = min(0, min(utilities_array))
    # shift everything over. subtract bc its either 0 or a negative number.
    utilities_array = [val - global_shift for val in utilities_array]
    total = sum(utilities_array) # yeah override this why not.
    normalized_utility_array = [val / total if total != 0 else 1 / len(total_order) for val in utilities_array]
    # new goal -- figure out how zip works
    overall_probability_array = [(p + u) / 2 for p, u in zip(normalized_popularity_array, normalized_utility_array)]
    probabilities = np.array(overall_probability_array)
    new_world_order = np.array(total_order)
    # shoudl pull without replacement from total order using the overall probability array, gives 3 choies without replacement.
    new_peeps = np.random.choice(new_world_order, p=probabilities, size=3, replace=False)
    indexes = peeps_to_total_order(new_peeps, total_order)
    return new_peeps, indexes

def peeps_to_total_order(peeps, total_order):
    indexes = []
    for peep in peeps:
        indexes.append(total_order.index(peep)+1)
    return indexes



if __name__ == "__main__":
    num_rounds = 100
    num_cycles = 3
    num_players = 9
    num_humans = 0
    create_graphs = True
    total_groups = ["", 0, 1, 2]
    chromosomes_directory = "testChromosome"
    group = ""
    # these paths are relative to the file location, so as long as you don't move the file it can and will run from anywhere.
    scenario = "scenarioIndicator/humanAttempt3"
    chromosome = "chromosomes/experiment"
    allocation_bot_type = ""
    utility_per_player = 3
    total_order = create_total_order(num_players, 0)
    current_logger = CompleteLogger()

    current_sim = create_sim(num_players, scenario, chromosome, group, total_order, allocation_bot_type, utility_per_player)
    current_logger.resetup(None, current_sim)
    updated_sim = run_trial(current_sim, num_rounds, num_cycles, create_graphs, group, total_order, current_logger)
    current_logger.gather_ending_deets(0)
    current_logger.create_big_boy_graphs(num_rounds, num_rounds * 0)  # also weird logger stuff

    curr_everything_grapher = CompleteGrapher()
    curr_everything_grapher.draw_long_term_graphs_given_logger(current_logger)


