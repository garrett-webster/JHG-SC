from Server.Engine.engine import JHGEngine
from Server.Engine.completeBots.geneagent3 import GeneAgent3
from Server.Engine.completeBots.baseagent import AbstractAgent
from dataclasses import dataclass
import random
import csv # WHEEE. make sure this doesn't leak over the client or server otherwise I have to update the venv on the chromebooks.
import os
import math
import numpy as np

"""
Genetic algorithm from C++ ijacai paper for training Gene3 agents in the Junior high test bed. this is the Python reference 
that I am using as a springboard for developing my own version for the SC + JHG version. evaluating fitness and whatnot is going to be 
difficult, but I am going to create a new file especially for my own format. today is my second tackle into this one to try and better
understand how this functinos before I use it myself. 
"""
## TODO: make sure that the results actually get written to a directory so we cna save them for later.
## TODO: add in the configured players functionality so we can train with other bots. (might need to adjust those bots to also work in the new testbed)

@dataclass # because python doesn't support dedicated new stucts the way C++ does. I could have built a custom class, but this seemed lighterweight and better addapted.
class PopularityMetrics:
    avePop: float
    endPop: float
    relPop: float

# ok so for our purposes this is almost always going to be 100. there are other things we CAN do but we are most interested in the initial 100 testbed.
def definiteInitialPopularities(initPopType, numPlayers, initialPopularities):
    # see its not gonna tell you this but you are going to need to return initial Popularities here
    basePop = 100.0
    if (initPopType == "random"):
        for i in range(numPlayers):
            initialPopularities[i] = (random.randint(0, 199)) + 1.0
    elif initPopType == "equal":
        for i in range(numPlayers):
            initialPopularities[i] = basePop
    elif initPopType == "step":
        for i in range(numPlayers):
            initialPopularities[i] = i + 1.0
        initialPopularities = shuffle(initialPopularities, numPlayers)
    elif initPopType == "random":
        for i in range(numPlayers):
            initialPopularities[i] = 1.0 / pow(i+1, 0.7)
        initialPopularities = shuffle(initialPopularities, numPlayers)
    elif initPopType == "highlow":
        for i in range(int(math.floor(numPlayers / 2))):
            initialPopularities[i] = 1.0 + random.randint(0, 49) + 150
        for i in range(int(math.ceil(numPlayers / 2)), numPlayers):
            initialPopularities[i] = 1.0 + random.randint(0, 49)
        initialPopularities = shuffle(initialPopularities, numPlayers)
    else:
        print("don't udnerstand input, going with equal ")
        for i in range(numPlayers): # the case we actually use.
            initialPopularities[i] = basePop

    # literally no clue what this does, other than be annoying. Seems to normalize everything just in case?
    toStartPop = basePop * numPlayers
    sm = sumVec(initialPopularities, numPlayers)
    for i in range(numPlayers):
        initialPopularities[i] /= sm
        initialPopularities[i] *= toStartPop

    return initialPopularities

# just a summing function. Python has a built in one, but to make sure that the codes match as 1:1 as possible
# I just went ahead and built the fetcher.
def sumVec(v, len):
    sm = 0.0
    for i in range(len):
        sm += v[i]
    return sm

# there is also probably a better way to do this as a built in python thing, but I went ahead and built it anyway.
def shuffle(initialPopularities, numPlayers):
    for i in range(numPlayers):
        n1 = random.randint(0, numPlayers-1)
        n2 = random.randint(0, numPlayers-1)
        tmp = initialPopularities[n1]
        initialPopularities[n1] = initialPopularities[n2]
        initialPopularities[n2] = tmp
    return initialPopularities


