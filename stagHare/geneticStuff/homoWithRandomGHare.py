# from Server.Engine.completeBots.jakecat import JakeCAT # this is the EXACT cat agent used in the OG_JHG_IJCAI paper. not sure if its the one melissa used...import
from prompt_toolkit.utils import to_str

from stagHare.agents.cabAgentThing import CabAgent # this is the cabAgent for STAGhare specifically.
import random
import numpy as np
import os
import csv  # used for writing to files

from concurrent.futures import ProcessPoolExecutor, as_completed # where the multiprocessing magic happens
from collections import defaultdict # him... I remember him from the stag_hare project...
import itertools
from tqdm import tqdm
from Server.Engine.completeBots.geneagent3 import GeneAgent3 # we need him for some random creation stuff.
from stagHare.runnerHelper import * # just get this all in here.
import copy

# class to hold the actual pop stuff for purposes of updating everything.
class PopularityMetrics:
    def __init__(self, gene, avePop, endPop):
        self.gene = gene
        self.avePop = avePop
        self.endPop = endPop
        self.relPop = 0  # just so it has SOME kind fo value.

    def set_relPop(self, relPop):
        self.relPop = relPop

    def __str__(self):
        return f"PopularityMetrics(avePop: {self.avePop}, endPop: {self.endPop}, relPop: {self.relPop}, gene: {self.gene})"

# try using this to hold things upstream of pmetrics to cauge agent metrics.
class AgentMetrics:
    def __init__(self, idx, absoluteFitness, count=1):
        self.idx = idx
        self.absoluteFitness = absoluteFitness
        self.count = count


def randomGeneString(numGeneCopies):
    GeneAgent3("", numGeneCopies)
    return GeneAgent3("", numGeneCopies).genes_long


# worry about this later, just have it here for now.
def write_generational_results(theGenePools, popSize, gen, folder):
    for i in range(popSize):
        if theGenePools[i].count > 0:
            theGenePools[i].relativeFitness /= theGenePools[i].count
            theGenePools[i].absoluteFitness /= theGenePools[i].count
            theGenePools[i].relativePopularity /= theGenePools[i].count
            theGenePools[i].absolutePopularity /= theGenePools[i].count
        else:
            theGenePools[i].relativeFitness = 0.0
            theGenePools[i].absoluteFitness = 0.0
            theGenePools[i].relativePopularity = 0.0
            theGenePools[i].absolutePopularity = 0.0

    # Sort agents by fitness
    sorted_agents = sorted(theGenePools, key=lambda agent: agent.absoluteFitness, reverse=True)

    # Get the absolute path to the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the full output directory path
    if folder == "":
        output_dir = os.path.join(script_dir, "HardHomo1Again", "theGenerations") # just to give it somewhere to go
    else:
        output_dir = os.path.join(script_dir, folder) # just to give it somewhere to go
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    # Construct the filename path
    filename = os.path.join(output_dir, f"gen_{gen}.csv")
    # Write CSV
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        # get rid of this STUPID and STINKY header.
        # writer.writerow(["Genes", "GamesPlayed", "RelativeUtility", "AbsoluteUtility"])  # optional header
        for agent in sorted_agents:
            writer.writerow([
                agent.getString(),
                agent.count,
                np.round(agent.relativeFitness, 4),
                np.round(agent.absoluteFitness, 4),
                np.round(agent.relativePopularity, 4),
                np.round(agent.absolutePopularity, 4),
            ])
    # force it to squeeze the scalar value out. not sure what the problem was.
    avg_fitness = np.sum([float(np.squeeze(agent.absoluteFitness)) for agent in theGenePools]) / popSize
    avg_popularity = np.sum([float(np.squeeze(agent.absolutePopularity)) for agent in theGenePools]) / popSize
    # print(f"Average utility in generation {gen}: {float(avg_fitness):.4f} Average Popularity: {float(avg_popularity):.4f}")


def selectByFitness(thePopulation, popSize, _rank):
    mag = 0.0
    for i in range(popSize):
        if _rank:
            mag += thePopulation[i].relativeFitness
        else:
            mag += thePopulation[i].absoluteFitness
    num = random.random()
    sum = 0.0
    for i in range(popSize):
        if _rank:
            sum += thePopulation[i].relativeFitness / mag
        else:
            sum += thePopulation[i].absoluteFitness / mag
        if num < sum:
            return i  # no clue what this does to be so honest with you

    print("uh oh, somethign went wrong, there was so selection, bricking")
    return popSize - 1  # return the last index.


