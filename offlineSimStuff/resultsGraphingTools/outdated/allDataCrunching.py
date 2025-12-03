# so this allows me to run the fetcher and create visualizations based off of scenarios and whatnot.
import copy

from numpy import ndarray

from Server.social_choice_sim import Social_Choice_Sim
from Server.JHGManager import JHG_simulator
from Server.Engine.simulator import GameSimulator

from tqdm import tqdm
import numpy as np
import os

from Server.OptionGenerators.generators import generator_factory

from Server.Engine.completeBots.geneagent3 import GeneAgent3
# from Server.Engine.completeBots.basicGeneAgent3 import BasicGeneAgent3

from offlineSimStuff.variousGraphingTools.individualLoggers.roundLogger import RoundLogger
from offlineSimStuff.variousGraphingTools.individualLoggers.gameLogger import GameLogger
from offlineSimStuff.variousGraphingTools.completeVersions.completeGrapher import CompleteGrapher
from Server.Engine.completeBots.projectCat import ProjectCat
from Server.Engine.completeBots.improvedJakeCate import ImprovedJakeCat

from offlineSimStuff.resultsGraphingTools.resultsSaver import ResultsSaver # logger for long term savings.

# import random
#
# seed_value = 42
# random.seed(seed_value)


# starts the sim, could make this take command line arguments
# takes in a bot type, a number of rounds, and then runs it and plots the results. plans for expansion coming soon.
def run_trial(agents, sc_sim: "Social_Choice_Sim", jhg_sim, round_list, num_cycles, group, total_order, pops, round_logger, create_round_graphs_bool, game_logger, create_game_graphs_bool, current_jhg_sim, peep_constant):

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
            influence_matrix = run_jhg_stuff(jhg_sim, curr_round, agents, len(agents), current_jhg_sim)
            played_jhg = True
            jhg_round = True
            pops.append(jhg_sim.get_popularity())

        if sc_rounds:
            old_influence_matrix = copy.copy(influence_matrix)
            influence_matrix, winning_vote = run_sc_stuff(sc_sim, jhg_sim, total_order, influence_matrix, curr_round, num_cycles, peep_constant)
            sc_sim.set_rounds(curr_sc_round) # ???
            curr_sc_round += 1
            played_sc = True
            sc_round = True


        round_logger.save_round(curr_round, sc_rounds, jhg_rounds)


        if create_round_graphs_bool:
            create_round_graphs(round_logger, curr_round, sc_rounds, jhg_rounds)

    if create_game_graphs_bool:
        game_logger.save_game(played_sc, played_jhg)
        create_game_graphs(game_logger)

    return sc_sim, jhg_sim, pops, played_sc, played_jhg


def run_sc_stuff(sc_sim, jhg_sim, total_order, influence_matrix, curr_round, num_cycles, peep_constant):
    # sc_sim.set_rounds(curr_round) # don't set that here methinks, let it ride.
    possible_peeps, indexes = generate_peeps(total_order, jhg_sim, sc_sim, peep_constant)  # people who are needed to create the matrix
    if influence_matrix is not None:
        new_influence = influence_matrix
    else:
        new_influence = sc_sim.get_influence_matrix() # if there is no JHG influence, we are flying solo, leach off of own influence
    # should I make this, you know, an entirely different bot? having them in the same file feels wrong beuase they are doing differen things.
    current_options_matrix, peeps = sc_sim.let_others_create_options_matrix(possible_peeps.tolist(), curr_round, new_influence)  # actually creates the matrix
    # print("these are the peeps" , peeps)
    sc_sim.start_round((current_options_matrix, indexes))

    bot_votes = {}
    for cycle in range(num_cycles):
        bot_votes[cycle] = sc_sim.get_votes(bot_votes, curr_round, cycle, num_cycles, influence_matrix)
        sc_sim.record_votes(bot_votes[cycle], cycle)

    # make sure that this happens IMMEDIATELY afterward.
    winning_vote, round_results = sc_sim.return_win(bot_votes[num_cycles - 1])
    new_influence = np.array(sc_sim.get_influence_matrix()) # ACTUALLY UPDATE THE FETCHER
    sc_sim.save_results()
    return new_influence, winning_vote # takes our modified influence and makes sure to feed it back into the jhg sim so we get a cyclical affect.


