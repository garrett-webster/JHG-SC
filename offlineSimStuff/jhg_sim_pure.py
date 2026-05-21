from Server.Engine.simulator import GameSimulator
import numpy as np
import random

class Jhg_Sim_Pure():
    def __init__(self, agents):
        pass
        self.agents = agents
        self.num_players = len(agents)
        self.engine = None
        self.create_engine(self.num_players) # assume the agents represent all possible players.
        self.T = None
        # goal: take in a list of agents, create a simulator that lets us do things
        # and go from there.
        self.avg_pop_per_round = [100]
        self.game_popularities = [[100] * self.num_players]
        self.bot_types = [0 for _ in range(self.num_players)] # I don't feel like dealing with this! Simple as!
        self.agent_names = ["" for _ in range(self.num_players)] # honestly yeah. that might be something worth implementing though.


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

    def create_engine(self, num_players):

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

        self.engine = GameSimulator(
            game_params)  # sets up our sim object - might need to make this global so we can grab it wherever we need it.
        self.T = np.array([[0.0 for _ in range(num_players)] for _ in range(num_players)])


    def get_influence(self):
        return self.engine.get_influence()

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

    def get_popularities(self, curr_round=None):
        return self.engine.get_popularity(curr_round)


    # like this should work?
    def execute_round(self, round):  # all of the player allocations will get passed in here
        # build allocations here.

        tkns = self.num_players
        T = np.eye(self.num_players) * tkns
        T_prev = self.engine.get_transaction()



        # use this under the sim.get_player inputs to populate T. The problem! is that I have to distinguish between human and non human players.
        for i, plyr in enumerate(self.agents):  # DON'T RUN THIS UNITL YOU KNOW THAT YOU HAVE EVERYONE
                T[i] = plyr.play_round(
                    i,  # player index
                    round,  # round
                    T_prev[:, i],  # received
                    self.engine.get_popularity(),  # popularity
                    self.engine.get_influence(),  # influence
                    self.engine.get_extra_data(i),  # could NOT tell you what this is.
                    # False,
                )
                #print(T[i])

        self.engine.play_round(T)
        self.T = T
        new_popularity = self.engine.get_popularity()
        avg_pop = sum(new_popularity) / self.num_players
        self.avg_pop_per_round.append(avg_pop)
        self.game_popularities.append(new_popularity)
        # no need to return anything, just let her ride.