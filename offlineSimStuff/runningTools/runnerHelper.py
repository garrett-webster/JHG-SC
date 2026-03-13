# this holds all the heavily used functions for post pure batch and for datacrunching better. as we work on those things, make updates here so they stay synced between the two.
from Server.SC_Bots.optimalHuman import OptimalHuman
from Server.social_choice_sim import Social_Choice_Sim
from Server.JHGManager import JHG_simulator
from Server.Engine.simulator import GameSimulator

import numpy as np
import os
import copy

from Server.OptionGenerators.generators import generator_factory

from Server.Engine.completeBots.geneagent3 import GeneAgent3
from offlineSimStuff.variousGraphingTools.completeVersions.completeGrapher import CompleteGrapher
from Server.Engine.completeBots.projectCat import ProjectCat
from Server.Engine.completeBots.improvedJakeCate import ImprovedJakeCat
from Server.Engine.completeBots.CantisFirst import CantisFirst

# from Server.SC_Bots.optimalHuman import OptimalHuman
from Server.Engine.completeBots.randomagent import RandomAgent

## TODO: remove the "total_order" from this call. should already be under the SC sim, if that makes sense.
def run_sc_stuff(sc_sim, jhg_sim_popularity, total_order, influence_matrix, curr_round, num_cycles, peep_constant):
    # sc_sim.set_rounds(curr_round) # don't set that here methinks, let it ride.
    possible_peeps, indexes = generate_peeps(total_order, jhg_sim_popularity, sc_sim, peep_constant)  # people who are needed to create the matrix
    if influence_matrix is not None:
        new_influence = influence_matrix
    else:
        new_influence = sc_sim.get_influence_matrix() # if there is no JHG influence, we are flying solo, leach off of own influence
    # should I make this, you know, an entirely different bot? having them in the same file feels wrong beuase they are doing differen things.
    current_options_matrix, peeps = sc_sim.let_others_create_options_matrix(possible_peeps.tolist(), curr_round, new_influence)  # actually creates the matrix
    # print("these are the peeps" , peeps)
    sc_sim.start_round((current_options_matrix, indexes))

    bot_votes = {}
    for cycle in range(num_cycles):
        bot_votes[cycle] = sc_sim.get_votes(bot_votes, curr_round, cycle, num_cycles, influence_matrix)
        sc_sim.record_votes(bot_votes[cycle], cycle)

    # make sure that this happens IMMEDIATELY afterward.
    winning_vote, round_results = sc_sim.return_win(bot_votes[num_cycles - 1])
    new_influence = np.array(sc_sim.get_influence_matrix()) # ACTUALLY UPDATE THE FETCHER
    sc_sim.save_results()
    return new_influence, winning_vote # takes our modified influence and makes sure to feed it back into the jhg sim so we get a cyclical affect.


def reconcile_influence(jhg_influence, sc_influence):
    # ok this fetcher uses convex recombination to put the two together and then uses the frobenius norm to decide on the magnitude to adjust back too. bars!
    # alpha = 0.5 # THIS iS JUST A STARTER VALUE, WILL LIKELY BE MADE INTO A GENE OR WHATEVER.
    alpha = 0.5 # THIS iS JUST A STARTER VALUE, WILL LIKELY BE MADE INTO A GENE OR WHATEVER.
    # Alpha of 0 is entirely JHG, alpha of 1 is entirely SC. I started with 0.5 but worry that that might have been too flattening.

    if sc_influence is None:
        print("something wrong :(")
        return jhg_influence

    sc_influence = np.array(sc_influence)
    jhg_influence = np.array(jhg_influence) # This shbould never get used but it couldn't hurt

    jhg_norm = np.linalg.norm(jhg_influence, 'fro')

    combined = (1 - alpha) * jhg_influence + alpha * sc_influence

    combined_norm = np.linalg.norm(combined, 'fro')
    if combined_norm == 0:
        return np.zeros_like(jhg_influence)

    rescaled = combined * (jhg_norm / combined_norm)
    return rescaled


