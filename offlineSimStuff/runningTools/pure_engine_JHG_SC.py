# so this allows me to run the fetcher and create visualizations based off of scenarios and whatnot.
import copy
import random

from Server.social_choice_sim import Social_Choice_Sim
# from Server.JHGManager import JHG_simulator
from Server.Engine.simulator import GameSimulator

from tqdm import tqdm
import numpy as np
import os
import matplotlib.pyplot as plt

from Server.OptionGenerators.generators import generator_factory

from Server.Engine.completeBots.geneagent3 import GeneAgent3
# from Server.Engine.completeBots.basicGeneAgent3 import BasicGeneAgent3

# from offlineSimStuff.variousGraphingTools.individualLoggers.roundLogger import RoundLogger
# from offlineSimStuff.variousGraphingTools.individualLoggers.gameLogger import GameLogger
# from offlineSimStuff.variousGraphingTools.groupStuff.groupLogger import GroupLogger
# from offlineSimStuff.variousGraphingTools.completeVersions.completeGrapher import CompleteGrapher
# from offlineSimStuff.variousGraphingTools.groupStuff.groupGrapher import GroupGrapher

# import random
#
# seed_value = 42
# random.seed(seed_value)


# starts the sim, could make this take command line arguments
# takes in a bot type, a number of rounds, and then runs it and plots the results. plans for expansion coming soon.
def run_trial(agents, sc_sim: "Social_Choice_Sim", jhg_sim, round_list, num_cycles, group, total_order, pops):

    sc_sim.set_group(group)
    played_sc = False
    played_jhg = False
    curr_sc_round = 0
    influence_matrix = None # this should get overwritten pretty quick, but its there so there's no error.
    for list_index in (range(0, len(round_list))): # fixed, we start at 0 now.
        jhg_round = False
        sc_round = False



        sc_rounds = round_list[list_index][-1] == "*"
        jhg_rounds = round_list[list_index][-1] == "-"
        curr_round = int(round_list[list_index][:-1]) # useful, yes, but not quite the logger round
        # print("this si the curr round ", curr_round)

        # print("*****************************ROUND ", curr_round, "********************************")

        if jhg_rounds:
            influence_matrix = run_jhg_stuff(jhg_sim, curr_round, agents, len(agents))
            played_jhg = True
            jhg_round = True
            pops.append(jhg_sim.get_popularity())

        # if sc_rounds:
        #     print("IF this goes off I'm ending up on the news")
        #     old_influence_matrix = copy.copy(influence_matrix)
        #     influence_matrix, winning_vote = run_sc_stuff(sc_sim, jhg_sim, total_order, influence_matrix, curr_round, num_cycles)
        #     sc_sim.set_rounds(curr_sc_round) # ???
        #     curr_sc_round += 1
        #     played_sc = True
        #     sc_round = True


        # round_logger.save_round(curr_round, sc_rounds, jhg_rounds)


        # if create_round_graphs_bool:
        #     create_round_graphs(round_logger, curr_round, sc_rounds, jhg_rounds)

    # if create_game_graphs_bool:
    #     game_logger.save_game(played_sc, played_jhg)
    #     create_game_graphs(game_logger)

    return sc_sim, jhg_sim, pops


# def run_sc_stuff(sc_sim, jhg_sim, total_order, influence_matrix, curr_round, num_cycles):
#     # sc_sim.set_rounds(curr_round) # don't set that here methinks, let it ride.
#     possible_peeps, indexes = generate_peeps(total_order, jhg_sim, sc_sim)  # people who are needed to create the matrix
#     if influence_matrix is not None:
#         new_influence = influence_matrix
#     else:
#         new_influence = sc_sim.get_influence_matrix() # if there is no JHG influence, we are flying solo, leach off of own influence
#     # should I make this, you know, an entirely different bot? having them in the same file feels wrong beuase they are doing differen things.
#     current_options_matrix, peeps = sc_sim.let_others_create_options_matrix(possible_peeps.tolist(), curr_round, new_influence)  # actually creates the matrix
#     # print("these are the peeps" , peeps)
#     sc_sim.start_round((current_options_matrix, indexes))
#
#     bot_votes = {}
#     for cycle in range(num_cycles):
#         bot_votes[cycle] = sc_sim.get_votes(bot_votes, curr_round, cycle, num_cycles, influence_matrix)
#         sc_sim.record_votes(bot_votes[cycle], cycle)
#
#     # make sure that this happens IMMEDIATELY afterward.
#     winning_vote, round_results = sc_sim.return_win(bot_votes[num_cycles - 1])
#     new_influence = np.array(sc_sim.get_influence_matrix()) # ACTUALLY UPDATE THE FETCHER
#     sc_sim.save_results()
#     return new_influence, winning_vote # takes our modified influence and makes sure to feed it back into the jhg sim so we get a cyclical affect.
#

