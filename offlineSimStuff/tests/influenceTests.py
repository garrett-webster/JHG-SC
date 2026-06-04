## RESULTS:
# T[i][j] = player j gives to payer i
# columns represent giving, rows represent receiving.

from Server.Engine.simulator import GameSimulator
import numpy as np
import random

def define_initial_pops(init_pop, num_players):
    base_pop = 100

    # assign the initial popularities
    if init_pop == "equal":
        initial_pops = [*[base_pop] * (num_players)]
    elif init_pop == "random":
        initial_pops = random.sample(range(1, 200), num_players)
    elif init_pop == "step":
        initial_pops = np.zeros(num_players, dtype=float)
        for i in range(0, num_players):
            initial_pops[i] = i + 1.0
        random.shuffle(initial_pops)
    elif init_pop == "power":
        initial_pops = np.zeros(num_players, dtype=float)
        for i in range(0, num_players):
            initial_pops[i] = 1.0 / (pow(i + 1, 0.7))
        random.shuffle(initial_pops)
    elif init_pop == "highlow":
        initial_pops = random.sample(range(1, 51), num_players)
        for i in range(0, num_players / 2):
            initial_pops[i] += 150
        random.shuffle(initial_pops)
    else:
        # print("don't understand init_pop " + str(init_pop) + " so just going with equal")
        initial_pops = [*[base_pop] * (num_players)]

    # normalize initial_pops so average popularity across all agents is 100
    tot_start_pop = base_pop * num_players
    sm = 1.0 * sum(initial_pops)
    for i in range(0, num_players):
        initial_pops[i] /= sm
        initial_pops[i] *= tot_start_pop

    return np.array(initial_pops)


def create_sim(num_players):
    poverty_line = 0
    init_pop = 100

    initial_pops = define_initial_pops(init_pop, num_players)

    alpha_min, alpha_max = 0.20, 0.20
    beta_min, beta_max = 0.5, 1.0
    keep_min, keep_max = 0.95, 0.95
    give_min, give_max = 1.30, 1.30
    steal_min, steal_max = 1.6, 1.60

    num_players = num_players

    game_params = {
        "num_players": num_players,
        "alpha": alpha_min,  # np.random.uniform(alpha_min, alpha_max),
        "beta": beta_min,  # np.random.uniform(beta_min, beta_max),
        "keep": keep_min,  # np.random.uniform(keep_min, keep_max),
        "give": give_min,  # np.random.uniform(give_min, give_max),
        "steal": steal_min,  # np.random.uniform(steal_min, steal_max),
        "poverty_line": poverty_line,
        "base_popularity": np.array(initial_pops)
    }

    sim = GameSimulator(
        game_params)  # sets up our sim object - might need to make this global so we can grab it wherever we need it.
    T = np.array([[0.0 for _ in range(num_players)] for _ in range(num_players)])
    return sim



if __name__ == '__main__':
    num_players = 7
    num_rounds = 20

    # lets do like, 10 people
    T_one = [[] for _ in range(num_players)]

    T_one = [
        [0, 0, 1, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0],
    ]

    print("This is T_one ", T_one)
    forced_random = False

    new_engine = create_sim(num_players)

    for i in range(num_rounds):
        new_engine.engine.apply_transaction(T_one)

    new_pops = new_engine.get_popularity()

    # lets do like, 10 people
    T_two = [
        [1, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 1],
    ]

    new_engine_two = create_sim(num_players)

    for i in range(num_rounds):
        new_engine_two.engine.apply_transaction(T_two)

    new_pops_two = new_engine_two.get_popularity()


    print("here is influence 1 \n", new_engine.get_influence())

    print("Here is influence 2 \n", new_engine_two.get_influence())
