# so this allows for larger scale batches to be run and the data to be collected in such a way that I can run statistical analysis on it later.
import copy

from tqdm import tqdm

from offlineSimStuff.variousGraphingTools.individualLoggers.gameLogger import GameLogger
from offlineSimStuff.variousGraphingTools.individualLoggers.roundLogger import RoundLogger
from concurrent.futures import ProcessPoolExecutor, as_completed  # where the multiprocessing magic happens

from offlineSimStuff.runningTools.runnerHelper import *  # get all the functions

from offlineSimStuff.resultsGraphingTools.individualResultsSaver import IndividualResultsSaver


# import random
#
# seed_value = 42
# random.seed(seed_value)

def run_attempt(attempt_id, num_players, num_humans, bot_types, peep_constant, agent,
                agents, jhg_bot_type, addAgents, enforce_majority, round_list, num_cycles):

    try:
        total_order = create_total_order(num_players, num_humans)  # scrambel them as we go for security reasons.
        round_logger = RoundLogger()
        game_logger = GameLogger(num_players, bot_types, peep_constant,
                                 agent)  # might be the wrong place to ahve this, as I don't actually have the gen number yet.
        current_jhg_engine = create_jhg_engine(num_players)
        current_jhg_sim = create_jhg_sim(num_humans, num_players, total_order, jhg_bot_type, addAgents,
                                         agents, current_jhg_engine)
        current_sc_sim = create_sim(num_players, num_humans, total_order, enforce_majority)
        current_sc_sim.bot_ovveride(agents)
        round_logger.reset_up(current_jhg_sim, current_sc_sim)
        game_logger.resetup(current_jhg_sim, current_sc_sim)
        current_sc_sim.cooperation_score = 0 #just set it all the way down.

        # use run trial from the runner helper to make sure its all in the same place.
        sc_sim, jhg_engine, sc_played, jhg_played = run_trial(agents, current_sc_sim, current_jhg_engine, round_list,
                                                              num_cycles, total_order, current_jhg_sim,
                                                              peep_constant)  # This is really whats getting run round times
        if sc_played:
            utility_to_log = sc_sim.results_sums
            cooperation_score = sc_sim.get_cooperation_score() # go aheand and slap that in
            # print('this is the cooperation score ', cooperation_score)
        else:
            utility_to_log = "NAN"
            cooperation_score = "NAN"

        if jhg_played:
            popularity_to_log = jhg_engine.get_popularity()
        else:
            popularity_to_log = "NAN"

        result = {
            "Attempt": attempt_id,
            "Utility": utility_to_log,
            "Popularity": popularity_to_log,
            "Cooperation_Score": cooperation_score,
        }
        return result
    # try and catch the bugger
    except Exception as e:
        print("exception ", e)
        self.outputQueue.put(e)

def create_file_name(agent_name, round_type, scenario, enforce_majority, peep_constant):
    file_name = str(agent_name) + "_" + str(round_type) + "_" + str(scenario) + "_" + str(enforce_majority) + "_" + str(peep_constant)
    return file_name


