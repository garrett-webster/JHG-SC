from Server.Engine.completeBots.geneagent3 import GeneAgent3
from Server.Engine.completeBots.baseagent import AbstractAgent
from Server.OptionGenerators.generators import generator_factory # i don't like him
from dataclasses import dataclass
import random
import csv # WHEEE. make sure this doesn't leak over the client or server otherwise I have to update the venv on the chromebooks.
import os
import math
import numpy as np
from tqdm import tqdm

from Server.social_choice_sim import Social_Choice_Sim
from offlineSimStuff.runningTools.batch_tester_JHG_SC import determine_rounds
from legacy.oldGeneBots.geneticLogger import geneticLogger



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
    avgUtility: float
    endUtility: float
    relUtility: float

# ok so for our purposes this is almost always going to be 100. there are other things we CAN do but we are most interested in the initial 100 testbed.
def definteInitialUtility(initPopType, numPlayers, initialPopularities):
    # see its not gonna tell you this but you are going to need to return initial Popularities here
    basePop = 10.0
    if (initPopType == "random"):
        for i in range(numPlayers):
            initialPopularities[i] = (random.randint(0, 19)) + 1.0
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
            initialPopularities[i] = 1.0 + random.randint(0, 5) + 15
        for i in range(int(math.ceil(numPlayers / 2)), numPlayers):
            initialPopularities[i] = 1.0 + random.randint(0, 5)
        initialPopularities = shuffle(initialPopularities, numPlayers)
    else:
        #print("don't udnerstand input, going with equal ")
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

# this is the one we have to absolutely massacre to make sure this works the way that we want it to.

def make_sims():
    total_order = create_total_order(0, numPlayers)
    cycle = -1
    curr_round = -1
    num_causes = 3
    scenario = ""
    chromosomes = ""
    allocation_bot_type = ""
    group = ""
    utility_per_player = 3
    generator = generator_factory(2, numPlayers, 5, -10, 10, 3, None, None)
    sc_sim = Social_Choice_Sim(numPlayers, num_causes, 0, generator, cycle, curr_round, chromosomes, scenario, group,
                               total_order, allocation_bot_type, utility_per_player)
    return sc_sim, total_order

def run_sc_gen_stuff(agents, sc_sim, total_order, curr_sc_round, num_cycles, numPlayers):
    possible_peeps, indexes = generate_peeps(total_order, sc_sim)
    current_options_matrix, peeps = sc_sim.let_others_create_options_matrix(possible_peeps.tolist(),
                                                                            curr_sc_round, sc_sim.get_influence_matrix())  # actually creates the matrix
    sc_sim.start_round((current_options_matrix, indexes))
    bot_votes = {}
    extra_data = {
        i: {
            j: None for j in range(len(total_order))
        } for i in range(len(total_order))
    }
    for cycle in range(num_cycles):
        bot_votes[cycle] = {}
        if cycle == 0:
            prev_votes = [0 for _ in range(len(total_order))]
        else:
            prev_votes = bot_votes[cycle-1]

        for agent in range(numPlayers):
            received = reconcile_received(sc_sim, agent, prev_votes) # use all bot votes here
            # the influence array is doing all sorts of silly things lately, and I am not sure why. I think we have lost track of SC round in here somewhere.
            bot_votes[cycle][agent] = (agents[agent].get_vote(agent, curr_sc_round, received, sc_sim.results_sums, np.array(sc_sim.I[curr_sc_round]), extra_data, current_options_matrix))
        sc_sim.record_votes(bot_votes[cycle], cycle) # important for logging individual games, can likely be disregarded here

    # make sure that this happens IMMEDIATELY afterward.
    winning_vote, round_results = sc_sim.return_win(bot_votes[num_cycles - 1])  # we need this to run, even if we don't need the results HERE per se
    sc_sim.save_results()
    # ok so what do I actually
    # what doe I need to
    return sc_sim.current_results, sc_sim.results_sums # so we have the change in utility and overall utility

# not a lot going on here - we simply take in the most recent votes,
def reconcile_received(self, agent, previous_votes):
    # if the game is just starting or the first round, we will have no room with which to think, thus 0's.
    solid_received = self.new_v[agent] if self.new_v is not None else [0 for _ in range( self.total_players)]  # this SHOULD? work better.
    # only problem - this completely fails to take into account previous cycles, which is odd. might need to save a new v per cycle and average it as we go.
    new_received = self.calculate_v_given_options_and_votes(self.current_options_matrix, previous_votes)[agent]
    # print("Here is the solid received ", solid_received, " and here is the new_received ", new_received)
    new_v = []
    for i in range(len(new_received)):
        new_v.append((solid_received[i] + new_received[
            i]) / 2)  # make this part of the agent chromosome at some point, for right now its just there.
    # print("this is the new v ", new_v)
    return new_v