def reconcile_influence(jhg_influence, sc_influence):
    # ok this fetcher uses convex recombination to put the two together and then uses the frobenius norm to decide on the magnitude to adjust back too. bars!
    # alpha = 0.5 # THIS iS JUST A STARTER VALUE, WILL LIKELY BE MADE INTO A GENE OR WHATEVER.
    alpha = 0.5 # THIS iS JUST A STARTER VALUE, WILL LIKELY BE MADE INTO A GENE OR WHATEVER.
    # Alpha of 0 is entirely JHG, alpha of 1 is entirely SC. I started with 0.5 but worry that that might have been too flattening.

    if sc_influence is None:
        print("something wrong :(")
        return jhg_influence

    sc_influence = np.array(sc_influence)
    jhg_influence = np.array(jhg_influence) # This shbould never get used but it couldn't hurt

    jhg_norm = np.linalg.norm(jhg_influence, 'fro')

    combined = (1 - alpha) * jhg_influence + alpha * sc_influence

    combined_norm = np.linalg.norm(combined, 'fro')
    if combined_norm == 0:
        return np.zeros_like(jhg_influence)

    rescaled = combined * (jhg_norm / combined_norm)
    return rescaled


def run_jhg_stuff(jhg_engine, curr_round, agents, num_players, current_jhg_sim):
    transactions = [0 for _ in range(num_players)]  # so this is how I replilcate it in python.
    T_prev = jhg_engine.get_transaction()

    for i in range(num_players):

        transactions[i] = agents[i].play_round(
            i,
            curr_round,
            T_prev[:,i],
            jhg_engine.get_popularity().tolist(),
            jhg_engine.get_influence(),
            jhg_engine.get_extra_data(i),
            # False
        )
    jhg_engine.play_round(transactions)  # thanks references


    current_jhg_sim.T = transactions
    new_popularity = current_jhg_sim.sim.get_popularity()
    avg_pop = sum(new_popularity) / current_jhg_sim.num_players
    current_jhg_sim.avg_pop_per_round.append(avg_pop)
    current_jhg_sim.game_popularities.append(new_popularity)

    # ok so now I have to return
    # the change in popularities,
    # return sc_sim.current_results, sc_sim.results_sums, new_influence  # so we have the change in utility and overall utility

    return jhg_engine.get_influence()  # return da influence matrix, the change in popularitry, and the new popularities.


def generate_peeps(total_order, jhg_sim, sc_sim, peep_constant):
    popularity_array = (jhg_sim.get_popularity()) # huh
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
    overall_probability_array = []
    alpha = peep_constant
    for pop, util in zip(normalized_popularity_array, normalized_utility_array):
        new_val = alpha * pop + (1 - alpha) * util
        overall_probability_array.append(new_val)

    overall_probability_array = [(p + u) / 2 for p, u in zip(normalized_popularity_array, normalized_utility_array)]
    probabilities = np.array(overall_probability_array)
    new_world_order = np.array(total_order)
    # shoudl pull without replacement from total order using the overall probability array, gives 3 choies without replacement.
    try:
        new_peeps = np.random.choice(new_world_order, p=probabilities, size=3, replace=False)
        indexes = peeps_to_total_order(new_peeps, total_order)
        return new_peeps, indexes
    except ValueError:
        print("Here the pops, stop here ")
        return 0, 0


def create_round_graphs(round_logger, curr_round, played_jhg, played_sc):
    complete_grapher = CompleteGrapher()
    complete_grapher.create_round_graphs_with_round_logger(round_logger, curr_round, played_jhg, played_sc)