def run_data_crunching_simulations(max_workers, forcedRandom, num_players, random_agents, num_humans,
                  jhg_bot_type, num_attempts, agent_names,
                  round_types, scenarios, peep_constants_list, enforce_majorities_list, new_list):

    # do be a dear and leave this here. output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "burned", "results")
    num_cycles = 3 # we don't have a good reason to change this, so I guess its just here.

    # good HEAVENS this is nested.
    for agent_index in tqdm(range(len(agent_names))):
        agent = agent_names[agent_index]  # so we can use the TQDM
        # print("this is the agent ", agent)
        agents = create_agents(num_players, new_list, agent, forcedRandom, random_agents)
        # print("this is the agent we are dealing with ", agent)
        # agent = "OptimalHuman"
        # agents = create_sc_agents(num_players, agent)

        for i, round_type in enumerate(round_types):
            # if we are trying to deal with 3 or more round types, use this. only works with the 3 round types tho.
            # # round_list = determine_rounds(round_type)
            # # num_rounds = sum(round_type) if len(round_type) > 2 else round_type[
            # #     -1]  # if its a list, len of list. else, grab the second identifier
            # # round_state = RoundState(round_type)
            # # index = round_state.return_round_state().index(
            # #     True)  # just find the index where its true and go from there.
            # # peep_constants = peep_constants_list[index]
            # # enforce_majorities = enforce_majorities_list[index]

            round_list = determine_rounds(round_type)
            peep_constants = peep_constants_list[i]
            enforce_majorities = enforce_majorities_list[i]

            for scenario in scenarios:
                print("testing scenario ", scenario)

                file_name = os.path.join("../..", "Server", "Engine", "scenarios", scenario)
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
                    print("Trying a different majoritiy ", enforce_majority)
                    # print("this is the round_type ", round_type, " and this is the ef ", enforce_majority)
                    # auto plugged in, no reason to change it at all.

                    for peep_constant in peep_constants:
                        # auto plugged in, no reason to change it at all.
                        results = []

                        file_name = create_file_name(agent, round_type, scenario, enforce_majority, peep_constant)
                        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "burned", "Results4")
                        current_results_saver = IndividualResultsSaver(output_dir, file_name)

                        with ProcessPoolExecutor(max_workers=max_workers) as executor:
                            futures = []
                            for attempt in range(num_attempts):
                                futures.append(executor.submit(run_attempt, attempt, num_players, num_humans, bot_types,
                                                               peep_constant, agent,
                                                               agents, jhg_bot_type, addAgents,
                                                               enforce_majority, round_list, num_cycles))

                            for future in as_completed(futures):
                                results.append(future.result())

                        # aight we are going to extract the results from the dictionary and put them back in lists like we had them before
                        utility_to_log = np.array([r["Utility"] for r in results if isinstance(r.get("Utility"), (
                            list, np.ndarray))])  # auto filer out the NAN's
                        popularity_to_log = np.array(
                            [r["Popularity"] for r in results if isinstance(r.get("Popularity"), (list, np.ndarray))])
                        # coop_to_log = np.array(r["Cooperation_Score"] for r in results if isinstance(r.get("Cooperation_Score"), (list, float)))
                        coop_to_log = np.array([r["Cooperation_Score"] for r in results if isinstance(r.get("Cooperation_Score"), (list, float))])

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
                            average_popularity_non_cats = average_popularity[
                                                          :num_normal].mean() if num_normal > 0 else "NAN"
                            average_popularity_cats = average_popularity[num_normal:].mean() if num_cats > 0 else "NAN"

                        else:
                            average_popularity_cats = "NAN"
                            average_popularity_non_cats = "NAN"

                        if isinstance(coop_to_log, np.ndarray) and coop_to_log.size > 0:
                            average_coop_score = sum(coop_to_log) / len(coop_to_log) # this should do the trick???
                        else:
                            average_coop_score = np.array(["NA"])


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
                            coop_to_log=average_coop_score,

                        )

                        current_results_saver.close_file()


if __name__ == "__main__":
    # gets the the number of logical cores that we possess.
    max_workers = max(1, os.cpu_count() - 2)  # save a couple of cores for other processes, don't want to overwhelm.

    # this section is just stuff that stays the same from batch to batch. Don't touch it.
    forcedRandom = False
    num_players = 10
    # lets try a couple fo different peep constants for fun, just to see

    random_agents = True  # Human behavior works better with em. # lets try reruning with all agents
    num_humans = 0
    num_cats = 0

    # these paths are relative to the file location, so as long as you don't move the file it can and will run from anywhere.
    jhg_bot_type = 0  # 0 is gene bots, 2 is social welfare and 3 is random. ## Social welfare and random are deprecated, don't look at them.
    num_attempts = 1000  # number of batches to do.

    # all consideratiosn about the new cats have been removed. we need to add a self play thing.
    agent_names = ["homoJHGSelfPlay.csv", "mixedJHGSelfPlay.csv"]
    # round_types = [["J", 30], ["S", 30], [4, 3, 3, 3, 3, 3, 3, 3, 3]]
    round_types = [["J", 30], ["S", 30]] # no mixing.
    # round_types = [["J", 3], ["S", 3]]  # small example to make sure everything is getting written appropriately.
    scenarios = ["SelfPlay"]  # For now, worry only about self play stuff.
    # 1 pure pops, 1 pure util, third has a bunch of constants that I want to test.
    # peep_constants_list = [[1], [0], [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]] # not sure the best way to test this
    peep_constants_list = [[1], [0]]  # doesn't actually matter yet, still working on support for cross play.
    # ROUND STATE: JHG, SC, COMBINED
    enforce_majorities_list = [[True], [True, False], [True, False]]

    new_list = [ImprovedJakeCat() for _ in range(num_cats)] # kind of?

    # ok there has GOT to be a better way to run this stuff.
    run_data_crunching_simulations(max_workers, forcedRandom, num_players, random_agents, num_humans,
                  jhg_bot_type, num_attempts, agent_names,
                  round_types, scenarios, peep_constants_list, enforce_majorities_list, new_list)




