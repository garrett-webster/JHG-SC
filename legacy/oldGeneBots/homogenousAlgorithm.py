
from Server.Engine.engine import JHGEngine
from Server.JHGManager import JHG_simulator
from Server.Engine.completeBots.geneagent3 import GeneAgent3
from Server.Engine.completeBots.baseagent import AbstractAgent
# from Server.Engine.completeBots.projectCat import ProjectCat
from Server.Engine.completeBots.jakecat import JakeCAT
from Server.OptionGenerators.generators import generator_factory # i don't like him
from dataclasses import dataclass
import random
import csv # WHEEE. make sure this doesn't leak over the client or server otherwise I have to update the venv on the chromebooks.
import os
import math
import numpy as np

from Server.social_choice_sim import Social_Choice_Sim
from offlineSimStuff.runningTools.batch_tester_JHG_SC import determine_rounds
from legacy.oldGeneBots.geneticLogger import geneticLogger
from offlineSimStuff.variousGraphingTools.individualLoggers.gameLogger import GameLogger
from offlineSimStuff.variousGraphingTools.completeVersions.completeGrapher import CompleteGrapher


"""
based on the genetic algorihtm as given within the IJCAII repo. However, it tries to implement some of the chagnes as seen within the flutter algorithm for
homogenity, trying to be better about having the CAB agents defend against outside bad actors (READ: CATS). 
"""


@dataclass # because python doesn't support dedicated new stucts the way C++ does. I could have built a custom class, but this seemed lighterweight and better addapted.
class PopularityMetrics:
    avgUtility: float
    endUtility: float
    relUtility: float
    avgPopularity: float
    endPopularity: float
    relPopularity: float

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
    jhg_bot_type = 0  # doesn't really matter, will also be doing a bot override.
    cycle = -1
    curr_round = -1
    num_causes = 3
    scenario = ""
    chromosomes = ""
    allocation_bot_type = ""
    group = ""
    utility_per_player = 3
    alpha = 0.2  # double check these magical fetchers when you get the chance actually.
    beta = 0.5
    give = 1.3
    keep = 0.95
    steal = 1.6
    base_pop = 100
    poverty_line = povertyLine
    game_params = {
        "alpha": alpha,
        "beta": beta,
        "keep": keep,
        "give": steal,
        "steal": steal,
        "poverty_line": poverty_line,
    }
    generator = generator_factory(2, numPlayers, 5, -10, 10, 3, None, None)
    jhg_engine = JHGEngine(alpha, beta, give, keep, steal, numPlayers, base_pop, povertyLine)
    sc_sim = Social_Choice_Sim(numPlayers, num_causes, num_humans, generator, cycle, curr_round, chromosomes, scenario, group, total_order, allocation_bot_type, utility_per_player)
    return jhg_engine, sc_sim, total_order

def run_sc_gen_stuff(agents, jhg_engine, sc_sim, total_order, curr_sc_round, num_cycles, numPlayers, influence_matrix, real_sc_round):
    possible_peeps, indexes = generate_peeps(total_order, jhg_engine.get_popularity(), sc_sim)

    if influence_matrix is not None:
        new_influence = influence_matrix
    else:
        new_influence = sc_sim.get_influence_matrix()  # if there is no JHG influence, we are flying solo, leach off of own influence

    current_options_matrix, peeps = sc_sim.let_others_create_options_matrix(possible_peeps.tolist(),
                                                                            curr_sc_round, new_influence)  # actually creates the matrix
    sc_sim.start_round((current_options_matrix, indexes))
    bot_votes = {}
    extra_data = {
        i: {
            j: None for j in range(len(total_order))
        } for i in range(len(total_order))
    }
    index = len(sc_sim.I)

    for cycle in range(num_cycles):
        bot_votes[cycle] = {}
        if cycle == 0:
            votes_put_in = None
        else:
            votes_put_in = bot_votes[cycle - 1]
        for agent in range(numPlayers):
            recieved = sc_sim.reconcile_received(agent, votes_put_in)
            # the influence array is doing all sorts of silly things lately, and I am not sure why. I think we have lost track of SC round in here somewhere.
            bot_votes[cycle][agent] = (agents[agent].get_vote(agent, curr_sc_round, recieved, sc_sim.results_sums, np.array(influence_matrix), extra_data, current_options_matrix, False))
        sc_sim.record_votes(bot_votes[cycle], cycle) # important for logging individual games, can likely be disregarded here

    winning_vote, round_results = sc_sim.return_win(bot_votes[num_cycles - 1])  # we need this to run, even if we don't need the results HERE per se
    new_influence = np.array(sc_sim.get_influence_matrix())  # ACTUALLY UPDATE THE FETCHER

    sc_sim.most_recent_influence = new_influence
    sc_sim.num_rounds = real_sc_round

    # make sure that this happens IMMEDIATELY afterward.

    sc_sim.save_results()
    return sc_sim.current_results, sc_sim.results_sums, new_influence # so we have the change in utility and overall utility

