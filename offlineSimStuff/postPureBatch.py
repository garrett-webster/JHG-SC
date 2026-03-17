# this allows for me to run smaller scale test and debug everything there.

from tqdm import tqdm

from offlineSimStuff.runningTools.runnerHelper import * # get all the functions
from offlineSimStuff.variousGraphingTools.individualLoggers.gameLogger import GameLogger
from offlineSimStuff.variousGraphingTools.individualLoggers.roundLogger import RoundLogger


# starts the sim, could make this take command line arguments
# takes in a bot type, a number of rounds, and then runs it and plots the results. plans for expansion coming soon.
def run_trial_graphing(agents, sc_sim: "Social_Choice_Sim", jhg_sim, round_list, num_cycles, group, total_order, pops, round_logger, create_round_graphs_bool, game_logger, create_game_graphs_bool, current_jhg_sim, peep_constant):

    sc_sim.set_group(group)
    played_sc = False
    played_jhg = False
    curr_sc_round = 0
    influence_matrix = None # this should get overwritten pretty quick, but its there so there's no error.
    for list_index in (range(0, len(round_list))): # fixed, we start at 0 now.

        sc_rounds = round_list[list_index][-1] == "*"
        jhg_rounds = round_list[list_index][-1] == "-"
        curr_round = int(round_list[list_index][:-1]) # useful, yes, but not quite the logger round
        # print("this si the curr round ", curr_round)

        # print("*****************************ROUND ", curr_round, "********************************")

        if jhg_rounds:
            influence_matrix = run_jhg_stuff(jhg_sim, curr_round, agents, len(agents), current_jhg_sim)
            played_jhg = True
            pops.append(jhg_sim.get_popularity())
            print("influence for round ", curr_round, " is \n", influence_matrix)



        if sc_rounds:
            influence_matrix, winning_vote = run_sc_stuff(sc_sim, jhg_sim.get_popularity(), total_order, influence_matrix, curr_round, num_cycles, peep_constant)
            sc_sim.set_rounds(curr_sc_round) # ???
            curr_sc_round += 1
            played_sc = True
            jhg_sim.set_new_influence(influence_matrix) # overrides the current influence matrix wiht the new one. The ONLY real way that we can have backwash.

        round_logger.save_round(curr_round, sc_rounds, jhg_rounds)


        if create_round_graphs_bool:
            create_round_graphs(round_logger, curr_round, sc_rounds, jhg_rounds)

    if create_game_graphs_bool:
        game_logger.save_game(played_sc, played_jhg)
        create_game_graphs(game_logger)

    return sc_sim, jhg_sim, pops

if __name__ == "__main__":

    import random
    # import numpy as np
    #
    SEED = 42  # pick any constant

    random.seed(SEED)  # Python’s stdlib RNG
    np.random.seed(SEED)  # NumPy’s RNG

    # various batch scenarios I keep on hand for reference.
    jhg_games_per_sc_round = [4, 3, 3, 3]
    # jhg_games_per_sc_round = ["J", 30]
    # jhg_games_per_sc_round = ["S", 30]
    forcedRandom = True # TRUE uses the list, so thats cool.
    enforce_majority = True # what we used in the other fetcher.
    random_agents = False # this is what we typically do.

    round_list = determine_rounds(jhg_games_per_sc_round)
    num_cycles = 3
    num_players = 10
    peep_constant = 0 # relates to the balance of which we us


    num_humans = 0
    tokens_per_player = 2
    utility_per_player = 3
    create_round_graphs_bool = True
    create_game_graphs_bool = True
    create_influence = True
    chromosomes_directory = "testChromosome"
    group = ""
    # cat_scenario = "2OldKitties"
    cat_scenario = "SelfPlay"
    # cat_scenario = "2SCKitties"
    # these paths are relative to the file location, so as long as you don't move the file it can and will run from anywhere.
    jhg_bot_type = 0 # 0 is gene bots, 2 is social welfare and 3 is random. 4 is the new social welfare that I am developing that is just a hair smarter.

    num_attempts = 3 # number of batches to do.
    num_rounds = sum(jhg_games_per_sc_round) if len(jhg_games_per_sc_round) > 2 else jhg_games_per_sc_round[-1] # if its a list, len of list. else, grab the second identifier

    file_name = os.path.join("..", "Server", "Engine", "scenarios", cat_scenario)
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
        if line.startswith("SCKitty"):
            new_list.append(-3)
        if line.startswith("SocialWelfare"):
            new_list.append(-4)
    num_vanilla_bots = num_players - num_humans - len(new_list)


    bot_types = [jhg_bot_type for _ in range(num_vanilla_bots)]
    bot_types += new_list

    # for individual testing
    # file_name = os.path.join(file_name, "gen_199.csv") # JHG cab agents as used in the study
    # file_name = os.path.join(file_name, "homogenousCatKillers.csv")
    # file_name = os.path.join(file_name, "heterogenousCatKillers.csv")
    # file_name = os.path.join(file_name, "homoNewCats.csv")
    # agent_name = "mixedJHGSelfPlay.csv"
    # agent_name = "homoSCSelfPlay.csv"
    agent_name = "6x6Round1.csv" # use this as sort of the default, for now.

    # bunch of stuff for print statements
    utility_to_log = []
    popularity_to_log = []
    pops = []


    # bot_types = [0 for _ in range(len(agents))]  # they are all cab doesn't REALLY matter here.

    # I want every bot type, in every scenario, with every type of cat, and on their own
    # which means we actually need to use the different scenarios.
    # don't worry about 1 vs 2 cats IG.

    agents = create_agents(num_players, new_list, agent_name, forcedRandom, random_agents)
    # agents = create_sc_agents(num_players, agent_name)

    for attempt in tqdm(range(num_attempts)): # create a new sim for each attempt to prevent bleeding over.
    # for attempt in (range(num_attempts)): # create a new sim for each attempt to prevent bleeding over.
        # stuff that we used to od outside that we now have to do inside.
        total_order = create_total_order(num_players, num_humans) # unfortunately we have to make that in here now just bc we are changing the num players
        round_logger = RoundLogger()
        game_logger = GameLogger(num_players, bot_types, peep_constant, agent_name)  # might be the wrong place to ahve this, as I don't actually have the gen number yet.
        complete_grapher = CompleteGrapher()


        offset = num_rounds * attempt # for logging purposes, lets us know the relationship between the logger round and current round
        current_jhg_engine = create_jhg_engine(num_players)
        current_jhg_sim = create_jhg_sim(num_humans, num_players, total_order, jhg_bot_type, addAgents, agents, current_jhg_engine)
        current_sc_sim = create_sim(num_players, num_humans, total_order, enforce_majority)
        current_sc_sim.bot_ovveride(agents, len(new_list)) # tells the SC sim to make sure that it is using the same bots as the JHG by passing htem as a reference to both voting and allocation slots.
        round_logger.reset_up(current_jhg_sim, current_sc_sim)
        game_logger.resetup(current_jhg_sim, current_sc_sim)

        sc_sim, jhg_engine, pops = run_trial_graphing(agents, current_sc_sim, current_jhg_engine, round_list, num_cycles, group, total_order, pops, round_logger, create_round_graphs_bool, game_logger, create_game_graphs_bool, current_jhg_sim, peep_constant) # This is really whats getting run round times
        utility_to_log.append(sc_sim.results_sums)
        popularity_to_log.append(jhg_engine.get_popularity())

    pops_by_player = np.array(pops).T





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
