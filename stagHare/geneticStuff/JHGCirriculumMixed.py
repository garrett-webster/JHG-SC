# from Server.Engine.completeBots.jakecat import JakeCAT # this is the EXACT cat agent used in the OG_JHG_IJCAI paper. not sure if its the one melissa used...import
from prompt_toolkit.utils import to_str

from Server.Engine.completeBots.improvedJakeCate import ImprovedJakeCat
# from Server.Engine.completeBots.basicGeneAgent3 import BasicGeneAgent3 # this is the EXACT basicAgent used by jake in his paper.
from Server.Engine.completeBots.geneagent3 import GeneAgent3
import random
import numpy as np
import os
import csv  # used for writing to files
from Server.Engine.simulator import GameSimulator

from concurrent.futures import ProcessPoolExecutor, as_completed # where the multiprocessing magic happens
from collections import defaultdict # him... I remember him from the stag_hare project...
import itertools
from tqdm import tqdm

from offlineSimStuff.pureJHGGraphing import run_jhg_graphing
from offlineSimStuff.runningTools.runnerHelper import create_jhg_sim_stripped


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
        # don't use these for this version, staghunt silly
        # self.avePop = avePop
        # self.endPop = endPop
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
        output_dir = os.path.join(script_dir, "MixedJHG", "attempt2") # just to give it somewhere to go
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
    # avg_fitness = np.sum([float(np.squeeze(agent.absoluteFitness)) for agent in theGenePools]) / popSize
    avg_popularity = np.sum([float(np.squeeze(agent.absoluteFitness)) for agent in theGenePools]) / popSize
    # print(f"Average utility in generation {gen}: {float(avg_fitness):.4f} Average Popularity: {float(avg_popularity):.4f}")
    print(f"Average popularity in generation: {float(avg_popularity):.4f}")


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

def runGame(agent_genes, numGeneCopies, agentsPerGame, roundsPerGame, gen, game_idx, folder, extraAgents):
    # seed = compute_game_seed(GLOBAL_SEED, gen, game_idx)
    # random.seed(seed)
    # np.random.seed(seed)

    # bc we are only using a single gene every time, we can JUST pass that gene around and generate agents as needed.
    # should save us a lot of copying and passing aroudn overhead.

    forced_random = False # if we make it true we use the list. not a fan.
    pmetrics = playGame(agent_genes, game_idx, forced_random) # this should be all we need


    metrics = []
    for i in range(agentsPerGame):
        absoluteFitness = pmetrics[i]["absoluteFitness"]

        metrics.append(AgentMetrics(
            idx=game_idx,
            absoluteFitness=absoluteFitness,
        ))
    return metrics

# this is exactly the same actually. nice.
def playGame(theGenes, game, forced_random):
    # so this is the part I was kinda worried about, and there isn't a godo way to replicate it bc the flutter thing just works so differently
    # so we are going to addlib this portion.
    # create the sim
    pmetrics_list = [] # just to make my compiler stop yelling at me.
    numGeneCopies = 1 # we only need 1, long story.
    num_agents_list = [3, 5, 10] # I actually don't ever use 5, but I figure it couldn't hurt.
    total_agents = len(theGenes)

    for num_agents in num_agents_list:
        agents = [GeneAgent3(theGenes[0], numGeneCopies) for i in range(num_agents)]

        # this should adjsut the agents as well. maybe.
        new_simulator = create_jhg_sim_stripped(agents, forced_random) # thats literally it.
        num_rounds = 30 # just for fun, make this passable.
        run_jhg_graphing(new_simulator, False, num_rounds)
        # we can use the gen adn the game to write the results to a file if we really want to.

        pmetrics = getPmetrics(game, new_simulator.game_popularities[-1], num_agents)
        pmetrics_list.append(pmetrics)

    pmetrics = create_pmetrics_from_list(pmetrics_list, game, total_agents)
    return pmetrics # the only thing we actually care about

# TODO: add the weighting system here like you wanted.
import random

