# refer to "main.py" in ../ for more information
import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from Server.Engine.completeBots.geneagent3 import GeneAgent3
# from Server.Engine.completeBots.basicGeneAgent3 import BasicGeneAgent3
from Server.Engine.completeBots.humanagent import HumanAgent
from Server.Engine.completeBots.socialwelfaragent import SocialWelfareAgent
from Server.Engine.completeBots.randomagent import RandomAgent
from Server.Engine.simulator import GameSimulator
from Server.Engine.completeBots.projectCat import ProjectCat
from Server.Engine.completeBots.completeSocialWelfare import SocialWelfare
from Server.Engine.completeBots.antiCat import AntiCat

import numpy as np
import random


np.set_printoptions(precision=2, suppress=True)

class JHG_simulator():
    def __init__(self, num_human_players, num_players, total_order, tokens_per_player=2, bot_type=0, start_game=True, agent_config=""):
        self.num_players = num_players
        self.total_order = total_order
        self.sim = None
        self.players = None
        # went ahead and gave this a default. the currently trained agents have this baked into them that they need to have 2 tokens per player, curious in expanding that.
        if start_game:
            self.start_game(num_human_players, num_players, tokens_per_player, bot_type, agent_config)
        else:
            self.create_sim(num_human_players)
        self.T = None
        self.avg_pop_per_round = [100]
        self.game_popularities = [[100] * num_players]


    # just sets us up a sim, quick and dirty like
    def create_sim(self, num_players):
        poverty_line = 0
        init_pop = 100

        initial_pops = self.define_initial_pops(init_pop, num_players)

        alpha_min, alpha_max = 0.20, 0.20
        beta_min, beta_max = 0.5, 1.0
        keep_min, keep_max = 0.95, 0.95
        give_min, give_max = 1.30, 1.30
        steal_min, steal_max = 1.6, 1.60

        num_players = num_players

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

        self.sim = GameSimulator(
            game_params)  # sets up our sim object - might need to make this global so we can grab it wherever we need it.
        self.T = np.array([[0.0 for _ in range(num_players)] for _ in range(num_players)])


    def override_everything(self, new_engine, new_agnets):
        self.sim = new_engine
        self.players = new_agnets

    def start_game(self, num_human_players, num_players, tokens_per_player, bot_type, agent_config):
        init_pop = "equal"

        numAgents = num_players - num_human_players
        configured_players = []
        if agent_config != "":
            fp = open(agent_config, "r")
            for line in fp:
                if line.startswith("Kitty"):
                    configured_players.append(ProjectCat())
                if line.startswith("SocialWelfare"):
                    configured_players.append(SocialWelfare())


        popSize = 40  # ??? I think? based on the command line arguemnts
        player_idxs = list(np.arange(0, numAgents-len(configured_players)))  # where numAgents is the number of actual agents, not players.

        for _ in range(num_human_players):
            configured_players.append(HumanAgent())


        for i in range(0, len(configured_players)):
            player_idxs = np.append(player_idxs, popSize + i)


        theFolder = "Server/Engine/botGenerations"
        theGen = 199
        num_gene_copies = 3 # lets just try this super quick.


        # should be formatted appropraitely?
        theGenePools = self.create_pools(popSize, theFolder, theGen, num_gene_copies, tokens_per_player, bot_type)

        plyrs = []
        for i in range(0, len(player_idxs)): # so here's the thing - I have 0! clue on how this works. I'mma try somethihgn stupid ig.
            if player_idxs[i] >= popSize:
                plyrs.append(configured_players[int(player_idxs[i] - popSize)])
            else:
                plyrs.append(theGenePools[player_idxs[i]])

        plyrs = self.reorder_agents(plyrs) # reorder them so we like them better.

        players = np.array(plyrs)
        self.players = players
        agents = list(players)

        initial_pops = self.define_initial_pops(init_pop, len(player_idxs))
        poverty_line = 0
        forcedRandom = False

        players = [
            *agents
        ]

        alpha_min, alpha_max = 0.20, 0.20
        beta_min, beta_max = 0.5, 1.0
        keep_min, keep_max = 0.95, 0.95
        give_min, give_max = 1.30, 1.30
        steal_min, steal_max = 1.6, 1.60

        num_players = len(players)

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

        for a in agents:  # sets the game params for all users.
            a.setGameParams(game_params, forcedRandom)

        self.sim = GameSimulator(
            game_params)  # sets up our sim object - might need to make this global so we can grab it wherever we need it.



    def reorder_agents(self, plyrs):
        bots = [a for a in plyrs if a.whoami != "Human"]
        players = [a for a in plyrs if a.whoami == "Human"]
        ordered_agents = []
        for id in self.total_order:
            if id.startswith("B"):
                ordered_agents.append(bots.pop(0))
            elif id.startswith("P"):
                ordered_agents.append(players.pop(0))
            else:
                raise ValueError(f"")
        return ordered_agents

    def execute_round(self, client_input, round):  # all of the player allocations will get passed in here
        # build allocations here.

        tkns = self.num_players
        T = np.eye(self.num_players) * tkns
        T_prev = self.sim.get_transaction()
        # print("these are the allocations ", allocations)


        # use this under the sim.get_player inputs to populate T. The problem! is that I have to distinguish between human and non human players.
        for i, plyr in enumerate(self.players):  # DON'T RUN THIS UNITL YOU KNOW THAT YOU HAVE EVERYONE
            if plyr.getType() == "Human":
                try:
                    T[i] = client_input[i]["ALLOCATIONS"] # ok so that will have to be adjusted, depends on how we are managing client ids. i'll cook up something better later.
                except KeyError:
                    print("here is the key that was causing the error ", client_input[i])
            else:
                # if round == 1:
                #     print("This is what we are passing in \n ", i, " r ", round, " T_prev ", T_prev[:, i], " sim_pop ",
                #           self.sim.get_popularity(), "\n influence ", self.sim.get_influence(), " and extra data ",
                #           self.sim.get_extra_data(i))

                T[i] = plyr.play_round(
                    i,  # player index
                    round,  # round
                    T_prev[:, i],  # received
                    self.sim.get_popularity(),  # popularity
                    self.sim.get_influence(),  # influence
                    self.sim.get_extra_data(i),  # could NOT tell you what this is.
                    # False,
                )
                #print(T[i])

        self.sim.play_round(T)
        self.T = T
        new_popularity = self.sim.get_popularity()
        avg_pop = sum(new_popularity) / self.num_players
        self.avg_pop_per_round.append(avg_pop)
        self.game_popularities.append(new_popularity)
        return new_popularity # I think this is all we need? maybe?


    def get_groups(self):
        group_assumptions = []
        for i, plyr in enumerate(self.players):
            if plyr.getType() == "Human":
                group_assumptions.append([-1]) # its a human, I don't have access to da numbers.
            else:
                group_assumptions.append(plyr.get_selected_community())

        return group_assumptions



    def define_initial_pops(self, init_pop, num_players):
        base_pop = 100

        # assign the initial popularities
        if init_pop == "equal":
            initial_pops = [*[base_pop] * (num_players)]
        elif init_pop == "random":
            initial_pops = random.sample(range(1, 200), num_players)
        elif init_pop == "step":
            initial_pops = np.zeros(num_players, dtype=float)
            for i in range(0, num_players):
                initial_pops[i] = i + 1.0
            random.shuffle(initial_pops)
        elif init_pop == "power":
            initial_pops = np.zeros(num_players, dtype=float)
            for i in range(0, num_players):
                initial_pops[i] = 1.0 / (pow(i + 1, 0.7))
            random.shuffle(initial_pops)
        elif init_pop == "highlow":
            initial_pops = random.sample(range(1, 51), num_players)
            for i in range(0, num_players / 2):
                initial_pops[i] += 150
            random.shuffle(initial_pops)
        else:
            # print("don't understand init_pop " + str(init_pop) + " so just going with equal")
            initial_pops = [*[base_pop] * (num_players)]

        # normalize initial_pops so average popularity across all agents is 100
        tot_start_pop = base_pop * num_players
        sm = 1.0 * sum(initial_pops)
        for i in range(0, num_players):
            initial_pops[i] /= sm
            initial_pops[i] *= tot_start_pop

        return np.array(initial_pops)


    def get_T(self):
        return self.T

    def get_bot_votes(self, current_options_matrix):
        votes = {}
        for i, player in enumerate(self.players):
            if player.getType() != "Human":
                votes[str(i)] = player.getVote(current_options_matrix, i)
        return votes


    def get_influence(self):
        return self.sim.get_influence()

    def get_popularities(self, curr_round=None):
        return self.sim.get_popularity(curr_round)

    def record_individual_round(self, curr_round):
        total_data = {
            "T": self.sim.get_transaction().tolist(),
            "pop_new": self.sim.get_popularity().tolist(),
            "influence": self.sim.get_influence().tolist(),
            "pop_old": self.sim.get_popularity(curr_round-1).tolist()
        }
        #return self.sim.get_transaction().tolist(), self.sim.get_popularity().tolist(), self.sim.get_influence().tolist(), self.sim.get_popularity(curr_round-1).tolist()
        return total_data

    def get_highest_popularity_player(self):
        return (self.total_order[(list(self.sim.get_popularity())).index([max(list(self.sim.get_popularity()))])])

    def get_bot_types(self):
        bots = []
        for player in self.players:
            if isinstance(player, GeneAgent3):
                bots.append(0)
            if isinstance(player, HumanAgent):
                bots.append(1)
            if isinstance(player, SocialWelfareAgent):
                bots.append(2)
            if isinstance(player, RandomAgent):
                bots.append(3)
        return bots


    def create_pools(self, popSize, generationFolder, startIndex, num_gene_pools, tokens_per_player, bot_type):
        thePopulation = []

        if bot_type == 0:
            thePopulation = loadPopulationFromFile(popSize, generationFolder, startIndex, num_gene_pools, tokens_per_player)
            return thePopulation
        # I know what you're thinking. wheres the human? He won't fall under pools, thankfully. he'll go other places.

        # if bot_type == 2: # just go all teh way through. get us the whole thing even though we dont' need it bc its just easier that way.
        #     for i in range(popSize):
        #         thePopulation.append(SocialWelfareAgent(tokens_per_player))
        if bot_type == 3:
            for i in range(popSize):
                thePopulation.append(RandomAgent(tokens_per_player))
        if bot_type == 4:
            for i in range(popSize):
                thePopulation.append(SocialWelfare())
        if bot_type == 5:
            for i in range(popSize):
                thePopulation.append(AntiCat())

        return thePopulation

    def bot_ovveride(self, bots): # make sure this is the right type before you throw it on there.
        self.players = bots


    def get_game_deets(self):
        b = self.get_b()
        # jhg_bot_type = 0 ## ignore this for now, its not terribly relavent atm.
        pops = list(zip(*self.game_popularities))
        cv = self.get_cv()
        influence = (self.get_influence()).tolist()
        pop_per_round = list(self.avg_pop_per_round)

        total_data = {
            "b": b,
            "pop": pops,
            "cv": cv,
            "influence": influence,
            "pop_per_round": pop_per_round,
        }

        #return b, pops, cv, influence, pop_per_round
        return total_data

    def get_b(self):
        starting_pop = 100
        jhg_rounds = range(1, len(self.avg_pop_per_round) + 1)
        log_ratio = np.log(np.array(self.avg_pop_per_round) / starting_pop)
        b = np.dot(jhg_rounds, log_ratio) / np.dot(jhg_rounds, jhg_rounds) if jhg_rounds else 0
        return b

    def get_cv(self):
        popularity = list(self.get_popularities())
        mean = np.mean(popularity)
        std = np.std(popularity)
        cv = std / abs(mean)  # measures distribution bet  ter than, say, std or mean on their own.
        return cv