# def reconcile_influence(jhg_influence, sc_influence):
#     # ok this fetcher uses convex recombination to put the two together and then uses the frobenius norm to decide on the magnitude to adjust back too. bars!
#     # alpha = 0.5 # THIS iS JUST A STARTER VALUE, WILL LIKELY BE MADE INTO A GENE OR WHATEVER.
#     alpha = 0.5 # THIS iS JUST A STARTER VALUE, WILL LIKELY BE MADE INTO A GENE OR WHATEVER.
#     # Alpha of 0 is entirely JHG, alpha of 1 is entirely SC. I started with 0.5 but worry that that might have been too flattening.
#
#     if sc_influence is None:
#         print("something wrong :(")
#         return jhg_influence
#
#     sc_influence = np.array(sc_influence)
#     jhg_influence = np.array(jhg_influence) # This shbould never get used but it couldn't hurt
#
#     jhg_norm = np.linalg.norm(jhg_influence, 'fro')
#
#     combined = (1 - alpha) * jhg_influence + alpha * sc_influence
#
#     combined_norm = np.linalg.norm(combined, 'fro')
#     if combined_norm == 0:
#         return np.zeros_like(jhg_influence)
#
#     rescaled = combined * (jhg_norm / combined_norm)
#     return rescaled


def run_jhg_stuff(jhg_engine, curr_round, agents, num_players):
    transactions = [0 for _ in range(num_players)]  # so this is how I replilcate it in python.
    T_prev = jhg_engine.get_transaction()

    for i in range(num_players):

        transactions[i] = agents[i].play_round(
            i,
            curr_round,
            T_prev[:,i],
            jhg_engine.get_popularity(),
            jhg_engine.get_influence(),
            jhg_engine.get_extra_data(i),
            # False
        )
    jhg_engine.play_round(transactions)  # thanks references
    # ok so now I have to return
    # the change in popularities,
    # return sc_sim.current_results, sc_sim.results_sums, new_influence  # so we have the change in utility and overall utility

    return jhg_engine.get_influence()  # return da influence matrix, the change in popularitry, and the new popularities.


# def generate_peeps(total_order, jhg_sim, sc_sim):
#     popularity_array = (jhg_sim.get_popularities()) # huh
#     total = sum(popularity_array)
#     # this is easy bc this will always be positive
#     normalized_popularity_array = [val / total for val in popularity_array]
#     # THIS IS WORSE.
#     utilities_array = sc_sim.results_sums
#     global_shift = min(0, min(utilities_array))
#     # shift everything over. subtract bc its either 0 or a negative number.
#     utilities_array = [val - global_shift for val in utilities_array]
#     total = sum(utilities_array) # yeah override this why not.
#     normalized_utility_array = [val / total if total != 0 else 1 / len(total_order) for val in utilities_array]
#     # new goal -- figure out how zip works
#     overall_probability_array = [(p + u) / 2 for p, u in zip(normalized_popularity_array, normalized_utility_array)]
#     probabilities = np.array(overall_probability_array)
#     new_world_order = np.array(total_order)
#     # shoudl pull without replacement from total order using the overall probability array, gives 3 choies without replacement.
#     new_peeps = np.random.choice(new_world_order, p=probabilities, size=3, replace=False)
#     indexes = peeps_to_total_order(new_peeps, total_order)
#     return new_peeps, indexes


# def create_round_graphs(round_logger, curr_round, played_jhg, played_sc):
#     pass
#     # complete_grapher = CompleteGrapher()
#     # complete_grapher.create_round_graphs_with_round_logger(round_logger, curr_round, played_jhg, played_sc)
#
# def create_game_graphs(game_logger):
#     pass
#     # complete_grapher = CompleteGrapher()
#     # complete_grapher.create_game_graphs_with_logger(game_logger)
#
# def create_group_graphs(group_logger):
#     pass
#     # group_grapher = GroupGrapher()
#     # group_grapher.create_graph(group_logger.get_group_data())

# # takes in a list of peeps (player or bot or both) and returns their player indexes as per total order
# def peeps_to_total_order(peeps, total_order):
#     indexes = []
#     for peep in peeps:
#         indexes.append(total_order.index(peep)+1)
#     return indexes


