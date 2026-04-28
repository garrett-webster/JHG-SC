from stagHare.environment.state import State
from typing import Tuple
from stagHare.utils.utils import POSSIBLE_DELTA_VALS, POSSIBLE_MOVEMENTS, VERTICAL
from stagHare.utils.variousFunctions import fastchoices

class Agent:
    def __init__(self, name: str) -> None:
        self.name = name

    def act(self, state: State, reward: float, round_num: int) -> Tuple[int, int]:
        pass

    def is_hunting_hare(self) -> bool:
        pass

    def random_action(self, state: State) -> Tuple[int, int]:
        curr_row, curr_col = state.agent_positions[self.name]
        movement = fastchoices(POSSIBLE_MOVEMENTS)
        delta = fastchoices(POSSIBLE_DELTA_VALS)

        if movement == VERTICAL:
            return curr_row + delta, curr_col

        else:
            return curr_row, curr_col + delta



