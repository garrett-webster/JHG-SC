from stagHare.agents.agent import Agent
from stagHare.environment.state import State
import numpy as np
from typing import Tuple
from stagHare.utils.utils import POSSIBLE_DELTA_VALS, POSSIBLE_MOVEMENTS, VERTICAL
from offlineSimStuff.runningTools.runnerHelper import create_agents

from Server.Engine.completeBots.geneagent3 import GeneAgent3


class CabAgent(Agent):
    # this might not be the neatest way to do it, it might be better
    # we might need ot go back and do the smae thing to the SC gene3 agents for consistency.
    def __init__(self, id, name: str, random_agents: bool, forced_random: bool, gene="", agent_name="") -> None:
        super().__init__(name) # super based off the agent call
        self.id = id
        self.name = name
        # doing 1 gene copy becuase 3 doesn't appera to really imporve performance appreciably.
        # create a Gene3agent that we can reference.
        # got gene? use that
        if gene != "":
            self.agent = GeneAgent3(gene, 1)
        # don't got gene? use that.
        else:
            if agent_name != "":    # just trying this for now.
                self.agent = create_agents(1, [], agent_name, forced_random, random_agents)[0]# just start wiht something,
            else:
                self.agent = GeneAgent3("", 1)  # create a random geneAgent3.



        # print("This is the first agent chromosome ", self.agent.genes_long[0]["alpha"])
        self.hunt = True # by default, they hunt the hare.
        self.set_game_params()

    # not sure if we will ever need this
    def set_agent(self, agent):
        self.agent = agent


    def set_id(self, id):
        self.id = id # just throw this in there for the genetic algorithm.

    # this however, this is gonna be a fetcher.
    def act(self, state: State, reward: float, round_num: int) -> Tuple[int, int]:

        extra_data = {
            i: {
                j: None for j in range(len(list(state.agent_positions.keys())))
            } for i in range(len(list(state.agent_positions.keys())))
        }

        new_allocation = self.agent.play_round(self.id, round_num, self.received, self.popularities, self.influence, extra_data)
        return new_allocation

        # so let me remember whats going on here
        # however, building the influence matrix, now THAT is goign to be a fetcher.
        # we need to grab the influence matrix, as well as the current state
        # we can ignore the reward
        # from there, we need to interpret the current allocation
        # just ask if its hare or stag oriented
        # then return that action


    def set_helpers(self, engine):
        self.influence = engine.get_influence()
        self.popularities = engine.get_popularity()
        T_prev = engine.get_transaction()
        self.received = T_prev[:,self.id]

    def set_hunt(self, new_bool):
        self.hunt = new_bool

    # don't know if we will need this or anything
    def is_hunting_hare(self) -> bool:
        return self.hunt # this should work better. 

    # shouldn't need this either.
    def random_action(self, state: State) -> Tuple[int, int]:
        curr_row, curr_col = state.agent_positions[self.name]
        movement = np.random.choice(POSSIBLE_MOVEMENTS)
        delta = np.random.choice(POSSIBLE_DELTA_VALS)

        if movement == VERTICAL:
            return curr_row + delta, curr_col

        else:
            return curr_row, curr_col + delta

    def set_game_params(self):
        num_players = 3 # this is hard coded in a lot of places.
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


        self.agent.setGameParams(game_params, forcedRandom)
