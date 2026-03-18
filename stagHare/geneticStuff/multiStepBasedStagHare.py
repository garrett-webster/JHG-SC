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
        output_dir = os.path.join(script_dir, "third attempt, 6x6", "theGenerations") # just to give it somewhere to go
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
    print(f"Average utility in generation {gen}: {float(avg_fitness):.4f} Average Popularity: {float(avg_popularity):.4f}")


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


def mutateIt(gene):  # expect gene to be an int. if its not there is going to be a problem.
    v = random.randrange(100)
    if v > 15:
        return gene  # no mutation
    elif v < 3:
        return random.randrange(101)
    else:
        g = gene + random.randrange(11) - 5
        if g < 0:  # need to cap values from 0, 100
            g = 0
        if g > 100:
            g = 100
    return g

def selectByTournament(thePopulation, popSize, use_relative, tournament_size=4):
    contestants = random.sample(range(popSize), tournament_size)
    if use_relative:
        return max(contestants, key=lambda i: thePopulation[i].relativeFitness)
    else:
        return max(contestants, key=lambda i: thePopulation[i].absoluteFitness)


def evolvePopulationPairsAgressive(theGenePoolsOld, popSize, numGeneCopies):
    theNewGenePools = []
    num_genes = len(theGenePoolsOld[0].genes_long[0]) # bars??
    ind1 = -1
    ind2 = -1

    # elitism addedd - carry the top agents forward unchanged.
    num_elites = max(1, popSize // 10) # top 10 percent survive.
    sorted_by_relative = sorted(range(popSize), key=lambda i: theGenePoolsOld[i].relativeFitness, reverse=True)

    for i in range(num_elites):
        elite_genes = extractGene(theGenePoolsOld[sorted_by_relative[i]].genes_long[0])
        theNewGenePools.append(GeneAgent3(elite_genes, numGeneCopies))

    for i in range(popSize - num_elites):
        if i < popSize * 0.35: # 35% elite crossover paris
            ind1 = selectByTournament(theGenePoolsOld, popSize, use_relative=True)
            ind2 = selectByTournament(theGenePoolsOld, popSize, use_relative=False)
            while ind2 == ind1:
                ind2 = selectByTournament(theGenePoolsOld, popSize, use_relative=False)
        else:
            ind1 = selectByTournament(theGenePoolsOld, popSize, use_relative=False)
            ind2 = selectByTournament(theGenePoolsOld, popSize, use_relative=False)
            while ind2 == ind1:
                ind2 = selectByTournament(theGenePoolsOld, popSize, use_relative=False)

        if ind1 == -1 or ind2 == -1:
            print("Something wrong in the evolve thing")

        geneStr = "gene_"
        ind1Genes = extractGene(theGenePoolsOld[ind1].genes_long[0]).split("_")[1:]
        ind2Genes = extractGene(theGenePoolsOld[ind1].genes_long[0]).split("_")[1:]

        for g in range(num_genes):
            minKeepindex = 12
            if g == minKeepindex:
                geneStr += "0_"
                continue
            if bool(random.getrandbits(1)):
                geneStr +=str(mutateIt(int(ind1Genes[g])))
                if g < num_genes - 1:
                    geneStr += "_"
            else:
                geneStr += str(mutateIt(int(ind2Genes[g])))
                if g < num_genes - 1:
                    geneStr += "_"
        theNewGenePools.append(GeneAgent3(geneStr, numGeneCopies))

    return theNewGenePools


def evolvePopulationPairs(theGenePoolsOld, popSize, numGeneCopies):
    theNewGenePools = []
    num_genes = len(theGenePoolsOld[0].genes_long[0])
    ind1 = -1
    ind2 = -1

    for i in range(popSize):
        if i < popSize / 5.0:  # this is making the assumption that popSize is 60 people large.
            ind1 = selectByFitness(theGenePoolsOld, popSize, True)
            ind2 = selectByFitness(theGenePoolsOld, popSize, False)
            while ind2 == ind1:  # prevent themselves from self breeding
                ind2 = selectByFitness(theGenePoolsOld, popSize, False)

        else:
            ind1 = selectByFitness(theGenePoolsOld, popSize, False)
            ind2 = selectByFitness(theGenePoolsOld, popSize, False)
            while ind2 == ind1:
                ind2 = selectByFitness(theGenePoolsOld, popSize, False)

        if ind1 == -1 or ind2 == -1:
            print("THAT WAS WRONG")
            print("here is the pop size ", popSize)

        geneStr = "gene_"

        # ind1Genes = extractGene(theGenePoolsOld[ind1].genes_long[0]).split("_")[1:]

        ind1Genes = extractGene(theGenePoolsOld[ind1].genes_long[0]).split("_")[
                    1:]  # the "gene_" at the beginning for both.
        ind2Genes = extractGene(theGenePoolsOld[ind2].genes_long[0]).split("_")[1:]

        for g in range(num_genes):
            minKeepIndex = 12
            if g == minKeepIndex:
                geneStr += "0_"  # maybe??
                continue  # we don't want to update this or anything, go back to the beginning.
            if bool(random.getrandbits(1)):  # just a 50/50 shot
                geneStr += str(mutateIt(int(ind1Genes[g])))
                if g < num_genes - 1:
                    geneStr += "_"

            else:
                geneStr += str(mutateIt(int(ind2Genes[g])))
                if g < num_genes - 1:
                    geneStr += "_"

        theNewGenePools.append(GeneAgent3(geneStr, numGeneCopies))  # create a new agent

    return theNewGenePools


def compute_game_seed(global_seed, generation_idx, game_idx):
    return global_seed + generation_idx * 100 + game_idx

def runGame(agent_genes, numGeneCopies, agentsPerGame, roundsPerGame, gen, game_idx, folder, enforce_majority, random_agents, forced_random, height, width):


    # seed = compute_game_seed(GLOBAL_SEED, gen, game_idx)
    # random.seed(seed)
    # np.random.seed(seed)

    # bc we are only using a single gene every time, we can JUST pass that gene around and generate agents as needed.
    # should save us a lot of copying and passing aroudn overhead.


    pmetrics = playGame(agent_genes, game_idx, random_agents, forced_random, height, width) # this should be all we need


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
def playGame(theGenes, game, random_agents, forced_random, height, width):
    # so this is the part I was kinda worried about, and there isn't a godo way to replicate it bc the flutter thing just works so differently
    # so we are going to addlib this portion.
    num_humans = 0 # never a reason to change this, but does make code more readable.
    total_agents = 3
    # agent params should already be in there sire.
    agent_scenario = 3
    agent_type = 3

    hunters = create_hunters_with_genes(theGenes, random_agents, forced_random) # the assingment has been undererstood

    # get dat new score.
    new_scores = run_trial_genetic(hunters, height, width)



    # we can use the gen adn the game to write the results to a file if we really want to.

    # we shall rework this in a second methinks.
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


def evolve_step_based_SH(popSize, numGeneCopies, startIndex, numGens, gamesPerGen, agentsPerGame, roundsPerGame, povertyLine, folder,
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

    for gen in tqdm(range(numGens), desc="Mixed", leave=False):
        print("starting gen", gen)

        args_list = [] # just create this so we have it somewhere.

        for game_idx in range(gamesPerGen):
            agent_indices = [random.randrange(popSize) for _ in range(agentsPerGame)]
            agent_genes = [
                extractGene(theGenePools[idx].genes_long[0])
                for idx in agent_indices
            ]

            args_list.append((
                game_idx, agent_indices, agent_genes, numGeneCopies, agentsPerGame, roundsPerGame,
                folder, gen, enforce_majority, random_agents, forced_random, height, width
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
            theGenePools = evolvePopulationPairsAgressive(theGenePoolsOld, popSize, numGeneCopies)





# GLOBAL_SEED = 42

if __name__ == "__main__":
    # print("We start here ")

    # random.seed(GLOBAL_SEED)
    # np.random.seed(GLOBAL_SEED)

    cpu_count = os.cpu_count()
    max_workers = max(1, os.cpu_count() - 2) # save some cores for the rest of us!
    # max_workers = 1 # I just want one thread please. we debugging rn sire.

    popSize = 60
    numGeneCopies = 1
    startIndex = 0
    numGens = 100
    gamesPerGen = 20
    agentsPerGame = 3 # we can only fit 3 hunters in there at at time...
    roundsPerGame = 30
    numCats = 0
    povertyLine = 0
    folder = ""
    enforce_majority = False
    random_agents = True
    forced_random = False
    height = 6
    width = 6
    evolve_step_based_SH(popSize, numGeneCopies, startIndex, numGens, gamesPerGen, agentsPerGame, roundsPerGame, povertyLine, folder,
                    max_workers, enforce_majority, random_agents, forced_random, height, width)
    # we are running no fear, no chat