def reconcile_received(self, agent, previous_votes):
    # if the game is just starting or the first round, we will have no room with which to think, thus 0's.
    solid_received = self.new_v[agent] if self.new_v is not None else [0 for _ in range(self.total_players)]  # this SHOULD? work better.
    # only problem - this completely fails to take into account previous cycles, which is odd. might need to save a new v per cycle and average it as we go.
    new_received = self.calculate_v_given_options_and_votes(self.current_options_matrix, previous_votes)[agent]
    # print("Here is the solid received ", solid_received, " and here is the new_received ", new_received)
    new_v = []
    for i in range(len(new_received)):
        new_v.append((solid_received[i] + new_received[i]) / 2) # make this part of the agent chromosome at some point, for right now its just there.
    # print("this is the new v ", new_v)
    return new_v


def run_jhg_gen_stuff(jhg_engine, curr_round, agents, num_players, current_jhg_sim):
    transactions = [0 for _ in range(num_players)]  # so this is how I replilcate it in python.
    T_prev = jhg_engine.get_transaction()
    extra_data = {
        i: {
            j: None for j in range(numPlayers)
        } for i in range(numPlayers)
    }

    for i in range(num_players):
        transactions[i] = agents[i].play_round(
            i,
            curr_round,
            T_prev[:,i],
            jhg_engine.get_popularity(),
            jhg_engine.get_influence(),
            extra_data,
            False
        )
    jhg_engine.apply_transaction(transactions)  # thanks references
    # print("here is the last player transaction ", transactions[-1])
    current_jhg_sim.T = transactions
    new_popularity = current_jhg_sim.sim.get_popularity()
    avg_pop = sum(new_popularity) / current_jhg_sim.num_players
    current_jhg_sim.avg_pop_per_round.append(avg_pop)
    current_jhg_sim.game_popularities.append(new_popularity)

    # ok so now I have to return
    # the change in popularities,
    # return sc_sim.current_results, sc_sim.results_sums, new_influence  # so we have the change in utility and overall utility

    return jhg_engine.get_influence()  # return da influence matrix, the change in popularitry, and the new popularities.


def playGame(agents, numPlayers, numRounds, gener, gamer, initialPopularities, povertyLine, forcedRandom, rounds_list, print_game):
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


    # received = [0.0 for _ in range(numPlayers)] # C++ really needs to allocate memeory before hadn
    # transactions = [0 for _ in range(numPlayers)] # so this is how I replilcate it in python.
    #
    # for i in range(numPlayers): # I think this makes the fetcher square?
    #     transactions[i] = [0 for _ in range(numPlayers)]

    # they hard lean into initalizing arrays of type class and then filling them later, which is weird to replicate in python
    pmetrics = [PopularityMetrics(avgUtility=0, endUtility=0, relUtility=0, avgPopularity=0, endPopularity=0, relPopularity=0) for _ in range(numPlayers)]
    # actually I can skip the next step because its just setting it up, yay for python one line loops.

    if print_game:
        print("Expect a game to be printed your honor")

    # make the new sims, and then override the bots that they have in them.
    ## TODO: make a reset function that allows us to not have to make new sims everytime and lets us recycle them.
    # the SC sim is especially heavy in terms of initalization.
    jhg_engine, sc_sim, total_order = make_sims()
    sc_sim.bot_ovveride(agents[:numPlayers]) # this should put us all on the same page
    sc_sim.set_group("")

    bot_types = [0 for _ in range(numPlayers - num_kitties)]
    for i in range(num_kitties):
        bot_types.append(-1)

    game_logger = GameLogger(numPlayers, bot_types)
    new_jhg_sim = create_jhg_sim(0, numPlayers, total_order, 2, bot_types, "", agents, jhg_engine)
    game_logger.resetup(new_jhg_sim, sc_sim)

    influence_matrix = np.array([[0 for _ in range(numPlayers)]for _ in range(numPlayers)]) # initalization for pure sc purposes
    curr_sc_round = 0
    for list_index in range(0, len(rounds_list)):

        sc_rounds = rounds_list[list_index][-1] == "*"
        jhg_rounds = rounds_list[list_index][-1] == "-"

        curr_round = int(rounds_list[list_index][:-1])  # useful, yes, but not quite the logger round
        #curr_logger_round = gamer + offset  # this way the logger is logging it continously, but the sims don't interpret it that way.
        if jhg_rounds:
            # influence_matrix, changePopularity, overallPopularity = run_jhg_gen_stuff(jhg_engine, curr_round, agents, numPlayers)
            influence_matrix = run_jhg_gen_stuff(jhg_engine, curr_round, agents, numPlayers, new_jhg_sim)

            for i in range(numPlayers):
                pmetrics[i].avgPopularity += float(jhg_engine.P[jhg_engine.t][i] / numRounds)
                pmetrics[i].endPopularity = float(jhg_engine.P[jhg_engine.t][i])

        if sc_rounds:
            changeUtility, overallUtility, influence_matrix = run_sc_gen_stuff(agents, jhg_engine, sc_sim, total_order, curr_round, num_cycles, numPlayers, influence_matrix, curr_sc_round)
            curr_sc_round += 1

            for i in range(numPlayers):
                pmetrics[i].avgUtility += changeUtility[i]
                pmetrics[i].endUtility = overallUtility[i]


    if print_game:
        game_logger.save_game(False, True)
        create_game_graphs(game_logger)

    # print("These are the final utilities ", sc_sim.results_sums, " and these are the final popularities ", (jhg_engine.get_popularity()).tolist())
    avg_non_cat_pop, avg_non_cat_util = calculate_average_stats(jhg_engine, sc_sim)

    return pmetrics, avg_non_cat_pop, avg_non_cat_util