def create_game_graphs(game_logger):
    complete_grapher = CompleteGrapher()
    complete_grapher.create_game_graphs_with_logger(game_logger)

def create_group_graphs(group_logger):
    pass
    # group_grapher = GroupGrapher()
    # group_grapher.create_graph(group_logger.get_group_data())

# takes in a list of peeps (player or bot or both) and returns their player indexes as per total order
def peeps_to_total_order(peeps, total_order):
    indexes = []
    for peep in peeps:
        indexes.append(total_order.index(peep)+1)
    return indexes


def create_sim(total_players, total_order=None, enforce_majority=False):
    cycle = -1 # a negative cycle indicates to me that this is a test - that, or something is really really wrong.
    curr_round = -1
    num_causes = 3
    generator = generator_factory(2, total_players, 5, 10, -10, 3, None, None)
    sc_sim = Social_Choice_Sim(total_players, num_causes, num_humans, generator, cycle, curr_round, total_order, enforce_majority)
    return sc_sim

def create_jhg_sim(num_humans, num_players, total_order, tokens_per_player, jhg_bot_type, addAgents, new_agents, new_engine):
    jhg_sim = JHG_simulator(num_humans, num_players, total_order, tokens_per_player, jhg_bot_type, agent_config=addAgents)
    jhg_sim.override_everything(new_engine, new_agents)
    return jhg_sim

def create_jhg_engine(num_humans, num_players, total_order, tokens_per_player, jhg_bot_type, addAgents):
    poverty_line = 0
    forcedRandom = False # lets try this for fun
    alpha = 0.2  # double check these magical fetchers when you get the chance actually.
    beta = 0.5
    give = 1.3
    keep = 0.95
    steal = 1.6
    base_pop = 100

    alpha_min, alpha_max = 0.20, 0.20
    beta_min, beta_max = 0.5, 1.0
    keep_min, keep_max = 0.95, 0.95
    give_min, give_max = 1.30, 1.30
    steal_min, steal_max = 1.6, 1.60

    initial_pops = [100 for _ in range(num_players)]

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

def loadPopulationFromFile(popSize, num_gene_pools, agent_name):
    fnombre = "Kill me"
    try:
        file_name = os.path.join("Server", "Engine", "botGenerations") # creates standard file path. we then append to this.
        file_name = os.path.join(file_name, agent_name)

        my_path = os.path.dirname(os.path.abspath(__file__))
        my_path = os.path.abspath(os.path.join(my_path, "../"))  # go up 2 levels and resolve path
        file_path = os.path.join(my_path, file_name)
        fnombre = file_path

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

        thePopulation.append(GeneAgent3(words[0], num_gene_pools))
        # thePopulation.append(BasicGeneAgent3(words[0], num_gene_pools))
        thePopulation[i].count = float(words[1])
        # thePopulation[i].relativeFitness = float(words[2])
        # thePopulation[i].absoluteFitness = float(words[3][0])

    fp.close()

    return thePopulation


def create_agents(num_players, new_list, agent_name):
    popSize = 100
    num_gene_pools = 1
    tokens_per_player = 2

    theGenePools = loadPopulationFromFile(popSize, num_gene_pools, agent_name)  # this gets us our fetcher

    initial_pops = [100 for _ in range(num_players)]

    plyrs = []
    for i in range(0, num_players-len(new_list)):
        plyrs.append(theGenePools[i])  # just add the first guys and go form there

    for i in new_list:
        if i == -1:
            plyrs.append(ImprovedJakeCat())
        if i == -2:
            plyrs.append(ProjectCat())


    agents = np.array(plyrs)
    players = [*agents]

    alpha_min, alpha_max = 0.20, 0.20
    beta_min, beta_max = 0.5, 1.0
    keep_min, keep_max = 0.95, 0.95
    give_min, give_max = 1.30, 1.30
    steal_min, steal_max = 1.6, 1.60

    num_players = len(players)

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

    }

    forcedRandom = True

    for a in agents:
        a.setGameParams(game_params, forcedRandom)

    return agents


