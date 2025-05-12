from Server.sim_interface import JHG_simulator
from Server.jhgLogger import JHGLogger
import time

def create_sim(num_players, num_humans):
    current_sim = JHG_simulator(num_humans, num_players)
    return current_sim

def run_trial(sim, num_rounds, create_graphs):

    currentLogger: JHGLogger = JHGLogger(current_sim)
    current_sim.start_game(num_humans, num_players)
    for round in range(num_rounds):
        current_popularity = current_sim.execute_round(None, round)
        print("this is the current popularity ", current_popularity)
        currentLogger.add_round_to_overview(round)

        time.sleep(1)
        # problem is I can't control the allocations here, which is a bust.


if __name__ == '__main__':
    num_players = 12
    num_humans = 0 # I Don't want any players. does that make this harder? Yes! I am gonna ignore that for now.
    create_graphs = True
    num_rounds = 10
    current_sim = create_sim(num_players, num_humans)


    updated_sim = run_trial(current_sim, num_rounds, create_graphs)