def create_jhg_sim(num_humans, num_players, total_order, tokens_per_player, jhg_bot_type, addAgents, new_agents, new_engine):
    jhg_sim = JHG_simulator(num_humans, num_players, total_order, tokens_per_player, jhg_bot_type, agent_config=addAgents, start_game=False)
    jhg_sim.override_everything(new_engine, new_agents)
    return jhg_sim


def create_game_graphs(game_logger):
    complete_grapher = CompleteGrapher()
    complete_grapher.create_game_graphs_with_logger(game_logger)


def calculate_average_stats(jhg_engine, sc_sim):

    popularities = (jhg_engine.get_popularity()).tolist()
    num_kitties = 2 # just trust me
    non_cats = 8
    cumulative_cat_score = sum(popularities[non_cats:])
    cumulative_non_cat_score = sum(popularities)- cumulative_cat_score
    avg_cat_pop = cumulative_cat_score / num_kitties
    avg_non_cat_pop = cumulative_non_cat_score / non_cats
    # print('here is the average cat / added agent ', avg_cat_pop, " and here is the average non cat utility ", avg_non_cat_pop)




    utilities = sc_sim.results_sums
    cumulative_cat_score = sum(utilities[non_cats:])
    cumulative_non_cat_score = sum(utilities)   - cumulative_cat_score
    avg_cat_util = cumulative_cat_score / num_kitties
    avg_non_cat_util = cumulative_non_cat_score / non_cats
    # print('here is the average cat / added agent popualrity ', avg_cat_util, " and here is the average non cat popularity ", avg_non_cat_util)

    return avg_cat_pop, avg_cat_util


