"""
the goal of this script is to make a JHG engine that can run
and then from there, I can test the allocations and whatnot from that JHG script to try and understand intent
I want to see if the staghunt_to_jhg function is broken or what.
steps: get just a jhg game running and make sure it works
track the allocations
run them through the thing, track intents
measure with various bots.
break.
"""
from tqdm import tqdm
from offlineSimStuff.runningTools.runnerHelper import * # get all the functions
from Server.Engine.simulator import GameSimulator
from stagHare.environment.jhgToStaghunt import allocation_to_movement, allocation_to_intent
from stagHare.runnerHelper import create_hunters_with_list
from stagHare.runnerHelper import *  # this SHOULD be all we need.
import numpy as np

def extractGene(gene_dict):
    gene_str = "gene_"
    values = list(gene_dict.values())
    result = "_".join(map(str, values))
    gene_str += result
    return gene_str


# base_to_csv = {
#     "SCab": "16x16round4.csv",
#     "HCab": "gen_z.csv",
#     "ECab99": "gen_99.csv",
#     "ECab199": "gen_199.csv",
#     "Allegatr": "Allegatr",
# }


def get_agents(agent, scenario):
    if scenario == "SelfPlay":
        if agent in base_to_csv:
            new_list = [base_to_csv[agent] for _ in range(3)]
        else:
            new_list = ["GStag" for _ in range(3)]
    else:
        if "Allegatr" in scenario:
            opponent_type = scenario[0:-1]  # "Allegatr"
        else:
            opponent_type = scenario[1:6]  # "GHare" or "GStag"

        num_opponents = int(scenario[-1])
        num_test_agents = 3 - num_opponents

        test_agents = [base_to_csv[agent] for _ in range(num_test_agents)]
        opponents = [opponent_type for _ in range(num_opponents)]

        new_list = test_agents + opponents


    return new_list

def run_test(curr_agent_name, scenario_type, height, width, random_agents, forced_random, GamesPerRound, graphing):

    # how many resources can we actually devote to this??
    max_workers = max(1, os.cpu_count() - 2)  # save just a few for other processes, plz don't crash.
    # max_workers = 1 # spawns only a single thread, simplifying debugging.

    new_object = run_trial_all(curr_agent_name, height, width, random_agents, forced_random,
                                scenario_type, GamesPerRound, graphing)
    popularities = new_object.popularity_during_game

    return popularities


def run_test_with_agents(hunters, noisy):

    run_amount = 1
    graphing = False
    current_round_grapher = None
    current_game_logger = None

    stag_hare = get_stag_hare(height, width, hunters)
    popularity_over_time = []
    intents = []
    positions = []

    for i in range(run_amount):  # if we only do 1 game, we only do this once.
        # does this suck? possibly.

        stag_hare.state.hunting_hare_map = {"R" + str(i): 2 for i in range(3)}  # Fill with NULL value

        # consolidated this into one super function, tests are in the test suite.
        new_score, new_intents, new_positions, popularity_over_time, _ = run_trial_debugging(stag_hare, graphing,
                                                                                                current_round_grapher,
                                                                                                current_game_logger,
                                                                                                noisy)

        popularity_over_time = popularity_over_time
        intents = new_intents
        positions = new_positions

        # just set up a new state that doesn't break immediately
        stag_hare = reset_stag_hare(stag_hare)

    return popularity_over_time, intents, positions, allocations


def create_agents_and_hunters(agent_name):

    agents = create_genetic_agents(3, [], agent_name, forced_random, random_agents)

    gene_dict = []
    for agent in agents:
        gene_dict.append(agent.genes_long)

    genes = []
    for gene in gene_dict:
        genes.append(extractGene(gene[0]))

    hunters = create_hunters_with_genes(genes, random_agents, forced_random)

    # hunters and gene agents are now exactly the same, which is what we are expecting.
    for i, gene in enumerate(genes):
        assert (extractGene(hunters[i].agent.genes_long[0]) == extractGene(agents[i].genes_long[0]))

    return agents, hunters



height = 16
width = 16
RandomAgents = True
forced_random = False
num_attempts = 100



if __name__ == "__main__":

    random_agents = False
    forced_random = True

    scenario = "SelfPlay"
    game_type = "Round"
    graphing = False
    num_games_per_round = 10
    print_results_to_console = True
    agent_name = "hardHomo.csv"
    noisy = True # THIS IS CRUCIAL HOLY MOLY WE NEED THIS
    # need this to be the same agents...
    agents, hunters = create_agents_and_hunters(agent_name)


    # FIRST THE STAGHARE THINGY.
    np.random.seed(42)
    popularities_during_game, intents = run_test_with_agents(hunters, noisy)
    num_rounds = len(popularities_during_game)