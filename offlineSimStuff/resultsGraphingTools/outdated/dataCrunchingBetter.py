# so this allows for larger scale batches to be run and the data to be collected in such a way that I can run statistical analysis on it later.
import copy

from tqdm import tqdm

from offlineSimStuff.variousGraphingTools.individualLoggers.gameLogger import GameLogger
from offlineSimStuff.variousGraphingTools.individualLoggers.roundLogger import RoundLogger
from offlineSimStuff.resultsGraphingTools.resultsSaver import ResultsSaver # logger for long term savings.
from concurrent.futures import ProcessPoolExecutor, as_completed # where the multiprocessing magic happens

from offlineSimStuff.runningTools.runnerHelper import * # get all the functions


# import random
#
# seed_value = 42
# random.seed(seed_value)


# starts the sim, could make this take command line arguments
# takes in a bot type, a number of rounds, and then runs it and plots the results. plans for expansion coming soon.
def run_trial(agents, sc_sim, jhg_sim, round_list, num_cycles, total_order, current_jhg_sim, peep_constant):

    group = "" # get rid fo this at some point, IKD why its till here.
    sc_sim.set_group(group)
    played_sc = False
    played_jhg = False
    curr_sc_round = 0
    influence_matrix = None # this should get overwritten pretty quick, but its there so there's no error.
    for list_index in (range(0, len(round_list))): # fixed, we start at 0 now.

        sc_rounds = round_list[list_index][-1] == "*"
        jhg_rounds = round_list[list_index][-1] == "-"
        curr_round = int(round_list[list_index][:-1]) # useful, yes, but not quite the logger round

        # print("*****************************ROUND ", curr_round, "********************************")

        if jhg_rounds:
            influence_matrix = run_jhg_stuff(jhg_sim, curr_round, agents, len(agents), current_jhg_sim)
            played_jhg = True


        if sc_rounds:
            old_influence_matrix = copy.copy(influence_matrix)
            influence_matrix, winning_vote = run_sc_stuff(sc_sim, jhg_sim.get_popularity(), total_order, influence_matrix, curr_round, num_cycles, peep_constant)
            sc_sim.set_rounds(curr_sc_round) # ???
            curr_sc_round += 1
            played_sc = True


    return sc_sim, jhg_sim, played_sc, played_jhg


def run_attempt(attempt_id, num_players, num_humans, bot_types, peep_constant, agent,
                agents, tokens_per_player, jhg_bot_type, addAgents, enforce_majority, round_list, num_cycles):

    total_order = create_total_order(num_players, num_humans)  # scrambel them as we go for security reasons.
    round_logger = RoundLogger()
    game_logger = GameLogger(num_players, bot_types, peep_constant,
                             agent)  # might be the wrong place to ahve this, as I don't actually have the gen number yet.
    current_jhg_engine = create_jhg_engine(num_players)
    current_jhg_sim = create_jhg_sim(num_humans, num_players, total_order, tokens_per_player, jhg_bot_type, addAgents,
                                     agents, current_jhg_engine)
    current_sc_sim = create_sim(num_players, num_humans, total_order, enforce_majority)
    current_sc_sim.bot_ovveride(agents)
    round_logger.reset_up(current_jhg_sim, current_sc_sim)
    game_logger.resetup(current_jhg_sim, current_sc_sim)

    sc_sim, jhg_engine, sc_played, jhg_played = run_trial(agents, current_sc_sim, current_jhg_engine, round_list,
                                                          num_cycles, total_order, current_jhg_sim, peep_constant)  # This is really whats getting run round times
    if sc_played:
        utility_to_log = sc_sim.results_sums
    else:
        utility_to_log = "NAN"

    if jhg_played:
        popularity_to_log = jhg_engine.get_popularity()
    else:
        popularity_to_log = "NAN"

    result = {
        "Attempt": attempt_id,
        "Utility": utility_to_log,
        "Popularity": popularity_to_log,
    }
    return result