def mutateIt(value, mutation_rate=0.05, magnitude=1):
    """
    lower chance mutation rate thing.
    """
    if random.random() < mutation_rate:
        return value + random.randint(-magnitude, magnitude)
    return value


# lets breed these boys for cooperation.
def evolvePopulationPairs(theGenePoolsOld, popSize, numGeneCopies):
    # sort by absolute fitness, assuming that higher absolute fitness is better.
    # change the attribute below for relativeFitness
    sorted_pools = sorted(theGenePoolsOld, key=lambda x: x.absoluteFitness, reverse=True)

    # elite size -- keep the top 10% untouched
    num_elites = max(1, popSize // 10)
    elites = sorted_pools[:num_elites]

    # breeding pool is now top 20%
    breeding_pool = sorted_pools[: max(2, popSize // 5)]

    # start the new population with elites.
    theNewGenePools = [GeneAgent3(extractGene(ind.genes_long[0]), numGeneCopies) for ind in elites]

    # fill the rest with children
    while len(theNewGenePools) < popSize:
        # pick two parents from breeding pool (top 20%)
        parent1 = random.choice(breeding_pool)
        parent2 = random.choice(breeding_pool)

        while parent1 == parent2:
            parent2 = random.choice(breeding_pool)

        child_gene_str = crossover_and_mutate(parent1, parent2, numGeneCopies)
        theNewGenePools.append(GeneAgent3(child_gene_str, numGeneCopies))

    return theNewGenePools[:popSize] # just in case something blew up

def crossover_and_mutate(parent1, parent2, numGeneCopies):
    ''' same crossover logic as before, but with mutation rate controlled'''
    ind1_vals = extractGene(parent1.genes_long[0]).split("_")[1:]
    ind2_vals = extractGene(parent2.genes_long[0]).split("_")[1:]

    num_genes = len(ind1_vals)

    gene_str = "gene_"
    minKeepIndex = 12

    for g in range(num_genes):
        if g == minKeepIndex:
            gene_str += "0_"
            continue

        if random.getrandbits(1):
            val = int(ind1_vals[g])

        else:
            val = int(ind2_vals[g])

        mutated_val = mutateIt(val, mutation_rate=0.05, magnitude=1)

        gene_str += str(mutated_val)
        if g < num_genes - 1:
            gene_str += "_"

    return gene_str


def compute_game_seed(global_seed, generation_idx, game_idx):
    return global_seed + generation_idx * 100 + game_idx

def runGame(agent_genes, numGeneCopies, agentsPerGame, roundsPerGame, gen, game_idx, folder, enforce_majority, random_agents, forced_random, height, width):
    # seed = compute_game_seed(GLOBAL_SEED, gen, game_idx)
    # random.seed(seed)
    # np.random.seed(seed)

    # bc we are only using a single gene every time, we can JUST pass that gene around and generate agents as needed.
    # should save us a lot of copying and passing aroudn overhead.


    pmetrics = playGame(agent_genes, game_idx, random_agents, forced_random, height, width, roundsPerGame) # this should be all we need


    metrics = []
    for i in range(agentsPerGame):
        absoluteFitness = pmetrics[i]["absoluteFitness"]

        metrics.append(AgentMetrics(
            idx=game_idx,
            absoluteFitness=absoluteFitness,
        ))
    return metrics

def set_game_params(agents):
    num_players = len(agents)
    poverty_line = 0
    forcedRandom = False  # replicable. # THIS SHOULD BE FALSE UNDER NORMAL TESTING.

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

    for a in agents:
        a.setGameParams(game_params, forcedRandom)

    return agents


# this is exactly the same actually. nice.
def playGame(theGenes, game, random_agents, forced_random, height, width, rounds_per_game):
    # run a trial, get the scores. The genetic is just a better wrapper for the simulator.
    new_scores = run_trial_genetic(theGenes, random_agents, forced_random, height, width, rounds_per_game)

    pmetrics = getPmetrics(game, new_scores, 3)
    return pmetrics  # this is the only thing we actually care about from this game.


def getPmetrics(game, new_scores, agentsPerGame):
    pmetrics = []

    # unfortunately, with only 1 game and not a really good way to try and understand whats going on, there isn't
    # nearly as much that we can use to fuel our information deficit.
    for i in range(agentsPerGame):
        metric = {
            "idx" : game,
            "absoluteFitness" : new_scores[i],
            "count" : 1,
        }
        pmetrics.append(metric)
    return pmetrics

def extractGene(gene_dict):
    gene_str = "gene_"
    values = list(gene_dict.values())
    result = "_".join(map(str, values))
    gene_str += result
    return gene_str


def run_game_helper(args):
    (game_idx, agent_indices, agent_genes, numGeneCopies, agentsPerGame, roundsPerGame, folder, gen, enforce_majority, random_agents, forced_random, height, width) = args

    metrics = runGame(agent_genes, numGeneCopies, agentsPerGame, roundsPerGame, gen, game_idx, folder, enforce_majority, random_agents, forced_random, height, width)

    for i, m in enumerate(metrics):
        m.idx = agent_indices[i]
    return metrics


def homo_based_SH(popSize, numGeneCopies, startIndex, numGens, gamesPerGen, agentsPerGame, roundsPerGame, povertyLine, folder,
           max_workers, enforce_majority, random_agents, forced_random, height, width):
    theGenePools = []
    theGenePoolsOld = []

    # implementatino specifc to this: We just do everything through gene pools, like before. we extract the genes, pass those down,
    # then take the pmetrics back up and attach them back to each gene. By doing this, we don't have to worry about different bot types
    # and can use this same algorithm with minimal changes to all sorts of test beds.

    if startIndex == 0:
        for j in range(popSize):
            # the agent name doesn't matter, just needs to have .csv in there somewhere.
            theGenePools.append(GeneAgent3("", 1)) # no gene string, random inititlization. maybe he initil  # just have it give them a random ID that it can't be.

    for gen in tqdm(range(numGens), desc="Homogenous", leave=False):
        args_list = []

        for game_idx in range(gamesPerGen):
            # Pick one individual for this whole game (cycle through population)
            ind_idx = game_idx % popSize
            base_gene = extractGene(theGenePools[ind_idx].genes_long[0])

            # Create a list of agentsPerGame identical copies
            # (use deepcopy if the gene is a mutable object that might be mutated during the game)
            agent_genes = [copy.deepcopy(base_gene) for _ in range(agentsPerGame)]

            # All agents trace back to the same individual
            agent_indices = [ind_idx] * agentsPerGame

            # just easier to prepare this all at once.
            args_list.append((
                game_idx, agent_indices, agent_genes, numGeneCopies, agentsPerGame,
                roundsPerGame, folder, gen, enforce_majority, random_agents,
                forced_random, height, width
            ))

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            all_metrics_nested = executor.map(run_game_helper, args_list)

            all_metrics = list(itertools.chain.from_iterable(all_metrics_nested))

            agg = defaultdict(lambda: {"absoluteFitness": 0.0, "count": 0})
            for m in all_metrics:
                idx = m.idx
                agg[idx]["absoluteFitness"] += m.absoluteFitness
                agg[idx]["count"] += m.count

            for idx, vals in agg.items():
                theGenePools[idx].absoluteFitness += vals["absoluteFitness"]
                theGenePools[idx].count += vals["count"]

            for g in theGenePools:
                if g.count > 0:
                    g.absoluteFitness /= g.count
                else:
                    g.absoluteFitness = 0

            total_abs = sum(g.absoluteFitness for g in theGenePools)
            for g in theGenePools:
                g.relativeFitness = g.absoluteFitness / total_abs if total_abs > 0 else 0

            theGenePools = sorted(theGenePools, key=lambda g: g.absoluteFitness)
            write_generational_results(theGenePools, popSize, gen, folder)

            theGenePoolsOld = theGenePools
            # lets just see if htis works at all.
            theGenePools = evolvePopulationPairs(theGenePoolsOld, popSize, numGeneCopies)





# GLOBAL_SEED = 42

if __name__ == "__main__":
    # print("We start here ")

    # random.seed(GLOBAL_SEED)
    # np.random.seed(GLOBAL_SEED)

    cpu_count = os.cpu_count()
    max_workers = max(1, os.cpu_count() - 2) # save some cores for the rest of us!
    # max_workers = 1 # I just want one thread please. we debugging rn sire.

    popSize = 100
    numGeneCopies = 1
    startIndex = 0
    numGens = 200
    gamesPerGen = 20
    agentsPerGame = 3 # we can only fit 3 hunters in there at at time...
    rounds_per_game = 1 # lets do a step based version super quick.
    numCats = 0
    povertyLine = 0
    folder = ""
    enforce_majority = False
    random_agents = True
    forced_random = False
    height = 16
    width = 16
    random_hare_chance = 5 # 5% chance that a hare agent spawns in with them.
    homo_based_SH(popSize, numGeneCopies, startIndex, numGens, gamesPerGen, agentsPerGame, rounds_per_game, povertyLine, folder,
                    max_workers, enforce_majority, random_agents, forced_random, height, width)
    # we are running no fear, no chat
