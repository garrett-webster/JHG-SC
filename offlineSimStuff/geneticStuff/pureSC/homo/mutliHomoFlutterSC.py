# from Server.Engine.completeBots.jakecat import JakeCAT # this is the EXACT cat agent used in the OG_JHG_IJCAI paper. not sure if its the one melissa used...import
from Server.Engine.completeBots.improvedJakeCate import ImprovedJakeCat
# from Server.Engine.completeBots.basicGeneAgent3 import BasicGeneAgent3 # this is the EXACT basicAgent used by jake in his paper.
from Server.Engine.completeBots.geneagent3 import GeneAgent3
import random
import numpy as np
import os
import csv  # used for writing to files
from Server.Engine.simulator import GameSimulator

from concurrent.futures import ProcessPoolExecutor  # where the multiprocessing magic happens
from collections import defaultdict # him... I remember him from the stag_hare project...
import itertools
from tqdm import tqdm

from offlineSimStuff.runningTools.runnerHelper import run_sc_stuff, create_sim, create_total_order


# class to hold the actual pop stuff for purposes of updating everything.
class PopularityMetrics:
    def __init__(self, index, gene, avePop, endPop):
        self.index = index
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
    def __init__(self, idx, absoluteFitness, avePop, endPop, count=1):
        self.idx = idx
        self.absoluteFitness = absoluteFitness
        self.avePop = avePop
        self.endPop = endPop
        self.count = count


def randomGeneString(numGeneCopies):
    GeneAgent3("", numGeneCopies)
    return GeneAgent3("", numGeneCopies).genes_long


# worry about this later, just have it here for now.
def write_generational_results(theGenePools, popSize, gen, folder, enforce_majority):
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
        output_dir = os.path.join(script_dir, "SecondAttemptLonger", "theGenerations") # just to give it somewhere to go
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


def writeGenerationalResults(theGenePools, popSize, gen, agentsPerGame, folder):
    # create a file here
    for i in range(popSize):
        # want the Gene, the Count, the Relative Fitness, the absoluteFitness, and the CVS formatted gene string
        pass


def evolvePopulationPairs(theGenePoolsOld, popSize, numGeneCopies):
    theNewGenePools = []
    num_genes = len(theGenePoolsOld[0].genes_long[0])
    ind1 = -1
    ind2 = -1

    for i in range(popSize):
        if i < popSize / 5.0:  # this is making the assumption that popSize is 100 people large.
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


def run_jhg_stuff(jhg_engine, round, agents, numAgents):
    # num agents is just everyone -- there is no need to discriminate between the two at this level.
    transactions = [0 for _ in range(numAgents)]
    T_prev = jhg_engine.get_transaction()

    for i in range(numAgents):
        transactions[i] = agents[i].play_round(
            i,
            round,
            T_prev[:, i],
            jhg_engine.get_popularity().tolist(),
            jhg_engine.get_influence(),
            jhg_engine.get_extra_data(i)
        )

    jhg_engine.play_round(transactions)

    return jhg_engine.get_influence()


def create_jhg_engine(agents):
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

    jhg_engine = GameSimulator(game_params)
    return jhg_engine, agents


def extractGene(gene_dict):
    gene_str = "gene_"
    values = list(gene_dict.values())
    result = "_".join(map(str, values))
    gene_str += result
    return gene_str


# something about pickling, IDK what.
def run_game_helper(args):
    game_idx, gene, numGeneCopies, agentsPerGame, roundsPerGame, folder, extraAgents, gen_idx, enforce_majority = args

    # seed = compute_game_seed(GLOBAL_SEED, gen_idx, game_idx)
    # random.seed(seed)
    # np.random.seed(seed)

    return run_game(game_idx, gene, numGeneCopies, agentsPerGame, roundsPerGame, folder, extraAgents, enforce_majority)

# def compute_game_seed(global_seed, generation_idx, game_idx):
#     return global_seed + generation_idx * 100 + game_idx

