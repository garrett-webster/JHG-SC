import os

from mixed.multiMixedFlutterJHG import evolve_mixed
from homogenous.mutliHomoFlutterJHG import evolve_homogenous

from Server.Engine.completeBots.improvedJakeCate import ImprovedJakeCat # cat bot type

from tqdm import tqdm
import numpy as np

# Suppress invalid value warnings
np.seterr(invalid='ignore', divide='ignore')

def get_folder_name(algorith_type, scenario):
    folder_name = ""
    if scenario == "SelfPlay":
        folder_name += "selfPlay"
    if scenario == "jakeCats":
        folder_name += "jakeCats"

    return folder_name


if __name__ == "__main__":
    cpu_count = os.cpu_count()
    max_workers = max(1, os.cpu_count() - 2) # save some cores for the rest of us!


    popSize = 100
    numGeneCopies = 1
    startIndex = 0
    numGens = 200
    gamesPerGen = 100
    agentsPerGame = 10 # decrement this based on cat count
    roundsPerGame = 30
    povertyLine = 0
    folder = ""
    numCats = 0 # just as a default
    # work on my own cats in the backround, see if we can't get that to work any better.
    scenarios = ["jakeCats", "SelfPlay"]
    algorithm_types = [evolve_homogenous]

    # Flattened loop using range
    total_iterations = len(scenarios) * len(algorithm_types)

    for i in range(total_iterations):
    #for i in tqdm(range(total_iterations), desc="Scenarios", leave=False):
        # Map i back to the nested loops
        algorithm_type = algorithm_types[i // len(scenarios)]
        scenario = scenarios[i % len(scenarios)]
        if scenario == "SelfPlay":
            numCats = 0
        if scenario == "jakeCats":
            numCats = 2
        extraAgents = [ImprovedJakeCat() for _ in range(numCats)]
        currentAgentsPerGame = agentsPerGame - numCats # adjusted values for self play vs actual cats.
        folder = get_folder_name(algorithm_type, scenario)

        algorithm_type(popSize, numGeneCopies, startIndex, numGens, gamesPerGen, currentAgentsPerGame, roundsPerGame, povertyLine, folder,
       extraAgents, max_workers)




    # extraAgents = [ImprovedJakeCat() for _ in range(numCats)]
