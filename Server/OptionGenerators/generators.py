from Server.OptionGenerators.RandomGenerator import RandomGenerator

GENERATORS = {
    1: RandomGenerator
}

def generator_factory(generator_type: int, num_players: int, noise_magnitude: int, max_utility: int,
                 min_utility: int, num_options: int):
    return GENERATORS[generator_type](num_players, noise_magnitude, max_utility, min_utility, num_options)