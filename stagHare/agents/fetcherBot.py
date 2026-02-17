# the purpose of this bot is to be a fetcher.
# thats his whole schtick.

# game plan: act like a cab agent (mostly), and just hunt the stag
# but! if we are close to the hare (within a space or two)
# suddenly defect and screw everyone else over.
# this should completely mess with the cab agents predictions.
# so lets just see what happens.

from stagHare.agents.agent import Agent
from stagHare.environment.state import State
import numpy as np
from typing import Tuple
from stagHare.utils.utils import POSSIBLE_DELTA_VALS, POSSIBLE_MOVEMENTS, VERTICAL
from offlineSimStuff.runningTools.runnerHelper import create_agents

from Server.Engine.completeBots.geneagent3 import GeneAgent3


class FetcherBot(Agent):
    # this might not be the neatest way to do it, it might be better
    # we might need ot go back and do the smae thing to the SC gene3 agents for consistency.
    def __init__(self, id, name: str) -> None:
        super().__init__(name) # super based off the agent call
        self.id = id
        self.name = name
        # create a Gene3agent that we can reference.
        self.agent = None # we don't use this.
        self.hunt = True # by default, they hunt the hare.

    # this however, this is gonna be a fetcher.
    def act(self, state: State, reward: float, round_num: int) -> list[int]:
        name = "R" + str(self.id)
        current_x, current_y = state.agent_positions[name]
        hare_x, hare_y = state.agent_positions["hare"]

        hare_movements = state.n_movements(current_x, current_y, hare_x, hare_y)

        if hare_movements <= 1: # if they are one tile from the hare or right next to it:
            # print("DEFECTING SIRE GREE HE HE ")
            self.hunt = False # just realized their intents and their everything else wasn't working out.
            new_allocation = [-2 for _ in range(3)] # always three agents.
            new_allocation[self.id] = 2

        else:
            self.hunt = True
            new_allocation = [2, 2, 2]

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