def create_sim(total_players, scenario=None, chromosomes=None, group="", total_order=None, allocation_scenario=None, utility_per_player=3):
    cycle = -1 # a negative cycle indicates to me that this is a test - that, or something is really really wrong.
    curr_round = -1
    num_causes = 3
    generator = generator_factory(2, total_players, 5, 10, -10, 3, None, None)
    sc_sim = Social_Choice_Sim(total_players, num_causes, num_humans, generator, cycle, curr_round, chromosomes, scenario, group, total_order, allocation_scenario, utility_per_player)
    return sc_sim


def create_jhg_sim(num_humans, num_players, total_order, tokens_per_player, jhg_bot_type, addAgents):
    poverty_line = 0
    forcedRandom = False # lets try this for fun
    alpha = 0.2  # double check these magical fetchers when you get the chance actually.
    beta = 0.5
    give = 1.3
    keep = 0.95
    steal = 1.6
    base_pop = 100

    game_params = {
        "num_players": num_players,
        "alpha": alpha_min,  # np.random.uniform(alpha_min, alpha_max),
        "beta": beta_min,  # np.random.uniform(beta_min, beta_max),
        "keep": keep_min,  # np.random.uniform(keep_min, keep_max),
        "give": give_min,  # np.random.uniform(give_min, give_max),
        "steal": steal_min,  # np.random.uniform(steal_min, steal_max),
        "poverty_line": poverty_line,
        "base_popularity": np.array(initial_pops)
        # "base_popularity": np.array([*[base_pop]*(num_players)])
        # "base_popularity": np.array(random.sample(range(1, 200), num_players))

    }

    for a in agents:
        a.setGameParams(game_params, forcedRandom)


    jhg_engine = GameSimulator(game_params)
    return jhg_engine


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
    new_list = [] # WHEEE gotta start somewhere
    if jhg_rounds_per_sc_game_list[0] == "J" or jhg_rounds_per_sc_game_list[0] == "S":
        print("engaging pure opertaiopns, standing by")
        if jhg_rounds_per_sc_game_list[0] == "J":
            num_rounds = int(jhg_rounds_per_sc_game_list[-1]) # possibly one of the jankier lines that I have ever written but here we are
            for i in range(num_rounds):
                new_list.append(str(i) + "-")

        if jhg_rounds_per_sc_game_list[0] == "S":
            num_rounds = int(jhg_rounds_per_sc_game_list[-1])
            for i in range(num_rounds):
                new_list.append(str(i) + "*")


    else:
        new_list = []
        current = 0  # Tracks number for "-" entries
        for instance in jhg_rounds_per_sc_game_list:
            for _ in range(instance):
                new_list.append(f"{current}-")
                current += 1
            new_list.append(f"{current - 1}*")  # Append the last "-" number with "*"

    return new_list

def loadPopulationFromFile(popSize, num_gene_pools, tokens_per_player):
    fnombre = "Kill me"
    try:
        file_name = os.path.join("Engine", "botGenerations") # creates standard file path. we then append to this.

        # file_name = os.path.join(file_name, "assassins_gen_175")  # trying to be better and mroe aggressive on group forming
        file_name = os.path.join(file_name, "gen_199.csv") # JHG cab agents as used in the study
        # file_name = os.path.join(file_name, "sc_jhg_gen_299.csv") # the smartest vanilla agents
        # file_name = os.path.join(file_name, "w_kitties_gen_256.csv") # attempting to overcome cats
        # file_name = os.path.join(file_name, "jhg_sc_w_one_cat.csv") # another attempt
        # file_name = os.path.join(file_name, "convex2.csv") # this one should do well against the cats in both settings.
        # file_name = os.path.join(file_name, "bestOfWorstConvex.csv")
        # file_name = os.path.join(file_name, "backToBasics299.csv")

        my_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(my_path, file_name)
        fnombre = r"C:\Users\Sean Smith\Documents\GitHub\JHG-SC\Server\Engine\botGenerations\gen_199.csv" # cause whatever man.

        fp = open(fnombre, "r")
    except FileNotFoundError:
        try:
            fnombre = "../Server/Engine/gen_199.csv"
            fp = open(fnombre, "r")
        except FileNotFoundError:
            print(fnombre + " not found")
            quit()

    thePopulation = []

    for i in range(0,popSize):
        line = fp.readline()
        words = line.split(",")

        thePopulation.append(GeneAgent3(words[0], num_gene_pools, tokens_per_player))
        # thePopulation.append(BasicGeneAgent3(words[0], num_gene_pools))
        thePopulation[i].count = float(words[1])
        thePopulation[i].relativeFitness = float(words[2])
        thePopulation[i].absoluteFitness = float(words[3])

    fp.close()

    return thePopulation