# this might POOP poop the bed, pretty sure it was written with managers in mind rather than the sims, so we shall see.
def generate_peeps(total_order, jhg_pops, sc_sim):
    popularity_array = jhg_pops  # huh
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
    output_dir = os.path.join(script_dir, "normalCats2", "theGenerations")
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    # Construct the filename path
    filename = os.path.join(output_dir, f"gen_{gen}.csv")

    # Write CSV
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        # get rid of this STUPID and STINKY header.
        #writer.writerow(["Genes", "GamesPlayed", "RelativeUtility", "AbsoluteUtility"])  # optional header
        for agent in sorted_agents:
            writer.writerow([
                agent.getString(),
                agent.count,
                round(agent.relativeFitness, 4),
                round(agent.absoluteFitness, 4),
                round(agent.relativePopularity, 4),
                round(agent.absolutePopularity, 4),
            ])

    avg_fitness = sum(agent.absoluteFitness for agent in theGenePools) / popSize
    avg_popularity = sum(agent.absolutePopularity for agent in theGenePools) / popSize
    print(f"Average utility in generation {gen}: {avg_fitness:.4f} Average Popularity: {avg_popularity:.4f}")


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
    theGenePool = [None] * popSize
    gene_keys = list(theGenePool_prev[0].genes_long[0].keys())
    minKeepIndex = 12

    for i in range(popSize):
        ind1 = selectByFitness(theGenePool_prev, popSize, True) if i < (popSize / 5) else selectByFitness(theGenePool_prev, popSize, False)
        ind2 = selectByFitness(theGenePool_prev, popSize, False)

        gene_values = []
        for gene, key in enumerate(gene_keys):
            if gene % minKeepIndex == 0:
                gene_values.append("0")
            else:
                gene1 = theGenePool_prev[ind1].genes_long[0][key]
                gene2 = theGenePool_prev[ind2].genes_long[0][key]
                selected_gene = mutateIt(gene1) if random.randint(0,1) == 0 else mutateIt(gene2)
                gene_values.append(str(selected_gene))
            geneStr = "gene_" + "_".join(gene_values)
            theGenePool[i] = GeneAgent3(geneStr, 1)

    return theGenePool

# take in our population and put the best fetchers at the very top and the worst fetchers at the very bottom.
# only problem is, what is
def selectByFitness(thePopulation, popSize, _rank):
    # get the magnitude in one go
    total_weight = sum(
        (p.relativePopularity if _rank else p.absolutePopularity)
        for p in thePopulation
    )

    # Fallback: if all weights are zero, pick random agent
    if total_weight <= 0.0:
        return random.randint(0, popSize - 1)

    # generate a random threshold
    pick = random.random() * total_weight

    cumulative = 0.0
    for i, p in enumerate(thePopulation):
        weight = p.relativePopularity if _rank else p.absolutePopularity
        cumulative += weight
        if pick <= cumulative: # how to decide where to return
            return i

    # Fallback for rounding edge cases
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

# this one has some modifications to it, namely
# less players, and shorter rounds.
# however, it is still doing 100 games per gen
# I hope this gives me a better prototype and a means to try and reason through this
# if we see progress here, we will up it back up and run it for longer.