def run_jhg_gen_stuff(jhg_engine, curr_round, agents, numPlayers):
    received = [0.0 for _ in range(numPlayers)]  # C++ really needs to allocate memeory before hadn
    transactions = [0 for _ in range(numPlayers)]  # so this is how I replilcate it in python.

    for i in range(numPlayers):
        for j in range(numPlayers):
            received[j] = np.array(jhg_engine.T[curr_round][j][i])
        transactions[i] = agents[i].play_round(i, curr_round, received, jhg_engine.P[curr_round], jhg_engine.I[curr_round], transactions[i])
    jhg_engine.apply_transaction(transactions) # thanks references

def playGame(agents, numPlayers, numRounds, gener, gamer, initialPopularities, povertyLine, forcedRandom, rounds_list):
    # for this one, reference defs.h in the C++ code. most of these are hard coded into the engine and this is just tranfering them over.
    # they might get set to different values in the engine, but i wan this engine to be consistent with other engines.
    # so for now just accept the magic numbers and we will move on with our day
    num_cycles = 3
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


    received = [0.0 for _ in range(numPlayers)] # C++ really needs to allocate memeory before hadn
    transactions = [0 for _ in range(numPlayers)] # so this is how I replilcate it in python.

    for i in range(numPlayers): # I think this makes the fetcher square?
        transactions[i] = [0 for _ in range(numPlayers)]

    # they hard lean into initalizing arrays of type class and then filling them later, which is weird to replicate in python
    pmetrics = [PopularityMetrics(avgUtility=0, endUtility=0, relUtility=0) for _ in range(numPlayers)]
    # actually I can skip the next step because its just setting it up, yay for python one line loops.


    # make the new sims, and then override the bots that they have in them.
    ## TODO: make a reset function that allows us to not have to make new sims everytime and lets us recycle them.
    # the SC sim is especially heavy in terms of initalization.
    sc_sim, total_order = make_sims() # just have em make they own bots
    sc_sim.set_group("")
    played_sc = False
    played_jhg = False
    influence_matrix = None
    curr_sc_round = 0
    for list_index in range(0, len(rounds_list)):

        sc_rounds = rounds_list[list_index][-1] == "*"
        jhg_rounds = rounds_list[list_index][-1] == "-"
        curr_round = int(rounds_list[list_index][:-1])  # yeah something like that

        changeUtility, overallUtility = run_sc_gen_stuff(agents, sc_sim, total_order, curr_sc_round, num_cycles, numPlayers)
        curr_sc_round += 1

        for i in range(numPlayers):
            pmetrics[i].avgUtility += changeUtility[i]
            pmetrics[i].endUtility = overallUtility[i]

    return pmetrics # returns out data type

# this might POOP poop the bed, pretty sure it was written with managers in mind rather than the sims, so we shall see.
def generate_peeps(total_order, sc_sim):
    popularity_array = [100 for _ in range(len(total_order))]  # huh
    total = sum(popularity_array)
    # this is easy bc this will always be positive
    normalized_popularity_array = [val / total for val in popularity_array]
    # THIS IS WORSE.
    utilities_array = sc_sim.results_sums
    global_shift = min(0, min(utilities_array))
    # shift everything over. subtract bc its either 0 or a negative number.
    utilities_array = [val - global_shift for val in utilities_array]
    total = sum(utilities_array)  # yeah override this why not.
    normalized_utility_array = [val / total if total != 0 else 1 / len(total_order) for val in utilities_array]
    # new goal -- figure out how zip works
    overall_probability_array = [(p + u) / 2 for p, u in zip(normalized_popularity_array, normalized_utility_array)]
    probabilities = np.array(overall_probability_array)
    new_world_order = np.array(total_order)
    # shoudl pull without replacement from total order using the overall probability array, gives 3 choies without replacement.
    new_peeps = np.random.choice(new_world_order, p=probabilities, size=3, replace=False)
    indexes = peeps_to_total_order(new_peeps, total_order)
    return new_peeps, indexes

def peeps_to_total_order(peeps, total_order):
    indexes = []
    for peep in peeps:
        indexes.append(total_order.index(peep)+1)
    return indexes

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

    # Get the absolute path to the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the full output directory path
    output_dir = os.path.join(script_dir, "SCResults", "theGenerations")
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    # Construct the filename path
    filename = os.path.join(output_dir, f"gen_{gen}.csv")
    print("this is where it is supposedly writing ", filename)

    # Write CSV
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Genes", "GamesPlayed", "RelativeUtility", "AbsoluteUtility"])  # optional header
        for agent in sorted_agents:
            writer.writerow([
                agent.getString(),
                agent.count,
                round(agent.relativeFitness, 4),
                round(agent.absoluteFitness, 4)
            ])

    avg_fitness = sum(agent.absoluteFitness for agent in theGenePools) / popSize
    print(f"Average utility in generation {gen}: {avg_fitness:.4f}")


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
# only problem is, what is
def selectByFitness(thePopulation, popSize, _rank):
    mag = 0.0
    for i in range(popSize):
        if (_rank):
            mag += thePopulation[i].relativeFitness
        else:
            mag += thePopulation[i].absoluteFitness
    num = random.random()  # Returns float in [0.0, 1.0)
    if mag == 0: # if there is nothing going on, just uhh return a random number.
        return random.randint(0, popSize-1)
    sum = 0.0
    for i in range(popSize):
        if (_rank):
            sum += thePopulation[i].relativeFitness / mag
        else:
            sum += thePopulation[i].absoluteFitness / mag

        if num <= sum:
            return i

    #print("uh no select, whatever happened ", num, " ", sum)
    # exit(1)

    return popSize - 1

