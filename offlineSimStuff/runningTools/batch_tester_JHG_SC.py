# so this allows me to run the fetcher and create visualizations based off of scenarios and whatnot.
import copy
import random

from Server.social_choice_sim import Social_Choice_Sim
from Server.JHGManager import JHG_simulator
from tqdm import tqdm
import numpy as np
import os



# from offlineSimStuff.variousGraphingTools.sc_tools.causeNodeGraphVisualizer import causeNodeGraphVisualizer
# from offlineSimStuff.variousGraphingTools.sc_tools.graph_influence_matrix import influenceGrapher
from Server.OptionGenerators.generators import generator_factory

# from offlineSimStuff.variousGraphingTools.completeVersions.completeLogger import CompleteLogger
# from offlineSimStuff.variousGraphingTools.completeVersions.completeGrapher import CompleteGrapher

from offlineSimStuff.variousGraphingTools.individualLoggers.roundLogger import RoundLogger
from offlineSimStuff.variousGraphingTools.individualLoggers.gameLogger import GameLogger
from offlineSimStuff.variousGraphingTools.groupStuff.groupLogger import GroupLogger
from offlineSimStuff.variousGraphingTools.completeVersions.completeGrapher import CompleteGrapher
from offlineSimStuff.variousGraphingTools.groupStuff.groupGrapher import GroupGrapher

# import random
#
# seed_value = 42
# random.seed(seed_value)


# starts the sim, could make this take command line arguments
# takes in a bot type, a number of rounds, and then runs it and plots the results. plans for expansion coming soon.
def run_trial(sc_sim: "Social_Choice_Sim", jhg_sim, round_list, num_cycles, group, total_order, round_logger, create_round_graphs_bool, game_logger, create_game_graphs_bool):

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
            influence_matrix = run_jhg_stuff(jhg_sim, curr_round)
            played_jhg = True
            jhg_round = True

        if sc_rounds:
            old_influence_matrix = copy.copy(influence_matrix)
            influence_matrix, winning_vote = run_sc_stuff(sc_sim, jhg_sim, total_order, influence_matrix, curr_round, num_cycles)
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

    return sc_sim, jhg_sim


def run_sc_stuff(sc_sim, jhg_sim, total_order, influence_matrix, curr_round, num_cycles):
    # sc_sim.set_rounds(curr_round) # don't set that here methinks, let it ride.
    possible_peeps, indexes = generate_peeps(total_order, jhg_sim, sc_sim)  # people who are needed to create the matrix
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


def run_jhg_stuff(jhg_sim, curr_round):
    jhg_engine = jhg_sim.sim
    agents = jhg_sim.players
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

    jhg_sim.T = transactions
    new_popularity = jhg_sim.sim.get_popularity()
    avg_pop = sum(new_popularity) / jhg_sim.num_players
    jhg_sim.avg_pop_per_round.append(avg_pop)
    jhg_sim.game_popularities.append(new_popularity)

    # ok so now I have to return
    # the change in popularities,
    # return sc_sim.current_results, sc_sim.results_sums, new_influence  # so we have the change in utility and overall utility

    return jhg_engine.get_influence()  # return da influence matrix, the change in popularitry, and the new popularities.



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


def create_round_graphs(round_logger, curr_round, played_jhg, played_sc):
    complete_grapher = CompleteGrapher()
    complete_grapher.create_round_graphs_with_round_logger(round_logger, curr_round, played_jhg, played_sc)

def create_game_graphs(game_logger):
    complete_grapher = CompleteGrapher()
    complete_grapher.create_game_graphs_with_logger(game_logger)

def create_group_graphs(group_logger):
    group_grapher = GroupGrapher()
    group_grapher.create_graph(group_logger.get_group_data())

# takes in a list of peeps (player or bot or both) and returns their player indexes as per total order
def peeps_to_total_order(peeps, total_order):
    indexes = []
    for peep in peeps:
        indexes.append(total_order.index(peep)+1)
    return indexes


def create_sim(total_players, total_order=None):
    cycle = -1 # a negative cycle indicates to me that this is a test - that, or something is really really wrong.
    curr_round = -1
    num_causes = 3
    generator = generator_factory(2, total_players, 5, 10, -10, 3, None, None)
    enforce_majority = True
    sc_sim = Social_Choice_Sim(total_players, num_causes, num_humans, generator, cycle, curr_round, total_order, enforce_majority)
    return sc_sim


def create_jhg_sim(num_humans, num_players, total_order, tokens_per_player, jhg_bot_type, addAgents):
    jhg_sim = JHG_simulator(num_humans, num_players, total_order, tokens_per_player, jhg_bot_type, agent_config=addAgents)
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



