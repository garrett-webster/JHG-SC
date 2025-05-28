from random import random
from typing import List

from Server.OptionGenerators.OptionGenerator import OptionGenerator

UTILITIY_PER_PLAYER = 5
MIN_TENDENCY = -3


class TendencyGenerator(OptionGenerator):
    def __init__(self, num_players: int, noise_magnitude: int, max_utility: int, min_utility: int, num_options: int):
        super().__init__(num_players, noise_magnitude, max_utility, min_utility, num_options)
        tendencies = self.generateZeros()

        for player in range(self.num_players):
            # The total utility that the tendencies of each player should add to
            total_utility = UTILITIY_PER_PLAYER * num_options
            for option_num in range(num_options):
                if option_num < num_options - 1: # The last tendency is set to whatever is left
                    tendency = total_utility
                else:
                    # Randomly allocate some amount of the remaining total as the current tendency
                    tendency = random.randint(MIN_TENDENCY, total_utility)
                    total_utility -= tendency
                tendencies[player][option_num] = tendency

    def generateOptions(self) -> List[List[int]]:
        pass