if __name__ == "__main__":
     # gets the the number of logical cores that we possess.
    max_workers = max(1, os.cpu_count()-2) # save a couple of cores for other processes, don't want to overwhelm.

    # this section is just stuff that stays the same from batch to batch. Don't touch it.
    forcedRandom = False
    num_cycles = 3
    num_players = 10
    # lets try a couple fo different peep constants for fun, just to see

    random_agents = True # Human behavior works better with em. # lets try reruning with all agents
    num_humans = 0
    tokens_per_player = 2
    utility_per_player = 3

    # none of these matter anymroe. leave them in for now, but get rid of them as we go.
    chromosomes_directory = "testChromosome"
    group = ""
    # these paths are relative to the file location, so as long as you don't move the file it can and will run from anywhere.
    jhg_bot_type = 0 # 0 is gene bots, 2 is social welfare and 3 is random. ## Social welfare and random are deprecated, don't look at them.
    num_attempts = 1000 # number of batches to do.

                # all consideratiosn about the new cats have been removed. we need to add a self play thing.
    agent_names = ["homoJHGSelfPlay.csv", "mixedJHGSelfPlay.csv"]
    # round_types = [["J", 30], ["S", 30], [4, 3, 3, 3, 3, 3, 3, 3, 3]]
    round_types = [["J", 30], ["S", 30]]
    # round_types = [["J", 3], ["S", 3]]  # small example to make sure everything is getting written appropriately.
    scenarios = ["SelfPlay"] # For now, worry only about self play stuff.
                        # 1 pure pops, 1 pure util, third has a bunch of constants that I want to test.
    # peep_constants_list = [[1], [0], [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]] # not sure the best way to test this
    peep_constants_list = [[1], [0]] # doesn't actually matter yet, still working on support for cross play.
    # ROUND STATE: JHG, SC, COMBINED
    enforce_majorities_list = [[True], [True, False], [True, False]]

    create_round_graphs_bool = False # leftovers from earlier iterations, not important.
    create_game_graphs_bool = False

    # used for adding cats or whatever.
    file_name = os.path.join("../../..", "Server", "Engine", "scenarios", "SelfPlay")
    my_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.normpath(os.path.join(my_path, file_name))
    addAgents = file_path
    new_list = []

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "burned", "results")
    current_results_saver = ResultsSaver(output_dir)


    # good HEAVENS this is nested.
    for agent_index in tqdm(range(len(agent_names))):
        agent = agent_names[agent_index] # so we can use the TQDM
        agents = create_agents(num_players, new_list, agent, forcedRandom, random_agents)

        for round_type in round_types:

            round_list = determine_rounds(round_type)
            num_rounds = sum(round_type) if len(round_type) > 2 else round_type[-1]  # if its a list, len of list. else, grab the second identifier
            round_state = RoundState(round_type)
            index = round_state.return_round_state().index(True) # just find the index where its true and go from there.
            peep_constants = peep_constants_list[index]
            enforce_majorities = enforce_majorities_list[index]

            for scenario in scenarios:

                file_name = os.path.join("../../..", "Server", "Engine", "scenarios", scenario)
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


                for enforce_majority in enforce_majorities:
                    # auto plugged in, no reason to change it at all.

                    for peep_constant in peep_constants:
                    # auto plugged in, no reason to change it at all.
                        results = []

                        with ProcessPoolExecutor(max_workers=max_workers) as executor:
                            futures = []
                            for attempt in range(num_attempts):
                                futures.append(executor.submit(run_attempt, attempt, num_players, num_humans, bot_types, peep_constant, agent,
                                                agents, tokens_per_player, jhg_bot_type, addAgents, enforce_majority, round_list, num_cycles))

                            for future in as_completed(futures):
                                results.append(future.result())

                        # aight we are going to extract the results from the dictionary and put them back in lists like we had them before
                        utility_to_log = np.array([r["Utility"] for r in results if isinstance(r.get("Utility"), (list, np.ndarray))]) # auto filer out the NAN's
                        popularity_to_log = np.array([r["Popularity"] for r in results if isinstance(r.get("Popularity"), (list, np.ndarray))])


                        # get the utilities to log and the popularities to log from the results?
                        num_cats = len(new_list)
                        num_normal = num_players - num_cats  # number of normal humans


                        if isinstance(utility_to_log, np.ndarray) and utility_to_log.size > 0:
                            average_utility = np.sum(utility_to_log, axis=0) / len(utility_to_log)
                            average_utility_non_cats = average_utility[:num_normal].mean() if num_normal > 0 else "NAN"
                            average_utility_cats = average_utility[num_normal:].mean() if num_cats > 0 else "NAN"

                        else:
                            average_utility_cats = "NAN"
                            average_utility_non_cats = "NAN"


                        if isinstance(popularity_to_log, np.ndarray) and popularity_to_log.size > 0:
                            average_popularity = np.sum(popularity_to_log, axis=0) / len(popularity_to_log)
                            average_popularity_non_cats = average_popularity[:num_normal].mean() if num_normal > 0 else "NAN"
                            average_popularity_cats = average_popularity[num_normal:].mean() if num_cats > 0 else "NAN"

                        else:
                            average_popularity_cats = "NAN"
                            average_popularity_non_cats = "NAN"

                        # go ahead and write anyway just
                        current_results_saver.write_result_row(
                            agent=agent,
                            random_agents=random_agents,
                            round_type=round_type,
                            scenario=scenario,
                            peep_constant=peep_constant,
                            enforce_majority=enforce_majority,
                            average_utility_non_cats=average_utility_non_cats,
                            average_utility_cats=average_utility_cats,
                            average_popularity_non_cats=average_popularity_non_cats,
                            average_popularity_cats=average_popularity_cats,
                            utility_to_log=utility_to_log,
                            popularity_to_log=popularity_to_log,

                        )

        current_results_saver.close_file()






