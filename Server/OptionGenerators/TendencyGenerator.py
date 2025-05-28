import copy
import random
from typing import List

from Server.OptionGenerators.OptionGenerator import OptionGenerator

UTILITIY_PER_PLAYER = 3
MIN_TENDENCY = -3


class TendencyGenerator(OptionGenerator):
    def __init__(self, num_players: int, noise_magnitude: int, max_utility: int, min_utility: int, num_options: int):
        super().__init__(num_players, noise_magnitude, max_utility, min_utility, num_options)
        self.tendencies = self.generateZeros()

        for player in range(self.num_players):
            # The total utility that the tendencies of each player should add to
            total_utility = UTILITIY_PER_PLAYER * num_options
            for option_num in range(num_options):
                if option_num == (num_options - 1): # The last tendency is set to whatever is left
                    tendency = total_utility
                else:
                    # Randomly allocate some amount of the remaining total as the current tendency
                    tendency = random.randint(MIN_TENDENCY, total_utility)
                    total_utility -= tendency
                # tendency = max(min(tendency, max_utility - noise_magnitude), MIN_TENDENCY) # Clamps the tendency numbers to the range from the minimum tendency to the max utility possible minus the noise magnitude to force it to be in the valid range
                self.tendencies[player][option_num] = tendency

        print("Debug")

    def generateOptions(self) -> List[List[int]]:
        options = self.generateZeros()

        for i in range(len(options)):
            for j in range(self.num_options):
                option = self.clamp(self.tendencies[i][j] + random.randint(-self.noise_magnitude, self.noise_magnitude))
                options[i][j] = option
        return options

    def clamp(self, option: int):
        if option > self.max_utility: option = self.max_utility
        if option < self.min_utility: option = self.min_utility

        return option