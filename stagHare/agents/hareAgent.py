from stagHare.agents.agent import Agent
from stagHare.environment.state import State
from typing import Tuple
import numpy as np

# this guy exclusively hunts hares. He's just for other stuff.
class HareAgent(Agent):
    def __init__(self, id: int, name: str) -> None:
        Agent.__init__(self, name)
        self.id = id

    def act(self, state: State, reward: float, round_num: int):
        new_allocation = [0 for _ in range(3)]
        new_allocation[self.id] = 6
        return new_allocation

    # for the hare agent, it shoudl return [2, -2, -2] if we are the first player.
    def create_allocation(self, index, state):
        num_players = len(state.agent_positions) - 2 # two of those agents are stag and hare
        allocation = np.zeros(num_players)
        allocation.fill(-2)
        allocation[index-2] = 2
        return allocation

    def is_hunting_hare(self) -> bool:
        return True


