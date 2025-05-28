from abc import abstractmethod, ABC, ABCMeta
from typing import List

# Attaches a wrapper to generateOptions in OptionGenerator to track the options over time
class GeneratorTrackerMeta(ABCMeta):
    def __new__(cls, name, bases, dct):
        original_generate = dct.get("generateOptions", None)

        if original_generate and callable(original_generate):
            def make_wrapper(func):
                def wrapper(self, *args, **kwargs):
                    result = func(self, *args, **kwargs)
                    self.options_history[len(self.options_history)] = result
                    return result
                return wrapper

            dct["generateOptions"] = make_wrapper(original_generate)

        return super().__new__(cls, name, bases, dct)

class OptionGenerator(ABC, metaclass=GeneratorTrackerMeta):
    def __init__(self, num_players: int, noise_magnitude: int, max_utility: int = 10, min_utility: int = -10, num_options: int = 3):
        self.num_players = num_players
        self.num_options = num_options
        self.max_utility = max_utility
        self.min_utility = min_utility
        self.noise_magnitude = noise_magnitude

        self.options_history = {}

    @abstractmethod
    def generateOptions(self) -> List[List[int]]:
        ...

    def generateZeros(self) -> List[List[int]]:
        return [[0 for _ in range(self.num_options)] for _ in range(self.num_players)]