def play_sc_game(sc_sim, total_order, influence_matrix, curr_round, num_cycles, peep_constant):
    popularity_array = np.array([100 for _ in range(sc_sim.total_players)]) # just make a blank list of the pops.
    influence_matrix, _ = run_sc_stuff(sc_sim, popularity_array, total_order, influence_matrix, curr_round, num_cycles, peep_constant)
    return influence_matrix



# here we just changed the arguments a bit, thats literally it.
def playGame(theGene, agents, agentsPerGame, numExtraAgents, roundsPerGame, gen, game, enforce_majority):
    # so this is the part I was kinda worried about, and there isn't a godo way to replicate it bc the flutter thing just works so differently
    # so we are going to addlib this portion.
    num_humans = 0 # never a reason to change this, but does make code more readable.
    total_agents = agentsPerGame + numExtraAgents
    agents = set_game_params(agents)
    total_order = create_total_order(total_agents, num_humans)
    influence_matrix = np.array([[0 for _ in range(total_agents)] for _ in range(total_agents)])  # initalization for pure sc purposes
    sc_sim = create_sim(agentsPerGame, num_humans, total_order=total_order, enforce_majority=enforce_majority) # creates the sim.
    sc_sim.bot_ovveride(agents, numExtraAgents) # for the allocation bots to get written too. Some weird stuff under the hood there.


    num_cycles = 3
    peep_constant = 0.5 # doesn't actually matter, in a pure context.


    for round in range(roundsPerGame):
        # ironically enough everything is already updated and held in there, so don't worry about it. maybe.
        play_sc_game(sc_sim, total_order, influence_matrix, round, num_cycles, peep_constant)

    # we can use the gen adn the game to write the results to a file if we really want to.

    # we shall rework this in a second methinks.
    pmetrics = getPmetrics(game, theGene, sc_sim, agents, agentsPerGame, numExtraAgents, roundsPerGame)
    return pmetrics  # this is the only thing we actually care about from this game.


# so in this one, we create a new metric, we don't actullay use the struct, a dictionary works fine.
def getPmetrics(game, theGene, sc_sim, agents, agentsPerGame, numExtraAgents, roundsPerGame):
    pmetrics = []

    unworked_results = (sc_sim.results)  # all da pops

    rows = list(unworked_results.values())  # preserves insertion order

    arr = np.array(rows)

    cumulative = arr.cumsum(axis=1)

    pops = cumulative.tolist()
    pops = np.array(pops)  # convert back to ndarray for mean purposes

    ave_pop = pops.mean(axis=0) # get teh average per column
    end_pop = sc_sim.results_sums # this is effectively the last one.

    for i in range(agentsPerGame):
        metric = {
            "idx": game,  # genetic algorithm silly
            "absoluteFitness": (ave_pop[i] + end_pop[i]) / 2.0,
            "avePop": ave_pop[i],
            "endPop": end_pop[i],
            "count": 1
        }
        pmetrics.append(metric)

    return pmetrics

# run da game
def run_game(game_idx, gene, numGeneCopies, agentsPerGame, roundsPerGame, folder, extraAgents, enforce_majority):
    ## freeze the seed
    # random.seed(GLOBAL_SEED)
    # np.random.seed(GLOBAL_SEED)

    # Generate agents sharing the same gene
    # oh nevermind here they are, safe and sound.
    agents = [GeneAgent3(gene, numGeneCopies) for _ in range(agentsPerGame)]
    agents.extend(extraAgents)
    numExtraAgents = len(extraAgents)

    # Run the game
    pmetrics = playGame(gene, agents, agentsPerGame, numExtraAgents, roundsPerGame, game_idx, folder, enforce_majority)

    # Convert to structured metrics
    metrics = []
    for i in range(agentsPerGame):
        ave_pop = pmetrics[i]["avePop"] # now an object instead of a dict, so there's that.
        end_pop = pmetrics[i]["endPop"]
        abs_fit = (ave_pop + end_pop) / 2.0

        metrics.append(AgentMetrics(
            idx=game_idx,
            absoluteFitness=abs_fit,
            avePop=ave_pop,
            endPop=end_pop
        ))
    return metrics # here we actually use the object. no idea if its faster or not.


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



