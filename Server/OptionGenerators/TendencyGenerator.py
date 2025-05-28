import random
from typing import List

from Server.OptionGenerators.OptionGenerator import OptionGenerator

UTILITIY_PER_PLAYER = 3
MIN_TENDENCY = -3


class TendencyGenerator(OptionGenerator):
    def __init__(self, num_players: int, noise_magnitude: int, max_utility: int, min_utility: int, num_options: int, *args):
        super().__init__(num_players, noise_magnitude, max_utility, min_utility, num_options)
        self.tendencies = self.generateZeros()

        for player in range(self.num_players):
            # The total utility that the tendencies of each player should add to
            total_utility = UTILITIY_PER_PLAYER * num_options

            option = int(round(total_utility/3 + random.randint(-2, 2)))
            self.tendencies[player][0] = option
            total_utility -= option

            option = int(round(total_utility / 2 + random.randint(-2, 2)))
            self.tendencies[player][1] = option
            total_utility -= option

            self.tendencies[player][2] = int(round(total_utility))


    def generateOptions(self) -> List[List[int]]:
        options = self.generateZeros()

        for i in range(len(options)):
            for j in range(self.num_options):
                option = self.clamp(self.tendencies[i][j] + random.randint(-self.noise_magnitude, self.noise_magnitude))
                options[i][j] = option
        return options
        # return self.tendencies