def playGame(agents, numPlayers, numRounds, gener, gamer, initialPopularities, povertyLine, forcedRandom):
    # for this one, reference defs.h in the C++ code. most of these are hard coded into the engine and this is just tranfering them over.
    # they might get set to different values in the engine, but i wan this engine to be consistent with other engines.
    # so for now just accept the magic numbers and we will move on with our day
    alpha = 0.2 # double check these magical fetchers when you get the chance actually.
    beta = 0.5
    give = 1.3
    keep = 0.95
    steal = 1.6
    base_pop = 100
    poverty_line = povertyLine
    game_params = {
        "alpha": alpha,
        "beta" : beta,
        "keep" : keep,
        "give" : steal,
        "steal" : steal,
        "poverty_line" : poverty_line,
    }
    for i in range(numPlayers):
        agents[i].setGameParams(game_params, forcedRandom)
        # IDK what post contract does, only seems to be relevant in the coop bots and I am not interesteed in them atm rn.


    numToknes = 2 * numPlayers # not actuall necessary as the numTokens is already built into the bots.
    received = [0.0 for _ in range(numPlayers)] # C++ really needs to allocate memeory before hadn
    transactions = [0 for _ in range(numPlayers)] # so this is how I replilcate it in python.

    for i in range(numPlayers): # I think this makes the fetcher square?
        transactions[i] = [0 for _ in range(numPlayers)]

    # they hard lean into initalizing arrays of type class and then filling them later, which is weird to replicate in python
    pmetrics = [PopularityMetrics(avePop=0, endPop=0, relPop=0) for _ in range(numPlayers)]
    # actually I can skip the next step because its just setting it up, yay for python one line loops.

    extra_data = {
        i: {
            j: None for j in range(numPlayers)
        } for i in range(numPlayers)
    }

    print("here is the extra data ", extra_data)
    # create a new JHG sim, so everything happens within the same sim
    jhg_sim = JHGEngine(alpha, beta, give, keep, steal, numPlayers, base_pop, povertyLine)
    for r in range(numRounds):
        for i in range(numPlayers):
            for j in range(numPlayers):
                received[j] = np.array(jhg_sim.T[r][j][i]) # ???
            #agents[i].play_round(numPlayers, numToknes, i, r, received, jhg_sim.P[r], jhg_sim.I[r], transactions[i])

            # player_idx, round_num, received, popularities, influence, extra_data, extra_flag=False
            transactions[i] = agents[i].play_round(i, r, received, jhg_sim.P[r], jhg_sim.I[r], extra_data) # ?? still don't know what the "extra data" is. might be transcations?
        jhg_sim.apply_transaction(transactions) # applies the round, this is where we learn

        for i in range(numPlayers): # how much have we increased overall and in this round
            pmetrics[i].avePop += jhg_sim.P[jhg_sim.t][i] / numRounds
            pmetrics[i].endPop = jhg_sim.P[jhg_sim.t][i]

    # this is where we dould record stuff under the game logs, not sure if I wnat to do that yet.
    # you know what, why not.
    filename = "../Results/theGameLogs/log_" + str(gener) + "_" + str(gamer) + ".csv"
    #jhg_sim.save(filename) # haven't actually bothered to write this yet.

    transactions = None # looks different than the C++ code, thats becuase garbage collection is a jerk.
    received = None
    jhg_sim = None

    return pmetrics # returns out data type

# writes the stuff so we can access it later when we want it.
def write_generational_results(theGenePools, popSize, gen, agentsPerGame):
    for i in range(popSize):
        if theGenePools[i].count > 0:
            theGenePools[i].relativeFitness /= theGenePools[i].count
            theGenePools[i].absoluteFitness /= theGenePools[i].count
        else:
            theGenePools[i].relativeFitness = 0.0
            theGenePools[i].absoluteFitness = 0.0

    # Sort agents by fitness
    sorted_agents = sorted(theGenePools, key=lambda agent: agent.absoluteFitness, reverse=True)

    # Ensure output directory exists
    output_dir = "../PureStuff/theGenerations"
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"gen_{gen}.csv")

    # Write CSV
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Genes", "GamesPlayed", "RelativeFitness", "AbsoluteFitness"])  # optional header
        for agent in sorted_agents:
            writer.writerow([
                agent.getString(),
                agent.count,
                round(agent.relativeFitness, 4),
                round(agent.absoluteFitness, 4)
            ])

    avg_fitness = sum(agent.absoluteFitness for agent in theGenePools) / popSize
    print(f"Average fitness in generation {gen}: {avg_fitness:.4f}")


def mutateIt(gene):
    v = random.randint(0, 99)
    if (v >= 15): # 85% chance of no mutation
        return gene
    elif v < 3: # 3% chance that it just completely changes
        return random.randint(0, 100)
    else: # leaves us with a 12% chance that it just slighly changes.
        g = gene + (random.randint(0, 10)) - 5
        if g < 0:
            g = 0
        if g > 100:
            g = 100
        return g # throw him back where we found it.