if __name__ == "__main__":

    # this section is just stuff that stays the same from batch to batch. Don't touch it.
    ForcedRandom = False
    num_cycles = 3
    num_players = 10
    peep_constant = 0.5 # relates to the balance of which we us
    # lets try a couple fo different peep constants for fun, just to see


    num_humans = 0
    tokens_per_player = 2
    utility_per_player = 3

    # none of these matter anymroe. leave them in for now, but get rid of them as we go.
    chromosomes_directory = "testChromosome"
    group = ""
    # these paths are relative to the file location, so as long as you don't move the file it can and will run from anywhere.
    jhg_bot_type = 0 # 0 is gene bots, 2 is social welfare and 3 is random. ## Social welfare and random are deprecated, don't look at them.
    num_attempts = 20 # number of batches to do.

                # all consideratiosn about the new cats have been removed. we need to add a self play thing.
    agent_names = ["heterogenousCatKillers.csv", "homogenousCatKillers.csv"]
    # round_types = [["S", 30], ["J", 30], [4, 3, 3, 3, 3, 3, 3, 3, 3]]
    round_types = [["S", 30]]#, # ["J", 30], [4, 3, 3, 3, 3, 3, 3, 3, 3]]
    scenarios = ["2OldKitties", "SelfPlay"] # exactly what it says on the tin.
    # round_list = determine_rounds(jhg_games_per_sc_round) ## format for later
    peep_constants = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0] # not sure the best way to test this
    enforce_majorities = [True, False]

    # use this in a second.
    # num_rounds = sum(jhg_games_per_sc_round) if len(jhg_games_per_sc_round) > 2 else jhg_games_per_sc_round[-1]  # if its a list, len of list. else, grab the second identifier
    # bunch of stuff for print statements

    # this is what we want to iterate and print between batches, write it somewhere.
    pops = []

    create_round_graphs_bool = False
    create_game_graphs_bool = False

    # used for adding cats or whatever.
    file_name = os.path.join("../../..", "Server", "Engine", "scenarios", "workingDirectory")
    my_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.normpath(os.path.join(my_path, file_name))
    addAgents = file_path
    new_list = []
    fp = open(addAgents, "r")

    for line in fp:
        if line.startswith("OldKitty"):
            new_list.append(-1)
        if line.startswith("NewKitty"):
            new_list.append(-2)
    num_vanilla_bots = num_players - num_humans - len(new_list)
    bot_types = [jhg_bot_type for _ in range(num_vanilla_bots)]
    bot_types += new_list

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "burned", "results")
    current_results_saver = ResultsSaver(output_dir)


    # good HEAVENS this is nested.
    for agent_index in tqdm(range(len(agent_names))):
        agent = agent_names[agent_index] # so we can use the TQDM
        agents = create_agents(num_players, new_list, agent)


        for round_type in round_types:

            round_list = determine_rounds(round_type)
            num_rounds = sum(round_type) if len(round_type) > 2 else round_type[-1]  # if its a list, len of list. else, grab the second identifier

            for scenario in scenarios:

                file_name = os.path.join("../../..", "Server", "Engine", "scenarios", "workingDirectory")
                my_path = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.normpath(os.path.join(my_path, file_name))
                addAgents = file_path
                new_list = []
                fp = open(addAgents, "r")

                for line in fp:
                    if line.startswith("OldKitty"):
                        new_list.append(-1)
                    if line.startswith("NewKitty"):
                        new_list.append(-2)
                    if line.startswith("SocialWelfare"):
                        new_list.append(-3)
                num_vanilla_bots = num_players - num_humans - len(new_list)

                bot_types = [jhg_bot_type for _ in range(num_vanilla_bots)]
                bot_types += new_list


                for peep_constant in peep_constants:
                    # auto plugged in, no reason to change it at all.

                    for enforce_majority in enforce_majorities:
                        # auto plugged in, no reason to change it at all.
                        utility_to_log = []
                        popularity_to_log = []

                        for attempt in range(num_attempts):

                            # create_game_graphs_bool = True if attempt == num_attempts-1 else False # print just the last game

                            total_order = create_total_order(num_players, num_humans)  # scrambel them as we go for security reasons.
                            round_logger = RoundLogger()
                            game_logger = GameLogger(num_players, bot_types, peep_constant, agent)  # might be the wrong place to ahve this, as I don't actually have the gen number yet.
                            complete_grapher = CompleteGrapher()
                            current_jhg_engine = create_jhg_engine(num_humans, num_players, total_order, tokens_per_player, jhg_bot_type, addAgents)
                            current_jhg_sim = create_jhg_sim(num_humans, num_players, total_order, tokens_per_player, jhg_bot_type, addAgents, agents, current_jhg_engine)
                            current_sc_sim = create_sim(num_players, total_order, enforce_majority)
                            current_sc_sim.bot_ovveride(agents)
                            round_logger.reset_up(current_jhg_sim, current_sc_sim)
                            game_logger.resetup(current_jhg_sim, current_sc_sim)

                            sc_sim, jhg_engine, pops, sc_played, jhg_played = run_trial(agents, current_sc_sim, current_jhg_engine, round_list,
                                                                 num_cycles, group, total_order, pops, round_logger,
                                                                 create_round_graphs_bool, game_logger,
                                                                 create_game_graphs_bool, current_jhg_sim,
                                                                 peep_constant)  # This is really whats getting run round times
                            if sc_played:
                                utility_to_log.append(sc_sim.results_sums)
                            else:
                                utility_to_log = "NAN"

                            if jhg_played:
                                popularity_to_log.append(jhg_engine.get_popularity())
                            else:
                                popularity_to_log = "NAN"


                        num_cats = len(new_list)
                        num_normal = num_players - num_cats  # number of normal humans

                        # ok so now I need to report on the actual amount of utility and popularity there were.
                        utility_to_log = np.array(utility_to_log) if isinstance(utility_to_log, list) else "NAN"
                        popularity_to_log = np.array(popularity_to_log) if isinstance(popularity_to_log, list) else "NAN"

                        if isinstance(utility_to_log, ndarray):
                            average_utility = np.sum(utility_to_log, axis=0) / len(utility_to_log)
                            average_utility_non_cats = average_utility[:num_normal]
                            average_utility_non_cats = average_utility[:num_normal].mean() if num_normal > 0 else "NAN"
                            average_utility_cats = average_utility[num_normal:].mean() if num_cats > 0 else "NAN"



                        if isinstance(popularity_to_log, ndarray):
                            average_popularity = np.sum(popularity_to_log, axis=0) / len(popularity_to_log)
                            average_popularity_non_cats = average_popularity[:num_normal]
                            average_popularity_non_cats = average_popularity[:num_normal].mean() if num_normal > 0 else "NAN"
                            average_popularity_cats = average_popularity[num_normal:].mean() if num_cats > 0 else "NAN"



                        else:
                            average_popularity_cats = "NAN"
                            average_popularity_non_cats = "NAN"

                        ## TODO: NOT GENERATING SCALARS! FIX THAT TOMORROW!



                        # print(agent, " ", round_type, " ", scenario, " ", peep_constant, ", ", enforce_majority)
                        # print("Results: ")
                        # print("Average utility of non cats ", average_utility_non_cats)
                        # print("Average utility of cats ", average_utility_cats)
                        # print("Average popularity of non cats ", average_popularity_non_cats)
                        # print("Average utility of cats ", average_utility_cats)

                        # current_results_saver.write_result_row(
                        #     agent,
                        #     round_type,
                        #     scenario,
                        #     peep_constant,
                        #     enforce_majority,
                        #     average_utility_non_cats,
                        #     average_utility_cats,
                        #     average_popularity_non_cats,
                        #     average_popularity_cats
                        # )

    current_results_saver.close_file()