def create_pmetrics_from_list(pmetrics_list, game, total_agents, noise_std=2.0):
    # Accumulate sum and count for each agent
    score_sums = [0.0] * total_agents
    score_counts = [0] * total_agents

    for score_list in pmetrics_list:
        for i, element in enumerate(score_list):
            score_sums[i] += element["absoluteFitness"]
            score_counts[i] += 1

    # Compute average, add noise, then apply your weighting
    new_pmetrics = []
    for i in range(total_agents):
        if score_counts[i] > 0:
            avg_fitness = score_sums[i] / score_counts[i]
        else:
            avg_fitness = 0.0

        # Add Gaussian noise to simulate SH's stochasticity
        noisy_fitness = avg_fitness + random.gauss(0, noise_std)
        # optional: clip to a reasonable range if needed
        noisy_fitness = max(0.0, noisy_fitness)

        # Your original weighting: depending on the index (which corresponds to player position,
        # but careful: this assumes the order in pmetrics_list matches the 3,5,10 player games.
        # If that's true, then keep it; else reconsider.)
        if i <= 2:
            weight = 3
        elif i <= 4:
            weight = 2
        elif i <= 9:
            weight = 1
        else:
            weight = -1   # mark invalid

        metric = {
            "idx": game,
            "absoluteFitness": noisy_fitness,
            "count": weight,   # using your custom weight, not the actual game count
        }
        new_pmetrics.append(metric)

    return new_pmetrics






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
    forcedRandom = True  # replicable.

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


def run_game_helper(args):
    (game_idx, agent_indices, agent_genes, numGeneCopies, agentsPerGame, roundsPerGame, folder, extraAgents, gen) = args

    metrics = runGame(agent_genes, numGeneCopies, agentsPerGame, roundsPerGame,
                      gen, game_idx, folder, extraAgents)

    for i, m in enumerate(metrics):
        m.idx = agent_indices[i]
    return metrics


def evolve_mixed_JHG(popSize, numGeneCopies, startIndex, numGens, gamesPerGen, agentsPerGame, roundsPerGame, povertyLine, folder,
           extraAgents, max_workers):
    theGenePools = []
    theGenePoolsOld = []

    # we can kind of assume that we start at 0, just as a matter of course. started from the bottom now we here.
    # can further modify this for tests, we can have a random folder (rnums.text) and make sure results are consistent between bots or whatever.
    if startIndex == 0:
        for j in range(popSize):
            theGenePools.append(GeneAgent3("", numGeneCopies))  # hot take I think I am going to keep it this way.
            # maybe the overhead is bigger? but they are clearly doing something else to get it be an agent.

    # we could open the CSV here, I am going to opt not to yet. create a functino called write genrational results and go from there.
    # I think we take the last successful thing, and run this on it, which doesn't make any sense... yet. I'll add it though.

    # theGenePools = evolvePopulationPairs(theGenePoolsOld, popSize, numGeneCopies) # only useful

    for gen in tqdm(range(numGens), desc="Mixed", leave=False):
        # print("starting gen", gen)

        args_list = []

        for game_idx in range(gamesPerGen):
            # rng = random.Random(compute_game_seed(GLOBAL_SEED, gen, game_idx)) # use this for deterministic worker seeding.
            agent_indices = [random.randrange(popSize) for _ in range(agentsPerGame)]
            agent_genes = [
                extractGene(theGenePools[idx].genes_long[0])
                for idx in agent_indices
            ]

            args_list.append((
                game_idx, agent_indices, agent_genes, numGeneCopies, agentsPerGame, roundsPerGame,
                folder, extraAgents, gen
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
            theGenePools = evolvePopulationPairs(theGenePoolsOld, popSize, numGeneCopies)




# GLOBAL_SEED = 42

if __name__ == "__main__":
    # print("We start here ")

    # random.seed(GLOBAL_SEED)
    # np.random.seed(GLOBAL_SEED)

    cpu_count = os.cpu_count()
    max_workers = max(1, os.cpu_count() - 2) # save some cores for the rest of us!
    # max_workers = 1

    # change all these before you actually start testing -- don't worry about it too much.
    popSize = 100
    numGeneCopies = 1
    startIndex = 0
    numGens = 100
    gamesPerGen = 60
    agentsPerGame = 10
    roundsPerGame = 30
    numCats = 0
    povertyLine = 0
    folder = ""
    extraAgents = [ImprovedJakeCat() for _ in range(numCats)]
    evolve_mixed_JHG(popSize, numGeneCopies, startIndex, numGens, gamesPerGen, agentsPerGame, roundsPerGame, povertyLine, folder,
           extraAgents, max_workers)
    # we are running no fear, no chat