# once again, garbage collection in python is really nice.
def deleteGenePool(theGenePools, popSize):
    theGenePools = None
    return theGenePools


def create_total_order(total_players, num_humans):
    total_order = []
    num_bots = total_players - num_humans
    total_order = []
    for bot in range(num_bots):
        total_order.append("B" + str(bot))
    for human in range(num_humans):
        total_order.append("P" + str(human))
    return total_order


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
    num_gens = 200 # generation to end traning trains up to 99
    games_per_gen = 10 # agents from the gene pool are selected at random, 100 times.
    agentsPerGame = 10 # number of agents per game
    roundsPerGame = 10 # number fo rounds per game
    povertyLine = 0 # see SM-1
    configFile = "basicConfig" # trains with just cab agents, no assasains.
    initPops = "varied" # starts eveyrone at different initial popularities when training.
    tokens_per_player = 2 # probably best if I just reduce this back to whatever. (Added by me just in case we wanted to be silly)
    num_humans = 0 # we discriminate in this fetcher
    current_logger = geneticLogger()

    # should initialize this fetcher
    theGenePools = [GeneAgent3("", numGeneGopies, tokens_per_player) for _ in range(popSize)] # don't let this be empty

    numPlayers = agentsPerGame + 0 # could put gocnifutred players.size but that si currently empty and I couldn't care less.
    maxPlayers = numPlayers

    plyrIdxs = [0 for _ in range(numPlayers)]
    possible_init_pops = ["equal", "random", "step", "power", "highlow"]
    initUtilities = [0.0 for _ in range(numPlayers)]
    initRelativeUtilities = [0.0 for _ in range(numPlayers)]
    agents = [AbstractAgent() for _ in range(popSize)]  # the fetchers we will be training

    # the nomral way to handle this is 3,4,4,4 etc where thats the number of jhg games per sc game
    # however, you can specify a certain number of rounds of pure by speciying "S,20" or "J,20" both of
    # which will give you either 20 sc games or 20 jhg games, respectively.
    jhg_games_per_round = ["S", 6] # just give me an easy place to start.
    rounds_list = determine_rounds(jhg_games_per_round)

    for gen in tqdm(range(num_gens)): # however many generations we want
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
            # this should be all 10's after the first run
            initUtilities = definteInitialUtility(possible_init_pops[sel], numPlayers, initUtilities)

            s = 0
            for i in range(numPlayers):
                s += initUtilities[i]

            # pretty sure this just normalizes it AGAIN in case we missed it the first time.
            for i in range(numPlayers):
                initRelativeUtilities[i] = initUtilities[i]/s

            pmetrics = playGame(agents, numPlayers, roundsPerGame, gen, game, initUtilities, povertyLine, False, rounds_list)

            # now we gotta calcualte relative popularity

            s = 0.0
            for i in range(numPlayers):
                s += pmetrics[i].avgUtility
            if s != 0.0:
                for i in range(numPlayers):
                    pmetrics[i].relUtility = pmetrics[i].avgUtility / s

            # print some stuff to the terminal for the purposes of understanding other stuf.f
            # print("Indicies: ")
            # for i in range(numPlayers):
            #     print("i, ", plyrIdxs[i])
            #
            # print("\n")
            # print("averageUtility :")
            # for i in range(numPlayers):
            #     print(f"{pmetrics[i].avgUtility}.2")
            # print("\n")
            # print("\n")
            #
            # print("relUtility: ")
            # for i in range(numPlayers):
            #     print(f"{pmetrics[i].relUtility}.2")
            #
            # print("\n")
            #print("Average Utility ", s / agentsPerGame)


            # we gotta update fitness - fitness whole pizza in they mouth
            for i in range(agentsPerGame):
                if theGenePools[plyrIdxs[i]].played_genes: # THANK GOODNESS I thought I was gonna have to assemble that from scratch.
                    theGenePools[plyrIdxs[i]].count += 1
                    theGenePools[plyrIdxs[i]].absoluteFitness += ((pmetrics[i].avgUtility + pmetrics[i].endUtility) / 2.0) # ok buddy
                    theGenePools[plyrIdxs[i]].relativeFitness += pmetrics[i].relUtility # this at least makes sense

        print("this is the gen it thinks it is ", gen)

        write_generational_results(theGenePools, popSize, gen, agentsPerGame)

        # LEBROOOON

        # now we gotta evolve the actual fetchers.
        theGenePools_old = theGenePools # switcherooni
        theGenePools = evolvePopulationPairs(theGenePools_old, popSize, numGeneGopies) # get the new ones
        theGenePools_old = None # clear out the old oners

    # garbage collection. please ignore.
    theGenePools_old = None
    initialPopularites = None
    iniitalRelativePopularities = None
    plyrIdxs = None
    agents = None

    # no extra players within the config file so we can probably just NOT do that

    # YAHOOO that should be it.

