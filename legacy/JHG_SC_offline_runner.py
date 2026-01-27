# so this allows me to run the fetcher and create visualizations based off of scenarios and whatnot.

from Server.social_choice_sim import Social_Choice_Sim
from Server.JHGManager import JHG_simulator
from tqdm import tqdm
import numpy as np


from offlineSimStuff.variousGraphingTools.completeVersions.completeGrapher import CompleteGrapher
from legacy.outDated.sc_tools import causeNodeGraphVisualizer
# from legacy.outDated.jhg_tools import influenceGrapher
from Server.OptionGenerators.generators import generator_factory
from legacy.outDated.completeLogger import CompleteLogger

# starts the sim, could make this take command line arguments
# takes in a bot type, a number of rounds, and then runs it and plots the results. plans for expansion coming soon.
def run_trial(sc_sim, jhg_sim, rounds_list, num_cycles, create_graphs, group, total_order, create_influence, current_logger):

    sc_sim.set_group(group)
    played_sc = False
    played_jhg = False
    influence_matrix = None # this should get overwritten pretty quick, but its there so there's no error.
    curr_sc_round = 0
    for list_index in tqdm(range(0, len(round_list))): # everything NEEDS to start at 1, PLEASE.

        sc_rounds = round_list[list_index][-1] == "*"
        curr_round = int(round_list[list_index][:-1])

        influence_matrix = run_jhg_stuff(jhg_sim, curr_round, current_logger)
        played_jhg = True

        if sc_rounds:
            run_sc_stuff(sc_sim, jhg_sim, total_order, influence_matrix, curr_sc_round, current_logger)
            played_sc = True
            curr_sc_round += 1

        if create_graphs:
            pass
            graphEverything(sc_sim, jhg_sim, curr_round, played_sc, played_jhg)

        # just want to have some sort of insight into what is happening.
        if curr_sc_round == 1000:
            graphEverything(sc_sim, jhg_sim, curr_round, played_sc, played_jhg)


    current_logger.gather_ending_deets("TRIAL_TRIAL_TRIAL")
    sc_sim.set_rounds(curr_round)
    graph_long_term_stuff(sc_sim, curr_round)

    return sc_sim, jhg_sim

def run_sc_stuff(sc_sim, jhg_sim, total_order, influence_matrix, curr_round, current_logger):
    sc_sim.set_rounds(curr_round)
    possible_peeps, indexes = generate_peeps(total_order, jhg_sim, sc_sim)  # people who are needed to create the matrix
    # should I make this, you know, an entirely different bot? having them in the same file feels wrong becuase they are doing differen things.
    current_options_matrix, peeps = sc_sim.let_others_create_options_matrix(possible_peeps.tolist(), curr_round, sc_sim.get_influence_matrix())  # actually creates the matrix
    sc_sim.start_round((current_options_matrix, indexes))

    bot_votes = {}
    for cycle in range(num_cycles):
        bot_votes[cycle] = sc_sim.get_votes(bot_votes, curr_round, cycle, num_cycles)
        sc_sim.record_votes(bot_votes[cycle], cycle)

    # make sure that this happens IMMEDIATELY afterward.
    winning_vote, round_results = sc_sim.return_win(
        bot_votes[num_cycles - 1])  # we need this to run, even if we don't need the results HERE per se
    sc_sim.save_results()
    current_logger.save_sc_round(curr_round)

def run_jhg_stuff(jhg_sim, curr_round, current_logger):
    jhg_sim.execute_round(None, curr_round)  # no client input, thats crazy talk here. run a JHG round.
    influence_matrix = jhg_sim.get_influence()  # need this for friend recognition and whatnot.
    current_logger.save_jhg_round(curr_round) # lets try not runing it wiht the logger.
    return influence_matrix

def graph_long_term_stuff(sc_sim, curr_round):
    current_grapher = CompleteGrapher()
    current_grapher.draw_long_term_graphs(sc_sim)

def generate_peeps(total_order, jhg_sim, sc_sim):
    popularity_array = (jhg_sim.get_popularities()) # huh
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

# takes in a list of peeps (player or bot or both) and returns their player indexes as per total order
def peeps_to_total_order(peeps, total_order):
    indexes = []
    for peep in peeps:
        indexes.append(total_order.index(peep)+1)
    return indexes



def graph_nodes(sim):
    currVisualizer = causeNodeGraphVisualizer()
    currVisualizer.create_graph_with_sim(sim)

def graph_influence(sim):
    curr_influence_grapher = influenceGrapher(sim.total_players) # gotta be a smarter way for this to read it so it doesn't get passed all teh way down.
    curr_influence_grapher.create_graph(sim.I, sim.results_sums, sim.round)

def graphEverything(sc_sim, jhg_sim, curr_round, played_sc, played_jhg):
    curr_everything_grapher = CompleteGrapher()
    curr_everything_grapher.create_graph_with_sims(curr_round, sc_sim, jhg_sim, played_sc, played_jhg)


def create_sim(total_players, scenario=None, chromosomes=None, group="", total_order=None, allocation_scenario=None, utility_per_player=3):

    cycle = -1 # a negative cycle indicates to me that this is a test - that, or something is really really wrong.
    curr_round = -1
    num_causes = 3

    generator = generator_factory(2, total_players, 5, 10, -10, 3, None, None)
    sc_sim = Social_Choice_Sim(total_players, num_causes, num_humans, generator, cycle, curr_round, chromosomes, scenario, group, total_order, allocation_scenario, utility_per_player)
    return sc_sim

def create_jhg_sim(num_humans, num_players, total_order, tokens_per_player):
    jhg_sim = JHG_simulator(num_humans, num_players, total_order, tokens_per_player)
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

def determine_rounds(jhg_rounds_per_sc_game_list):
    num_games_in_cycle = jhg_rounds_per_sc_game_list
    new_list = []
    max_item = 0
    for instance in num_games_in_cycle:
        for i in range(instance):
            new_list.append(str(i + max_item) + "-")
        new_list.pop()
        new_list.append(str(len(new_list)) + "*")
        max_item = len(new_list)

    #print("This is the new list ", new_list, " and here is what we were workign with ", jhg_rounds_per_sc_game_list)
    return new_list


if __name__ == "__main__":
    # jhg_games_per_sc_round = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    jhg_games_per_sc_round = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    round_list = determine_rounds(jhg_games_per_sc_round)
    num_cycles = 3
    num_players = 9
    num_humans = 0
    tokens_per_player = 2
    utility_per_player = 3
    create_graphs = True
    create_influence = True
    total_groups = ["", 0, 1, 2]
    chromosomes_directory = "testChromosome"
    group = ""
    # these paths are relative to the file location, so as long as you don't move the file it can and will run from anywhere.
    scenario = "scenarioIndicator/cheetahAttempt"
    chromosome = "chromosomes/experiment"
    allocation_bot_type = "allocations_scenarios/social_welfare"
    total_order = create_total_order(num_players, num_humans)

    current_jhg_sim = create_jhg_sim(num_humans, num_players, total_order, tokens_per_player)
    current_sc_sim = create_sim(num_players, scenario, chromosome, group, total_order, allocation_bot_type, utility_per_player)
    current_logger = CompleteLogger()
    sc_sim, jhg_sim = run_trial(current_sc_sim, current_jhg_sim, round_list, num_cycles, create_graphs, group, total_order, create_influence, current_logger)