def evolve_homogenous_SC(popSize, numGeneCopies, startIndex, numGens, gamesPerGen, agentsPerGame,
           roundsPerGame, povertyLine, folder, extraAgents, maxWorkers, enforce_majority):

    theGenePools = []
    theGenePoolsOld = []

    if startIndex == 0:
        for _ in range(popSize):
            theGenePools.append(GeneAgent3("", numGeneCopies))

    for gen in tqdm(range(numGens), desc="Homo", leave=False):
        # print(f"Starting generation {gen}")

        # Prepare gene for each game
        genes_for_games = [extractGene(theGenePools[i % popSize].genes_long[0]) for i in range(gamesPerGen)]


        args_list = [
            (i, genes_for_games[i], numGeneCopies, agentsPerGame, roundsPerGame, folder, extraAgents, gen, enforce_majority)
            for i in range(gamesPerGen)
        ]

        # here is where the MAGIC happens
        with ProcessPoolExecutor(max_workers=maxWorkers) as executor:
            all_metrics_nested = executor.map(run_game_helper, args_list)

        # flatten metrics into something that I can actually use
        all_metrics = list(itertools.chain.from_iterable(all_metrics_nested))
        # print("here are all the metrics ", all_metrics)
        # get everything PER AGENT bc that makes more sense in this context. this includes the absolute fitnesses and counts.
        agg = defaultdict(lambda: {"absoluteFitness": 0.0, "count": 0})
        for m in all_metrics:
            idx = m.idx
            agg[idx]["absoluteFitness"] += m.absoluteFitness
            agg[idx]["count"] += m.count

        # now update the entire gene pool in one go
        for idx, vals in agg.items():
            theGenePools[idx].absoluteFitness += vals["absoluteFitness"]
            theGenePools[idx].count += vals["count"]

        # normalize the absolute values by counts
        for g in theGenePools:
            if g.count > 0:
                g.absoluteFitness /= g.count
            else:
                g.absoluteFitness = 0

        # now we finally get to the relative fitnesses.
        total_abs = sum(g.absoluteFitness for g in theGenePools)
        for g in theGenePools:
            g.relativeFitness = g.absoluteFitness / total_abs if total_abs > 0 else 0

        # Sort by absolute fitness
        theGenePools = sorted(theGenePools, key=lambda g: g.absoluteFitness)
        # Save results

        # DISIABLE THIS FOR NOW!! PUT IT BACK IN LATER, WE ARE TESTING SOMETHING
        # write_generational_results(theGenePools, popSize, gen, folder, enforce_majority)

        # Evolve to next generation
        theGenePoolsOld = theGenePools
        theGenePools = evolvePopulationPairs(theGenePoolsOld, popSize, numGeneCopies)

# GLOBAL_SEED = 42 # global little guy

if __name__ == "__main__":
    # print("We start here ")

    # # freeze the seed
    # random.seed(GLOBAL_SEED)
    # np.random.seed(GLOBAL_SEED)

    # starting with a small debugging example. really small pop, no cats, etc.


    cpu_count = os.cpu_count() # gets the the number of logical cores that we possess.
    max_workers = max(1, os.cpu_count() - 2) # save a couple of cores for other processes, don't want to overwhelm.

    popSize = 100
    numGeneCopies = 1
    startIndex = 0
    numGens = 200
    gamesPerGen = popSize  # this is in part what makes it homogenous. for mixed, use a discrete number
    agentsPerGame = 8
    roundsPerGame = 10
    numCats = 0
    povertyLine = 0
    folder = ""
    extraAgents = [ImprovedJakeCat() for _ in range(numCats)]
    enforce_majority = False
    evolve_homogenous_SC(popSize, numGeneCopies, startIndex, numGens, gamesPerGen, agentsPerGame, roundsPerGame, povertyLine, folder,
           extraAgents, max_workers, enforce_majority)
    # we are running no fear, no chat
