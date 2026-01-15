from stagHare.agents.agent import Agent
from stagHare.environment.state import State
import numpy as np
from typing import Tuple
from stagHare.utils.utils import POSSIBLE_DELTA_VALS, POSSIBLE_MOVEMENTS, VERTICAL
from offlineSimStuff.runningTools.runnerHelper import create_agents


class CabAgent(Agent):
    # this might not be the neatest way to do it, it might be better
    # we might need ot go back and do the smae thing to the SC gene3 agents for consistency.
    def __init__(self, id, name: str) -> None:
        super().__init__(name) # super based off the agent call
        self.id = id
        self.name = name
        # create a Gene3agent that we can reference.
        self.agent = create_agents(1, [], "pureJHGselfPlayMFalse.csv", True, True) # just start wiht something,


    # this however, this is gonna be a fetcher.
    def act(self, state: State, reward: float, round_num: int) -> Tuple[int, int]:
        pass
        # so let me remember whats going on here
        # however, building the influence matrix, now THAT is goign to be a fetcher.
        # we need to grab the influence matrix, as well as the current state
        # we can ignore the reward
        # from there, we need to interpret the current allocation
        # just ask if its hare or stag oriented
        # then return that action




    # don't know if we will need this or anything
    def is_hunting_hare(self) -> bool:
        pass

    # shouldn't need this either.
    def random_action(self, state: State) -> Tuple[int, int]:
        curr_row, curr_col = state.agent_positions[self.name]
        movement = np.random.choice(POSSIBLE_MOVEMENTS)
        delta = np.random.choice(POSSIBLE_DELTA_VALS)

        if movement == VERTICAL:
            return curr_row + delta, curr_col

        else:
            return curr_row, curr_col + delta