def run_jhg_stuff(jhg_engine, curr_round, agents, num_players, current_jhg_sim):
    transactions = [0 for _ in range(num_players)]  # so this is how I replilcate it in python.
    T_prev = jhg_engine.get_transaction()

    for i in range(num_players):

        transactions[i] = agents[i].play_round(
            i,
            curr_round,
            T_prev[:,i],
            jhg_engine.get_popularity().tolist(),
            jhg_engine.get_influence(),
            jhg_engine.get_extra_data(i),
            # False
        )
    jhg_engine.play_round(transactions)  # thanks references


    current_jhg_sim.T = transactions
    new_popularity = current_jhg_sim.sim.get_popularity()
    avg_pop = sum(new_popularity) / current_jhg_sim.num_players
    current_jhg_sim.avg_pop_per_round.append(avg_pop)
    current_jhg_sim.game_popularities.append(new_popularity)

    # ok so now I have to return
    # the change in popularities,
    # return sc_sim.current_results, sc_sim.results_sums, new_influence  # so we have the change in utility and overall utility

    return jhg_engine.get_influence()  # return da influence matrix, the change in popularitry, and the new popularities.

# should be 0 for the pure SC environment, and 1 for the pure JHG environment. anythign in the middle is mixed.
def generate_peeps(total_order, popularity_array, sc_sim, peep_constant):
    total = sum(popularity_array) # use her here
    # this is easy bc this will always be positive
    normalized_popularity_array = [val / total for val in popularity_array]
    # THIS IS WORSE.
    utilities_array = sc_sim.results_sums
    global_shift = min(0, min(utilities_array))
    # shift everything over. subtract bc its either 0 or a negative number.
    utilities_array = [val - global_shift for val in utilities_array]
    total = sum(utilities_array) # yeah override this why not.
    normalized_utility_array = [val / total if total != 0 else 1 / len(total_order) for val in utilities_array]
    # new goal -- figure out how zip works
    overall_probability_array = []
    alpha = peep_constant
    for pop, util in zip(normalized_popularity_array, normalized_utility_array):
        new_val = alpha * pop + (1 - alpha) * util
        overall_probability_array.append(new_val)

    overall_probability_array = [(p + u) / 2 for p, u in zip(normalized_popularity_array, normalized_utility_array)]
    probabilities = np.array(overall_probability_array)
    new_world_order = np.array(total_order)
    # shoudl pull without replacement from total order using the overall probability array, gives 3 choies without replacement.
    new_peeps = np.random.choice(new_world_order, p=probabilities, size=3, replace=False)
    indexes = peeps_to_total_order(new_peeps, total_order)
    return new_peeps, indexes


def create_round_graphs(round_logger, curr_round, played_jhg, played_sc):
    complete_grapher = CompleteGrapher()
    complete_grapher.create_round_graphs_with_round_logger(round_logger, curr_round, played_jhg, played_sc)

def create_game_graphs(game_logger):
    complete_grapher = CompleteGrapher()
    complete_grapher.create_game_graphs_with_logger(game_logger)

def peeps_to_total_order(peeps, total_order):
    indexes = []
    for peep in peeps:
        indexes.append(total_order.index(peep)+1)
    return indexes


def create_sim(total_players, num_humans, total_order=None, enforce_majority=False):
    cycle = -1 # a negative cycle indicates to me that this is a test - that, or something is really really wrong.
    curr_round = -1
    num_causes = 3
    generator = generator_factory(2, total_players, 5, 10, -10, 3, None, None)
    sc_sim = Social_Choice_Sim(total_players, num_causes, num_humans, generator, cycle, curr_round, total_order, enforce_majority)
    return sc_sim

def create_jhg_sim(num_humans, num_players, total_order, jhg_bot_type, addAgents, new_agents, new_engine):
    jhg_sim = JHG_simulator(num_humans, num_players, total_order, bot_type=jhg_bot_type, agent_config=addAgents, start_game=False)
    jhg_sim.override_everything(new_engine, new_agents)
    return jhg_sim


