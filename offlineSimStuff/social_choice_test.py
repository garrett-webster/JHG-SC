# so this allows me to run the fetcher and create visualizations based off of scenarios and whatnot.
import time
from Server.social_choice_sim import Social_Choice_Sim
import os
from tqdm import tqdm

from offlineSimStuff.variousGraphingTools.causeNodeGraphVisualizer import causeNodeGraphVisualizer
from offlineSimStuff.variousGraphingTools.longTermGrapher import longTermGrapher


# starts the sim, could make this take command line arguments
# takes in a bot type, a number of rounds, and then runs it and plots the results. plans for expansion coming soon.
def run_trial(sim, num_rounds, num_cycles, create_graphs, group):
    # we need to get the groups, where we can have no groups or a variety of groups.

    sim.set_rounds(num_rounds) # for graphing purposes
    start_time = time.time() # so we can calculate total time. not entirely necessary.


    for curr_round in tqdm(range(num_rounds)): # do this outside the sim, could make it inside but I like it outside.
        sim.set_group(group)
        sim.start_round() # creates the current current options matrix, makes da player nodes, sets up causes, etc.
        bot_votes = {}
        for cycle in range(num_cycles):
            bot_votes[cycle] = sim.get_votes(bot_votes, curr_round, cycle)
            if create_graphs:
                graph_nodes(sim, curr_round, cycle) # only do this for specific rounds

        bot_votes = bot_votes[num_cycles-1] # grab just the last votes, they are the only ones that matter anyway.
        total_votes = len(bot_votes)
        # keep this out just in case.
        winning_vote, round_results = sim.return_win(bot_votes)  # is all votes, works here
        # this saves everything to the JSON that we need. I mean it saves it to the sim, I can change that so we can log it instead.
        sim.save_results()

    end_time = time.time()
    print("This was the total time ", end_time - start_time)
    return sim


def graph_nodes(sim, curr_round, cycle):
    currVisualizer = causeNodeGraphVisualizer()
    currVisualizer.create_graph(sim, curr_round, cycle)


def create_sim():
    chromosomes = r"C:/Users/Sean/Documents/GitHub/OtherGarrettStuff/JHG-SC/offlineSimStuff/chromosomes/bGStandard.csv"
    # SUM: this sets the bot list type, so we can have siutaions set up
    scenario = r"C:\Users\Sean\Documents\GitHub\OtherGarrettStuff\JHG-SC\offlineSimStuff\scenarioIndicator\somewhatMoreAwareGreedy"
    cycle = -1 # a negative cycle indicates to me that this is a test - that, or something is really really wrong.
    curr_round = -1

    sim = Social_Choice_Sim(11, 3, 0, cycle, curr_round, chromosomes, scenario)

    return sim



if __name__ == "__main__":
    num_rounds = 10000
    num_cycles = 3
    create_graphs = False
    total_groups = ["",0,1,2]
    scenario_directory = "scenarioIndicator"

    # for scenario_path in os.listdir(scenario_directory):
    #     scenario = os.path.join(scenario_directory, scenario_path)
    #     for group in total_groups:

    # current_sim = create_sim(scenario)
    current_sim = create_sim()
    current_sim = run_trial(current_sim, num_rounds, num_cycles, create_graphs, "")
    current_visualizer = longTermGrapher()
    current_visualizer.draw_graph(current_sim)


    # set up a fake round and then graph it
    #current_sim.start_round()
    #current_sim.get_votes() # literally just to place votes somewhere, yeah?
    #graph_nodes(current_sim)