def loadPopulationFromFile(popSize, generationFolder, startIndex, num_gene_pools, tokens_per_player):
    fnombre = "Kill me"
    try:
        file_name = os.path.join("Engine", "botGenerations") # creates standard file path. we then append to this.

        # file_name = os.path.join(file_name, "assassins_gen_175")  # trying to be better and mroe aggressive on group forming
        file_name = os.path.join(file_name, "6x6Round1.csv") # JHG cab agents as used in the study
        # file_name = os.path.join(file_name, "longerConvex2.csv")
        # file_name = os.path.join(file_name, "sc_jhg_gen_299.csv") # the smartest vanilla agents
        # file_name = os.path.join(file_name, "w_kitties_gen_256.csv") # attempting to overcome cats
        # file_name = os.path.join(file_name, "jhg_sc_w_one_cat.csv") # another attempt
        # file_name = os.path.join(file_name, "convex2.csv") # this one should do well against the cats in both settings.
        # file_name = os.path.join(file_name, "bestOfWorstConvex.csv")
        # file_name = os.path.join(file_name, "backToBasics299.csv")
        # file_name = os.path.join(file_name, "PureJHGAntiCat.csv")
        # file_name = os.path.join(file_name, "fullyDevelopedPureJHG.csv")

        my_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(my_path, file_name)
        fnombre = file_path

        fp = open(fnombre, "r")
    except FileNotFoundError:
        try:
            fnombre = "../Server/Engine/gen_199.csv"
            fp = open(fnombre, "r")
        except FileNotFoundError:
            print(fnombre + " not found")
            quit()

    thePopulation = []

    for i in range(0,popSize):
        line = fp.readline()
        words = line.split(",")

        thePopulation.append(GeneAgent3(words[0], num_gene_pools))
        # thePopulation.append(GeneAgent3(words[0], num_gene_pools))
        thePopulation[i].count = float(words[1])
        thePopulation[i].relativeFitness = float(words[2])
        thePopulation[i].absoluteFitness = float(words[3])

    fp.close()

    return thePopulation


