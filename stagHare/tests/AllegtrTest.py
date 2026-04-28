from stagHare.environment.world import StagHare
from stagHare.runnerHelper import run_trial, process_scores, create_hunters_with_list  # this SHOULD be all we need.
import numpy as np

def test_transition_function_differences():
    num_attempts = 1  # don't worry about this
    # don't add cats yet, we will worry about that later.
    # agent_name = "mixedJHGSelfPlay.csv"
    agent_names = [["6x6round3.csv", "6x6round3.csv", "6x6round3.csv"]]
    scenario_types = ["HCAB_self_play"]

    height, width = 16, 16  # lets start there, not too big but there.
    random_agents = False
    forced_random = True
    scenario_type = scenario_types[0]
    curr_agent_names = agent_names[0]


    hunters = create_hunters_with_list(random_agents, forced_random, curr_agent_names)

    np.random.seed(42) # whatever.
    stag_hare_1 = None
    while stag_hare_1 is None or stag_hare_1.is_over():
        stag_hare_1 = StagHare(height, width, hunters)


    np.random.seed(42)
    stag_hare_2 = None
    while stag_hare_2 is None or stag_hare_2.is_over():
        stag_hare_2 = StagHare(height, width, hunters)

    assert stag_hare_1.state.agent_positions == stag_hare_2.state.agent_positions
    assert np.array_equal(stag_hare_1.state.grid, stag_hare_2.state.grid)

    ethan_bools = [True, False]
    # we no longer use this, becuase there is now never a reason to use it. You can re-instantiate this if you really
        # want to though, but this was to help us test some stuff.


    # breaking news: these two do generate the same stag hare map, so the discrepancy isn't there. its somewhere else!

    np.random.seed(0) # whatever.
    game_information_1 = run_trial(curr_agent_names, height, width, random_agents, forced_random, scenario_type)

    np.random.seed(0) # whatever.
    game_information_2 = run_trial(curr_agent_names, height, width, random_agents, forced_random, scenario_type)

    assert(game_information_1.position_history == game_information_2.position_history)

if __name__ == "__main__":
    test_transition_function_differences()