if __name__ == "__main__":

    import random
    import numpy as np

    # SEED = 42  # pick any constant
    #
    # random.seed(SEED)  # Python’s stdlib RNG
    # np.random.seed(SEED)  # NumPy’s RNG

    # jhg_games_per_sc_round = [4,3,3,3,3]  # what we trained the sleepy assasain bots on.
    jhg_games_per_sc_round = ["S", 30]


    round_list = determine_rounds(jhg_games_per_sc_round)
    num_cycles = 3
    num_players = 10


    num_humans = 0
    tokens_per_player = 2
    utility_per_player = 3
    create_round_graphs_bool = False
    create_game_graphs_bool = True
    create_influence = False
    group = ""
    # these paths are relative to the file location, so as long as you don't move the file it can and will run from anywhere.
    jhg_bot_type = 0 # 0 is gene bots, 2 is social welfare and 3 is random. 4 is the new social welfare that I am developing that is just a hair smarter.

    num_attempts = 1 # number of batches to do.
    num_rounds = sum(jhg_games_per_sc_round) if len(jhg_games_per_sc_round) > 2 else jhg_games_per_sc_round[-1] # if its a list, len of list. else, grab the second identifier

    file_name = os.path.join("../..", "Server", "Engine", "scenarios", "workingDirectory")
    my_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.normpath(os.path.join(my_path, file_name))
    addAgents = file_path
    new_list = []
    fp = open(addAgents, "r")
    for line in fp:
        if line.startswith("Kitty"):
            new_list.append(-1)
        if line.startswith("SocialWelfare"):
            new_list.append(-2)
    num_vanilla_bots = num_players - num_humans - len(new_list)
    bot_types = [jhg_bot_type for _ in range(num_vanilla_bots)]
    bot_types += new_list

    # these are legacy but they don't actually get used anywhere and I am too lazy to change it so here we are.
    # scenario = "scenarioIndicator/allRandom"
    chromosome = "chromosomes/highestFromTesting"
    pure_sc_bot_type = "OptimalHuman" # for funsies, means nothing for now.
    # allocation_bot_type = "allocations_scenarios/random"

    utility_to_log = []
    popularity_to_log = []
    peep_constant = 0.5
    agent_name = "PURE SC THING"

    for attempt in tqdm(range(num_attempts)): # create a new sim for each attempt to prevent bleeding over.
    # for attempt in (range(num_attempts)): # create a new sim for each attempt to prevent bleeding over.
        # stuff that we used to od outside that we now have to do inside.
        total_order = create_total_order(num_players, num_humans) # unfortunately we have to make that in here now just bc we are changing the num players
        round_logger = RoundLogger()
        game_logger = GameLogger(num_players, bot_types, peep_constant, agent_name)  # might be the wrong place to ahve this, as I don't actually have the gen number yet.
        complete_grapher = CompleteGrapher()


        offset = num_rounds * attempt # for logging purposes, lets us know the relationship between the logger round and current round
        current_jhg_sim = create_jhg_sim(num_humans, num_players, total_order, tokens_per_player, jhg_bot_type, addAgents)
        current_sc_sim = create_sim(num_players, total_order)
        current_sc_sim.create_bots(chromosome, addAgents)
        # current_sc_sim.bot_ovveride(current_jhg_sim.players) # tells the SC sim to make sure that it is using the same bots as the JHG by passing htem as a reference to both voting and allocation slots.
        round_logger.reset_up(current_jhg_sim, current_sc_sim)
        game_logger.resetup(current_jhg_sim, current_sc_sim)

        sc_sim, jhg_sim = run_trial(current_sc_sim, current_jhg_sim, round_list, num_cycles, group, total_order, round_logger, create_round_graphs_bool, game_logger, create_game_graphs_bool) # This is really whats getting run round times
        utility_to_log.append(sc_sim.results_sums)
        popularity_to_log.append(jhg_sim.get_popularities())



        #print("here are the final utilities ", sc_sim.results_sums)
    inverted_results = list(zip(*utility_to_log))
    new_results = []
    for i in range(len(inverted_results)):
        new_sum = sum(inverted_results[i]) / len(inverted_results[i])
        new_results.append(new_sum)




    num_kitties = 2
    non_cats = (num_players - num_kitties)
    cumulative_cat_score = sum(new_results[non_cats:])
    cumulative_non_cat_score = sum(new_results)- cumulative_cat_score
    avg_cat_score = cumulative_cat_score / num_kitties
    avg_non_cat_score = cumulative_non_cat_score / non_cats
    print('here is the average cat / added agent ', avg_cat_score, " and here is the average non cat utility ", avg_non_cat_score)
    # print("here is the average Gene3agent score ", avg_non_cat_score)
    inverted_results.clear()


    # man this sucks
    popularity_to_log = np.round(np.array(popularity_to_log).astype(float), 2).tolist()

    inverted_results = list(zip(*popularity_to_log))
    new_results = []
    for i in range(len(inverted_results)):
        new_sum = sum(inverted_results[i]) / len(inverted_results[i])
        new_results.append(new_sum)

    non_cats = (num_players - num_kitties)
    cumulative_cat_score = sum(new_results[non_cats:])
    cumulative_non_cat_score = sum(new_results)   - cumulative_cat_score
    avg_cat_score = cumulative_cat_score / num_kitties
    avg_non_cat_score = cumulative_non_cat_score / non_cats
    print('here is the average cat / added agent popualrity ', avg_cat_score, " and here is the average non cat popularity ", avg_non_cat_score)
