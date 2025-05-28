from random import randint
from typing import List

from Server.OptionGenerators.OptionGenerator import OptionGenerator


class RandomGenerator(OptionGenerator):
    def __init__(self, num_players: int, noise_magnitude: int, max_utility: int, min_utility: int, num_options: int):
        super().__init__(num_players, noise_magnitude, max_utility, min_utility, num_options)

    def generateOptions(self) -> List[List[int]]:
        options = []
        for _ in range(self.num_players):
            generated_options = [randint(self.min_utility + self.noise_magnitude, self.max_utility - self.noise_magnitude) for _ in range(self.num_options)]
            for i in range(len(generated_options)):
                generated_options[i] += randint(-self.noise_magnitude,self.noise_magnitude)
            options.append(generated_options)

        return options