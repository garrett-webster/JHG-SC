from stagHare.agents.agent import Agent
from stagHare.environment.state import State
from typing import Tuple
import numpy as np

class HareAgent(Agent):
    def __init__(self, id: int, name: str) -> None:
        Agent.__init__(self, name)
        self.id = id

    def act(self, state: State, reward: float, round_num: int) -> Tuple[int, int]:
        # the allocation is going to be weird but we got this
        print("HEY THIS SHOULDN'T BE TRIPPING!!! ")
        return [0, 0] # don't move anywhere.

    # for the hare agent, it shoudl return [2, -2, -2] if we are the first player.
    def create_allocation(self, index, state):
        num_players = len(state.agent_positions) - 2 # two of those agents are stag and hare
        allocation = np.zeros(num_players)
        allocation.fill(-2)
        allocation[index-2] = 2
        return allocation

    def is_hunting_hare(self) -> bool:
        return True