# takes in a gene pool, our popsize and the number of copies and proceeds to evolve all of the pairs.
def evolvePopulationPairs(theGenePool_prev, popSize, numGeneCopies):
    genes_dict = theGenePool_prev[0].genes_long[0]  # assume [dict]
    gene_keys = list(genes_dict.keys()) # just easier this way
    num_genes = len(gene_keys) * 3 # cycle through it 3 times, one for each one
    # represents the amount we will have to iterate through or something.
    # problem - you need to generate a list 3 times the length so we can put it all in there. trhat way you can have 3 copies. give it another whirl on monday.
    print("TheGenePool_prev[0]->numGenes:", num_genes) # this is 99, not 33.

    theGenePool = [GeneAgent3("", numGeneCopies, 2) for _ in range(popSize)] #initalize empty gene pool.

    for i in range(popSize): # for EVERY fetcher
        ind1 = selectByFitness(theGenePool_prev, popSize, True) if i < (popSize / 5) else selectByFitness(theGenePool_prev, popSize, False)
        ind2 = selectByFitness(theGenePool_prev, popSize, False)

        # the following was a fetching pain to translate over. it works but if it breaks I will have 0 idea of how to fix it. 5 stars.
        gene_values = [] # holds the new genes
        for g in range(num_genes):
            cycle = g // len(gene_keys)
            # we have 3 genes that have the same 33 repeating values. we iterate through all of them.
            # would probably be easier to just go through the list three times and adjust the keys as we go. however, if this works, I won't complain.
            new_g = g - (len(gene_keys) * cycle) # this should allow it to be new and not have any carry over issues.
            key = gene_keys[new_g]
            selected_gene = (
                mutateIt(theGenePool_prev[ind1].genes_long[cycle][key])
                if random.randint(0, 1) == 0
                else mutateIt(theGenePool_prev[ind2].genes_long[cycle][key])
            )
            gene_values.append(str(selected_gene))

        geneStr = "gene_" + "_".join(gene_values) # reassembles the genes
        theGenePool[i] = GeneAgent3(geneStr, numGeneCopies, 2) # creates a new agent at that index and puts it back in the gene pool.

    return theGenePool # puts back the new gene pool to be played with again.

# take in our population and put the best fetchers at the very top and the worst fetchers at the very bottom.
def selectByFitness(thePopulation, popSize, _rank):
    mag = 0.0
    for i in range(popSize):
        if (_rank):
            mag += thePopulation[i].relativeFitness
        else:
            mag += thePopulation[i].absoluteFitness
    num = random.random()  # Returns float in [0.0, 1.0)
    sum = 0.0
    for i in range(popSize):
        if (_rank):
            sum += thePopulation[i].relativeFitness / mag
        else:
            sum += thePopulation[i].absoluteFitness / mag

        if num <= sum:
            return i

    print("uh no select, whatever happened ", num, " ", sum)
    # exit(1)

    return popSize - 1

# once again, garbage collection in python is really nice.
def deleteGenePool(theGenePools, popSize):
    theGenePools = None
    return theGenePools


