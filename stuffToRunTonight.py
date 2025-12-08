# what do I need to run tonight
# genetic algorihtms.
from offlineSimStuff.geneticStuff.pureSC.homo.mutliHomoFlutterSC import evolve_homogenous_SC
from offlineSimStuff.geneticStuff.pureSC.mixed.mutliMixedFlutterSC import evolve_mixed_SC
from Server.Engine.completeBots.improvedJakeCate import ImprovedJakeCat # not that we ever actually use him
        # but if we want to run cats in the future could be useful.
import os
from offlineSimStuff.resultsGraphingTools.dataCrunchingBetterSeparated import run_data_crunching_simulations
from offlineSimStuff.runningTools.runnerHelper import get_file_names

import shutil


def run_genetic_stuff():
    popSize = 100
    numGeneCopies = 1
    startIndex = 0
    numGens = 200
    gamesPerGen = popSize # for HOMO, needs same number. better practice to just always set.
    agentsPerGame = 10 # should be 10 agents.
    roundsPerGame = 30
    numCats = 0
    povertyLine = 0
    # folder = ""
    extraAgents = [ImprovedJakeCat() for _ in range(numCats)]

    scenarios = ["homo", "mixed"] # different training scenarios
    majority_possibilities = [True, False] # differing types of enforce majority we could do

    for scenario in scenarios:

        for enforce_majority in majority_possibilities:

            folder = str(scenario) + "SC" + "selfPlay" + "M" + str(enforce_majority) # need this in here somewhere or I won't know which is which.

            if scenario == "homo":
                evolve_homogenous_SC(popSize, numGeneCopies, startIndex, numGens, gamesPerGen, agentsPerGame,
                                     roundsPerGame, povertyLine, folder,
                                     extraAgents, max_workers, enforce_majority)
            if scenario == "mixed":
                evolve_mixed_SC(popSize, numGeneCopies, startIndex, numGens, gamesPerGen, agentsPerGame, roundsPerGame,
                                povertyLine, folder,
                                extraAgents, max_workers, enforce_majority)

def run_simulations():
    # this section is just stuff that stays the same from batch to batch. Don't touch it.
    forcedRandom = False
    num_players = 10
    random_agents = True  # Human behavior works better with em. # lets try reruning with all agents
    num_humans = 0
    num_cats = 0

    jhg_bot_type = 0  # 0 is gene bots, 2 is social welfare and 3 is random. ## Social welfare and random are deprecated, don't look at them.
    num_attempts = 1000  # number of batches to do.

    # all considerations about the new cats have been removed. we need to add a self play thing.
    # agent_names = ["homoJHGSelfPlay.csv", "mixedJHGSelfPlay.csv"] # sure
    #  lets dynamically grab all the agent names
    agent_directory = r"C:\Users\Sean Smith\Documents\GitHub\JHG-SC\Server\Engine\botGenerations"
    # agent_names = get_file_names(agent_directory) # go aheand and only run the ones we need.
    agent_names = ["mixedSCselfPlayMFalse.csv", "mixedSCselfPlayMTrue.csv"]



    round_types = [["J", 30], ["S", 30]] # no mixing.
    # round_types = [["J", 3], ["S", 3]]  # small example to make sure everything is getting written appropriately.
    scenarios = ["SelfPlay"]  # For now we are only concerned with self play stuff.
    # 1 pure pops, 1 pure util, third has a bunch of constants that I want to test.
    # peep_constants_list = [[1], [0], [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]] # not sure the best way to test this
    peep_constants_list = [[1], [0]]  # doesn't actually matter yet, still working on support for cross play.
    # ROUND STATE: JHG, SC, COMBINED
    # enforce_majorities_list = [[True], [True, False], [True, False]]
    enforce_majorities_list = [[True], [True, False]] # PURE JHG, PURE SC.

    new_list = [ImprovedJakeCat() for _ in range(num_cats)] # kind of? just as a prototype, its not yet being tested / supported.

    # ok there has GOT to be a better way to run this stuff.
    run_data_crunching_simulations(max_workers, forcedRandom, num_players, random_agents, num_humans,
                  jhg_bot_type, num_attempts, agent_names,
                  round_types, scenarios, peep_constants_list, enforce_majorities_list, new_list)


def copy_the_genetic_stuff():
    source_1 = r"C:\Users\Sean Smith\Documents\GitHub\JHG-SC\offlineSimStuff\geneticStuff\pureSC\homo\homoSCselfPlayMFalse\gen_199.csv"
    destination_1 = r"C:\Users\Sean Smith\Documents\GitHub\JHG-SC\Server\Engine\botGenerations\homoSCselfPlayMFalse.csv"
    shutil.copy(source_1, destination_1) # THIS WILL OVERWRITE DESTINATION 1 if you are NOT careful

    source_2 = r"C:\Users\Sean Smith\Documents\GitHub\JHG-SC\offlineSimStuff\geneticStuff\pureSC\homo\homoSCselfPlayMTrue\gen_199.csv"
    destination_2 = r"C:\Users\Sean Smith\Documents\GitHub\JHG-SC\Server\Engine\botGenerations\homoSCselfPlayMTrue.csv"
    shutil.copy(source_2, destination_2)

    source_3 = r"C:\Users\Sean Smith\Documents\GitHub\JHG-SC\offlineSimStuff\geneticStuff\pureSC\mixed\mixedSCselfPlayMFalse\gen_199.csv"
    destination_3 = r"C:\Users\Sean Smith\Documents\GitHub\JHG-SC\Server\Engine\botGenerations\mixedSCselfPlayMFalse.csv"
    shutil.copy(source_3, destination_3)

    source_4 = r"C:\Users\Sean Smith\Documents\GitHub\JHG-SC\offlineSimStuff\geneticStuff\pureSC\mixed\mixedSCselfPlayMTrue\gen_199.csv"
    destination_4 = r"C:\Users\Sean Smith\Documents\GitHub\JHG-SC\Server\Engine\botGenerations\mixedSCselfPlayMTrue.csv"
    shutil.copy(source_4, destination_4)



if __name__ == "__main__":
    cpu_count = os.cpu_count()
    max_workers = max(1, os.cpu_count() - 2) # save some cores for the rest of us!

    # looks like the simulations and writing crashed, lets try running it again and see what happens.

    # run_genetic_stuff()

    # copy_the_genetic_stuff()

    # run_simulations()