if __name__ == "__main__":
    ## -- INIT STUFF , didn't feel like using the command line everytime, thats on me. heres' the init and all explanation -- ##
    #// - run the code: ./jhgsim(0) evolve(1) ../Results/theGenerations(2) 100(3) 3(4) 0(5) 100(6) 100(7) 10(8) 30(9) 0(10) basicConfig(11) varied(12)
    # (fileName) (commandArgument) (Folder(2)), (numGeneCopies(3)), (startIndex(4)), (numGenes(5)), (gamesPerGen(6)), (agentsPerGame(7)), roundsPerGame(8), povertyLine(9)
    # using the default arguments from the ijacai documentation.
    # 0 -- executable (doesn't change)
    # 1 -- code directive to evolve population (doesn't change)
    theFolder = "SomeFolder" # folder where trained parameters of cab agents are stored.
    popSize = 100 # number of agnets in the gene pool (use 100 here)
    numGeneGopies = 1 # numbers of sets of genes (3 was the number used in the paper)
    # 1 should ALSO work fine, I should stress.

    startIndex = 0 # generation to start training (0 to start form scratch)
    num_gens = 300 # generation to end traning trains up to 99
    games_per_gen = popSize # agents from the gene pool are selected at random, 100 times.
    # BIG NOTICE --> THIS NEEDS TO BE EQUAL TO GAMES_PER_GEN.
    agentsPerGame = 8 # number of agents per game
    # roundsPerGame = 30 # number fo rounds per game
    povertyLine = 0 # see SM-1
    initPops = "equal" # starts eveyrone at different initial popularities when training.
    num_humans = 0 # we discriminate in this fetcher
    num_kitties = 2
    current_logger = geneticLogger()

    configured_players = []
    for i in range(num_kitties):
        configured_players.append(JakeCAT())

    # should initialize this fetcher
    theGenePools = [GeneAgent3("", numGeneGopies) for _ in range(popSize)] # don't let this be empty
    # when the agents are handed an empty string, they go ahead and randomize it for me. don't know why thats changed between the two.


    numPlayers = agentsPerGame + len(configured_players) # could put gocnifutred players.size but that si currently empty and I couldn't care less.
    # maxPlayers = numPlayers + len(configured_players)

    plyrIdxs = [0 for _ in range(numPlayers)]
    possible_init_pops = ["equal", "random", "step", "power", "highlow"]
    # initUtilities = [0.0 for _ in range(numPlayers)]
    # initRelativeUtilities = [0.0 for _ in range(numPlayers)]
    agents = [AbstractAgent() for _ in range(popSize)]  # the fetchers we will be training

    jhg_games_per_round = ["J", 30]
    rounds_list = determine_rounds(jhg_games_per_round)
    mxPlayers = numPlayers

    for gen in range(num_gens): # however many generations we want
        list_non_cat_pops = []
        list_non_cat_util = []
        game_to_print = random.randint(0, games_per_gen)
        # game_to_print = 1 # just so its fairly early
        # print("this is the game we wnat to print ", game_to_print)
        for game in range(games_per_gen): # however many games we want per generation
            print_game = False
            if game == game_to_print:
                print_game = True
            # print_game = True

            # time to pick an individual frfom the gene poosl
            for i in range(agentsPerGame):
                plyrIdxs[i] = game # hope for the best IG.
                agents[i] = theGenePools[plyrIdxs[i]] # YIPEEE

            # not adding in the configured players yet, leave that alone for now.
            numPlayers = agentsPerGame
            for i in range(agentsPerGame, mxPlayers, 1):
                plyrIdxs[numPlayers] = popSize + i
                agents[numPlayers] = configured_players[i-agentsPerGame]
                numPlayers += 1

            if initPops == "varied":
                sel = random.randint(0, 4)
            else:
                sel = 0
            # this should be all 10's after the first run
            # should also point out that it never gets used -- wanted for models with different starting points.
            # not currently implemented and its not SUPER interesting to me.
            # initUtilities = definteInitialUtility(possible_init_pops[sel], numPlayers, initUtilities)
            initUtilities = [10 for _ in range(numPlayers)]
            initRelativeUtilities = [0 for _ in range(numPlayers)] # just to get something down.

            s = 0
            for i in range(numPlayers):
                s += initUtilities[i]

            # pretty sure this just normalizes it AGAIN in case we missed it the first time.
            for i in range(numPlayers):
                initRelativeUtilities[i] = initUtilities[i]/s

            if len(jhg_games_per_round) == 2: # pure operations
                num_rounds = jhg_games_per_round[1]
            else:
                num_rounds = sum(jhg_games_per_round)

            pmetrics, non_cat_pops, non_cat_util = playGame(agents, numPlayers, num_rounds, gen, game, initUtilities, povertyLine, False, rounds_list, print_game)
            list_non_cat_pops.append(non_cat_pops)
            list_non_cat_util.append(non_cat_util)

            # now we gotta calcualte relative popularity


            # TEMP ripping this our for PURE sc purposes. Uncomment it later.
            s = 0.0
            # t = 0.0
            for i in range(numPlayers):
                s += pmetrics[i].avgUtility
                # t += pmetrics[i].avgPopularity
            if s != 0.0:
                for i in range(numPlayers):
                    pmetrics[i].relUtility = pmetrics[i].avgUtility / s
                    # pmetrics[i].relPopularity = pmetrics[i].avgPopularity / t

            # we gotta update fitness - fitness whole pizza in they mouth
            for i in range(agentsPerGame):
                if theGenePools[plyrIdxs[i]].played_genes: # THANK GOODNESS I thought I was gonna have to assemble that from scratch.
                    theGenePools[plyrIdxs[i]].count += 1
                    theGenePools[plyrIdxs[i]].absolutePopularity += ((pmetrics[i].avgPopularity + pmetrics[i].endPopularity) / 2.0)
                    theGenePools[plyrIdxs[i]].relativePopularity += pmetrics[i].relPopularity # this also appears to make sense.
                    # theGenePools[plyrIdxs[i]].absoluteFitness += ((pmetrics[i].avgUtility + pmetrics[i].endUtility) / 2.0) # ok buddy
                    # theGenePools[plyrIdxs[i]].relativeFitness += pmetrics[i].relUtility # this at least makes sense

        print("this is the gen it thinks it is ", gen)
        average_pops = sum(list_non_cat_pops) / len(list_non_cat_pops)
        # average_util = sum(list_non_cat_util) / len(list_non_cat_util)
        # print("Average Utility: ", average_util, " of the cats ")#, " Average Pops: ", average_pops, " of the CATS")
        print(" Average Pops: ", average_pops, " of the CATS")

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
    configured_agents = None # more garbage collection


    # no extra players within the config file so we can probably just NOT do that

    # YAHOOO that should be it.