if __name__ == "__main__":
    ## -- INIT STUFF , didn't feel like using the command line everytime, thats on me. heres' the init and all explanation -- ##
    #// - run the code: ./jhgsim(0) evolve(1) ../Results/theGenerations(2) 100(3) 3(4) 0(5) 100(6) 100(7) 10(8) 30(9) 0(10) basicConfig(11) varied(12)
    # (fileName) (commandArgument) (Folder(2)), (numGeneCopies(3)), (startIndex(4)), (numGenes(5)), (gamesPerGen(6)), (agentsPerGame(7)), roundsPerGame(8), povertyLine(9)
    # using the default arguments from the ijacai documentation.
    # 0 -- executable (doesn't change)
    # 1 -- code directive to evolve population (doesn't change)
    theFolder = "SomeFolder" # folder where trained parameters of cab agents are stored.
    popSize = 100 # number of agnets in the gene pool (use 100 here)
    numGeneGopies = 3 # numbers of sets of genes (3 was the number used in the paper)
    startIndex = 0 # generation to start training (0 to start form scratch)
    num_gens = 100 # generation to end traning trains up to 99
    games_per_gen = 100 # agents from the gene pool are selected at random, 100 times.
    agentsPerGame = 10 # number of agents per game
    roundsPerGame = 30 # number fo rounds per game
    povertyLine = 0 # see SM-1
    configFile = "basicConfig" # trains with just cab agents, no assasains.
    initPops = "varied" # starts eveyrone at different initial popularities when training.
    tokens_per_player = 2 # probably best if I just reduce this back to whatever. (Added by me just in case we wanted to be silly)


    # should initialize this fetcher
    theGenePools = [GeneAgent3("", numGeneGopies) for _ in range(popSize)] # don't let this be empty

    numPlayers = agentsPerGame + 0 # could put gocnifutred players.size but that si currently empty and I couldn't care less.
    maxPlayers = numPlayers
    possible_init_pops = ["equal", "random", "step", "power", "highlow"]
    initPopularities = [0.0 for _ in range(numPlayers)]
    initRelativePops = [0.0 for _ in range(numPlayers)]
    plyrIdxs = [0 for _ in range(numPlayers)]
    agents = [AbstractAgent() for _ in range(popSize)] # unfortunately this DOES seem to be the best way to do this in python.

    for gen in range(num_gens): # however many generations we want
        for game in range(games_per_gen): # however many games we want per generation

            # pick individuals to put into the gene pools.
            for i in range(agentsPerGame):
                plyrIdxs[i] = random.randint(0, popSize - 1)
                agents[i] = theGenePools[plyrIdxs[i]]

            # not adding in the configured players yet, leave that alone for now.

            if initPops == "varied":
                sel = random.randint(0, 4)
            else:
                sel = 0
            initialPopularites = definiteInitialPopularities(possible_init_pops[sel], numPlayers, initPopularities)

            s = 0
            for i in range(numPlayers):
                s += initialPopularites[i]

            # pretty sure this just normalizes it AGAIN in case we missed it the first time.
            for i in range(numPlayers):
                initRelativePops[i] = initialPopularites[i]/s

            print("Here where we start ", agents[0])
            pmetrics = playGame(agents, numPlayers, roundsPerGame, gen, game, initialPopularites, povertyLine, False)

            # now we gotta calcualte relative popularity

            s = 0.0
            for i in range(numPlayers):
                s += pmetrics[i].avePop
            for i in range(numPlayers):
                pmetrics[i].relPop = pmetrics[i].avePop / s

            # print some stuff to the terminal for the purposes of understanding other stuf.f
            print("Indicies: ")
            for i in range(numPlayers):
                print("i, ", plyrIdxs[i])

            print("\n")
            print("averagePop :")
            for i in range(numPlayers):
                print(f"{pmetrics[i].avePop}.2")
            print("\n")
            print("\n")

            print("relPop: ")
            for i in range(numPlayers):
                print(f"{pmetrics[i].relPop}.2")

            print("\n")
            print("Average popularity ", s / agentsPerGame)


            # we gotta update fitness - fitness whole pizza in they mouth
            for i in range(agentsPerGame):
                if theGenePools[plyrIdxs[i]].played_genes: # THANK GOODNESS I thought I was gonna have to assemble that from scratch.
                    theGenePools[plyrIdxs[i]].count += 1
                    theGenePools[plyrIdxs[i]].absoluteFitness += ((pmetrics[i].avePop + pmetrics[i].endPop) / 2.0) # ok buddy
                    theGenePools[plyrIdxs[i]].relativeFitness += pmetrics[i].relPop # this at least makes sense


            pmetrics = None # free that up, thank you very much garbage collection.


        write_generational_results(theGenePools, popSize, gen, agentsPerGame)
        # LEBROOOON

        # now we gotta evolve the actual fetchers.
        theGenePools_old = theGenePools # switcherooni
        theGenePools = evolvePopulationPairs(theGenePools_old, popSize, numGeneGopies) # get the new ones
        theGenePools_old = None # clear out the old oners

        # # garbage collection. please ignore.
        # theGenePools_old = None
        # initialPopularites = None
        # iniitalRelativePopularities = None
        # plyrIdxs = None
        # agents = None

        # no extra players within the config file so we can probably just NOT do that

        # YAHOOO that should be it.