def create_jhg_engine(num_players):
    poverty_line = 0

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

    jhg_engine = GameSimulator(game_params)
    return jhg_engine


def determine_rounds(jhg_rounds_per_sc_game_list):
    new_list = [] # WHEEE gotta start somewhere
    if jhg_rounds_per_sc_game_list[0] == "J" or jhg_rounds_per_sc_game_list[0] == "S":
        if jhg_rounds_per_sc_game_list[0] == "J":
            num_rounds = int(jhg_rounds_per_sc_game_list[-1]) # possibly one of the jankier lines that I have ever written but here we are
            for i in range(num_rounds):
                new_list.append(str(i) + "-")

        if jhg_rounds_per_sc_game_list[0] == "S":
            num_rounds = int(jhg_rounds_per_sc_game_list[-1])
            for i in range(num_rounds):
                new_list.append(str(i) + "*")


    else:
        # print("YOU DECIDED YOU WERE REMOVING SUPPORT FOR THIS UNTIL LATER. WRONG!")
        new_list = []
        current = 0  # Tracks number for "-" entries
        for instance in jhg_rounds_per_sc_game_list:
            for _ in range(instance):
                new_list.append(f"{current}-")
                current += 1
            new_list.append(f"{current - 1}*")  # Append the last "-" number with "*"

    return new_list



def create_total_order(total_players, num_humans):
    num_bots = total_players - num_humans
    total_order = []
    for bot in range(num_bots):
        total_order.append("B" + str(bot))
    for human in range(num_humans):
        total_order.append("P" + str(human))
    return total_order

def loadPopulationFromFile(popSize, num_gene_pools, agent_name):
    if ".csv" in agent_name:

        fnombre = "Kill me"
        try:
            file_name = os.path.join("Server", "Engine", "botGenerations") # creates standard file path. we then append to this.
            file_name = os.path.join(file_name, agent_name)

            my_path = os.path.dirname(os.path.abspath(__file__))
            my_path = os.path.abspath(os.path.join(my_path, "../../"))  # go up 2 levels and resolve path
            file_path = os.path.join(my_path, file_name)
            fnombre = file_path

            fp = open(fnombre, "r")

            # C:\Users\Sean Smith\Documents\GitHub\JHG - SC\Server\Engine\botGenerations\mixedJHGSelfPlay.csv

        except FileNotFoundError:
            try:
                fnombre = "../Server/Engine/gen_199.csv"
                fp = open(fnombre, "r")
            except FileNotFoundError:
                print(fnombre + " not found")
                quit()

        thePopulation = []

        for i in range(0,popSize): # so this is NOT random. oh FETCH.
            line = fp.readline()
            words = line.split(",")

            thePopulation.append(GeneAgent3(words[0], num_gene_pools))
            # thePopulation.append(BasicGeneAgent3(words[0], num_gene_pools))
            if len(words) == 1:
                print("what is going on here")
            thePopulation[i].count = float(words[1])
            # thePopulation[i].relativeFitness = float(words[2])
            # thePopulation[i].absoluteFitness = float(words[3][0])

        fp.close()
    else:
        thePopulation = []

    return thePopulation


def create_sc_agents(num_players, agent_name):
    if "random" in agent_name:
        new_bots = [RandomAgent(2) for i in range(num_players)]
    if "Optimal" in agent_name:
        new_bots = [OptimalHuman(i) for i in range(num_players)]
    # chromosome auto set, don't worry about it

    return new_bots