if __name__ == "__main__":

    import random
    import numpy as np

    SEED = 42  # pick any constant

    random.seed(SEED)  # Python’s stdlib RNG
    np.random.seed(SEED)  # NumPy’s RNG

    # various batch scenarios I keep on hand for reference.
    #jhg_games_per_sc_round = [1,1,1,1,1,1,1,1]#,1,1,1,1,1,1,1,1,1,1,1,1]
    # jhg_games_per_sc_round = [4,3,3,3,3,3,3,3] # what we trained the og assasain agents on.
    # jhg_games_per_sc_round = [4, 3, 3, 3, 3]
    # jhg_games_per_sc_round = [4,3,3,3,3]  # what we trained the sleepy assasain bots on.
    # jhg_games_per_sc_round = [2,3,3]#,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2]
    jhg_games_per_sc_round = ["J", 30]
    # jhg_games_per_sc_round = [1,1,1]
    # jhg_games_per_sc_round = [2,2,2]


    round_list = determine_rounds(jhg_games_per_sc_round)
    num_cycles = 3
    num_players = 10


    num_humans = 0
    tokens_per_player = 2
    utility_per_player = 3
    create_round_graphs_bool = False
    create_game_graphs_bool = True
    create_influence = False
    chromosomes_directory = "testChromosome"
    group = ""
    # these paths are relative to the file location, so as long as you don't move the file it can and will run from anywhere.
    scenario = "scenarioIndicator/allRandom"
    chromosome = "chromosomes/experiment"
    allocation_bot_type = "allocations_scenarios/random"
    jhg_bot_type = 0 # 0 is gene bots, 2 is social welfare and 3 is random. 4 is the new social welfare that I am developing that is just a hair smarter.

    num_attempts = 1 # number of batches to do.
    num_rounds = sum(jhg_games_per_sc_round) if len(jhg_games_per_sc_round) > 2 else jhg_games_per_sc_round[-1] # if its a list, len of list. else, grab the second identifier

    file_name = os.path.join("../..", "Server", "Engine", "scenarios", "workingDirectory")
    my_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.normpath(os.path.join(my_path, file_name))
    addAgents = file_path
    new_list = []
    fp = open(addAgents, "r")

    # TODO: add support for cats whenever we get this fetcher working.

    for line in fp:
        if line.startswith("Kitty"):
            new_list.append(-1)
        if line.startswith("SocialWelfare"):
            new_list.append(-2)
    num_vanilla_bots = num_players - num_humans - len(new_list)


    bot_types = [jhg_bot_type for _ in range(num_vanilla_bots)]
    bot_types += new_list



    utility_to_log = []
    popularity_to_log = []

    popSize = 60
    num_gene_pools = 3

    pops = []


    theGenePools = loadPopulationFromFile(popSize, num_gene_pools, tokens_per_player) # this gets us our fetcher

    initial_pops = [100 for _ in range(num_players)]

    plyrs = []
    for i in range(0, num_players):
        plyrs.append(theGenePools[i]) # just add the first guys and go form there

    agents = np.array(plyrs)
    players = [ *agents ]

    alpha_min, alpha_max = 0.20, 0.20
    beta_min, beta_max = 0.5, 1.0
    keep_min, keep_max = 0.95, 0.95
    give_min, give_max = 1.30, 1.30
    steal_min, steal_max = 1.6, 1.60

    num_players = len(players)
    base_pop = 100
    tkns = num_players

    poverty_line = 0

    game_params = {
        "num_players": num_players,
        "alpha": alpha_min,  # np.random.uniform(alpha_min, alpha_max),
        "beta": beta_min,  # np.random.uniform(beta_min, beta_max),
        "keep": keep_min,  # np.random.uniform(keep_min, keep_max),
        "give": give_min,  # np.random.uniform(give_min, give_max),
        "steal": steal_min,  # np.random.uniform(steal_min, steal_max),
        "poverty_line": poverty_line,
        "base_popularity": np.array(initial_pops)
        # "base_popularity": np.array([*[base_pop]*(num_players)])
        # "base_popularity": np.array(random.sample(range(1, 200), num_players))

    }

    forcedRandom = False

    for a in agents:
        a.setGameParams(game_params, forcedRandom)



    bot_types = [0 for _ in range(len(players))]  # they are all cab doesn't REALLY matter here.


    for attempt in tqdm(range(num_attempts)): # create a new sim for each attempt to prevent bleeding over.
    # for attempt in (range(num_attempts)): # create a new sim for each attempt to prevent bleeding over.
        # stuff that we used to od outside that we now have to do inside.
        total_order = create_total_order(num_players, num_humans) # unfortunately we have to make that in here now just bc we are changing the num players
        # round_logger = RoundLogger()
        # game_logger = GameLogger(num_players, bot_types)  # might be the wrong place to ahve this, as I don't actually have the gen number yet.
        # complete_grapher = CompleteGrapher()


        offset = num_rounds * attempt # for logging purposes, lets us know the relationship between the logger round and current round
        current_jhg_engine = create_jhg_sim(num_humans, num_players, total_order, tokens_per_player, jhg_bot_type, addAgents)
        current_sc_sim = create_sim(num_players, scenario, chromosome, group, total_order, allocation_bot_type, utility_per_player)
        current_sc_sim.bot_ovveride(agents) # tells the SC sim to make sure that it is using the same bots as the JHG by passing htem as a reference to both voting and allocation slots.
        # round_logger.reset_up(current_jhg_engine, current_sc_sim)
        # game_logger.resetup(current_jhg_engine, current_sc_sim)

        sc_sim, jhg_engine, pops = run_trial(agents, current_sc_sim, current_jhg_engine, round_list, num_cycles, group, total_order, pops) # This is really whats getting run round times
        utility_to_log.append(sc_sim.results_sums)
        popularity_to_log.append(jhg_engine.get_popularity())

    pops_by_player = np.array(pops).T

    # Compute average popularity per round
    avg_pop_per_round = np.mean(np.array(pops), axis=1)

    # Set up the plot
    fig, ax = plt.subplots(figsize=(12, 6))

    num_players = pops_by_player.shape[0]
    rounds = np.arange(len(pops))

    color_library = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
    bot_types = list(range(num_players))  # just indices 0–9 here

    for i in range(num_players):
        player_scores = pops_by_player[i]
        color = color_library[bot_types[i] % len(color_library)]
        label = f'P{i + 1}'
        ax.plot(rounds, player_scores, label=label, color=color)

    # Plot average line
    ax.plot(rounds, avg_pop_per_round, color='black', linewidth=3, label='Avg')

    # Labeling
    ax.set_title('Average Popularity Over Time', loc="left")
    ax.set_xlabel('Round')
    ax.set_ylabel('Popularity')
    ax.legend()
    ax.grid(True)

    plt.tight_layout()
    plt.show()


        #print("here are the final utilities ", sc_sim.results_sums)
    inverted_results = list(zip(*utility_to_log))
    new_results = []
    for i in range(len(inverted_results)):
        new_sum = sum(inverted_results[i]) / len(inverted_results[i])
        new_results.append(new_sum)




    # num_kitties = 2
    # non_cats = (num_players - num_kitties)
    # cumulative_cat_score = sum(new_results[non_cats:])
    # cumulative_non_cat_score = sum(new_results)- cumulative_cat_score
    # avg_cat_score = cumulative_cat_score / num_kitties
    # avg_non_cat_score = cumulative_non_cat_score / non_cats
    # print('here is the average cat / added agent ', avg_cat_score, " and here is the average non cat utility ", avg_non_cat_score)
    # # print("here is the average Gene3agent score ", avg_non_cat_score)
    # inverted_results.clear()
    #
    #
    # # man this sucks
    # popularity_to_log = np.round(np.array(popularity_to_log).astype(float), 2).tolist()
    #
    # inverted_results = list(zip(*popularity_to_log))
    # new_results = []
    # for i in range(len(inverted_results)):
    #     new_sum = sum(inverted_results[i]) / len(inverted_results[i])
    #     new_results.append(new_sum)
    #
    # non_cats = (num_players - num_kitties)
    # cumulative_cat_score = sum(new_results[non_cats:])
    # cumulative_non_cat_score = sum(new_results)   - cumulative_cat_score
    # avg_cat_score = cumulative_cat_score / num_kitties
    # avg_non_cat_score = cumulative_non_cat_score / non_cats
    # print('here is the average cat / added agent popualrity ', avg_cat_score, " and here is the average non cat popularity ", avg_non_cat_score)
