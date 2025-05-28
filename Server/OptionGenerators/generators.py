from ConnectionManager import ConnectionManager
from Server.JHGManager import JHGManager
from Server.OptionGenerators.RandomGenerator import RandomGenerator
from Server.OptionGenerators.TendencyGenerator import TendencyGenerator

GENERATORS = {
    1: RandomGenerator,
    2: TendencyGenerator
}

def generator_factory(generator_type: int, num_players: int, noise_magnitude: int, max_utility: int,
                 min_utility: int, num_options: int, jhg_manager: JHGManager, connection_manager: ConnectionManager):
    return GENERATORS[generator_type](num_players, noise_magnitude, max_utility, min_utility, num_options, jhg_manager, connection_manager)