def create_agents(num_players, new_list, agent_name, forcedRandom, random_agents):
    popSize = 60
    num_gene_pools = 1

    if ".csv" in agent_name:
        theGenePools = loadPopulationFromFile(popSize, num_gene_pools, agent_name)  # this gets us our fetcher
    else:
        theGenePools = create_sc_agents(popSize, agent_name)

    initial_pops = [100 for _ in range(num_players)]

    plyrs = []

    # lets add some stochacisty to this


    if random_agents: # for the HCABs mostly.
        plyr_idxs = np.random.choice(np.arange(popSize), size=num_players, replace=False)

    else:
        plyr_idxs = np.arange(num_players)


    for i in range(0, num_players-len(new_list)):
        plyrs.append(theGenePools[plyr_idxs[i]])  # just add the first guys and go form there

    for i in new_list:
        if i == -1:
            plyrs.append(ImprovedJakeCat())
        if i == -2:
            plyrs.append(ProjectCat())
        if i == -3:
            plyrs.append(CantisFirst())


    agents = np.array(plyrs)
    players = [*agents]

    alpha_min, alpha_max = 0.20, 0.20
    beta_min, beta_max = 0.5, 1.0
    keep_min, keep_max = 0.95, 0.95
    give_min, give_max = 1.30, 1.30
    steal_min, steal_max = 1.6, 1.60

    num_players = len(players)

    poverty_line = 0

    game_params = {
        "num_players": num_players,
        "alpha": alpha_min,  # np.random.uniform(alpha_min, alpha_max),
        "beta": beta_min,  # np.random.uniform(beta_min, beta_max),
        "keep": keep_min,  # np.random.uniform(keep_min, keep_max),
        "give": give_min,  # np.random.uniform(give_min, give_max),
        "steal": steal_min,  # np.random.uniform(steal_min, steal_max),
        "poverty_line": poverty_line,
        "base_popularity": np.array(initial_pops)

    }

    for a in agents:
        a.setGameParams(game_params, forcedRandom)

    return agents


class RoundState:
    def __init__(self, round_type):
        self.pure_jhg = False
        self.pure_sc = False
        self.combined = False
        if round_type[0] == "S":
            self.pure_jhg = False
            self.pure_sc = True
            self.combined = False
        elif round_type[0] == "J":
            self.pure_jhg = True
            self.pure_sc = False
            self.combined = False
        else:
            self.pure_jhg = False
            self.pure_sc = False
            self.combined = True

    def return_round_state(self):
        return [self.pure_jhg, self.pure_sc, self.combined]

    def print(self):
        return str(self.return_round_state())

def get_file_names(agent_directory):
    files = os.listdir(agent_directory)
    files = [f for f in files if os.path.isfile(agent_directory+'/'+f)]
    return files



# most stripped down version of run trial. Just plays the thing, returns the new sims, and then what was played. simple as.
def run_trial(agents, sc_sim, jhg_sim, round_list, num_cycles, total_order, current_jhg_sim, peep_constant):
    group = ""  # get rid fo this at some point, IKD why its till here.
    sc_sim.set_group(group)
    played_sc = False
    played_jhg = False
    curr_sc_round = 0
    influence_matrix = None  # this should get overwritten pretty quick, but its there so there's no error.
    for list_index in (range(0, len(round_list))):  # fixed, we start at 0 now.

        sc_rounds = round_list[list_index][-1] == "*"
        jhg_rounds = round_list[list_index][-1] == "-"
        curr_round = int(round_list[list_index][:-1])  # useful, yes, but not quite the logger round

        # print("*****************************ROUND ", curr_round, "********************************")

        if jhg_rounds:
            influence_matrix = run_jhg_stuff(jhg_sim, curr_round, agents, len(agents), current_jhg_sim)
            played_jhg = True

        if sc_rounds:
            old_influence_matrix = copy.copy(influence_matrix)
            influence_matrix, winning_vote = run_sc_stuff(sc_sim, jhg_sim.get_popularity(), total_order,
                                                          influence_matrix, curr_round, num_cycles, peep_constant)
            sc_sim.set_rounds(curr_sc_round)  # ???
            curr_sc_round += 1
            played_sc = True

    return sc_sim, jhg_sim, played_sc, played_jhg