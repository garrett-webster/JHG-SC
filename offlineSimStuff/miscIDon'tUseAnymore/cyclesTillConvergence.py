# so this allows me to run the fetcher and create visualizations based off of scenarios and whatnot.
import time
from Server.social_choice_sim import Social_Choice_Sim
from tqdm import tqdm
import statistics
from offlineSimStuff.variousGraphingTools.causeNodeGraphVisualizer import causeNodeGraphVisualizer
from offlineSimStuff.variousGraphingTools.longTermGrapher import longTermGrapher
from offlineSimStuff.variousGraphingTools.simLogger import simLogger
import os

# starts the sim, could make this take command line arguments
# takes in a bot type, a number of rounds, and then runs it and plots the results. plans for expansion coming soon.
def run_trial(sim, num_rounds, num_cycles, create_graphs, group):
    # we need to get the groups, where we can have no groups or a variety of groups.
    current_logger = simLogger(sim)
    sim.set_rounds(num_rounds) # for graphing purposes
    start_time = time.time() # so we can calculate total time. not entirely necessary.
    sim.set_group(group)
    cycle_list = []
    for curr_round in tqdm(range(num_rounds)): # do this outside the sim, could make it inside but I like it outside.

        sim.start_round() # creates the current current options matrix, makes da player nodes, sets up causes, etc.
        bot_votes = {}
        cycle = 0
        while True:
            cycle += 1
            bot_votes[cycle] = sim.get_votes(bot_votes, curr_round, cycle, num_cycles)
            prev_votes = bot_votes.get(cycle-1)
            if prev_votes is not None:
                if prev_votes == bot_votes[cycle]:
                    break
            #if create_graphs:
                #graph_nodes(sim) # only do this for specific rounds
            if cycle > 20:
                print("Maximum reached")
                break
        cycle_list.append(cycle)

        bot_votes = bot_votes[num_cycles-1] # grab just the last votes, they are the only ones that matter anyway.
        total_votes = len(bot_votes)
        # keep this out just in case.
        winning_vote, round_results = sim.return_win(bot_votes)  # is all votes, works here
        # this saves everything to the JSON that we need. I mean it saves it to the sim, I can change that so we can log it instead.
        #sim.save_results()
        #current_logger.record_individual_round()

    end_time = time.time()
    current_logger.record_big_picture()
    #print("This was the total time ", end_time - start_time)
    print("this was the max ", max(cycle_list), " and then here is teh median ", statistics.median(cycle_list), " and here is the averaage ", statistics.mean(cycle_list))
    return sim


def graph_nodes(sim, votes_override):
    currVisualizer = causeNodeGraphVisualizer()
    currVisualizer.create_graph_with_sim_vote_ovverride(sim, votes_override)


def create_sim(scenario=None, chromosomes=None, group=""):

    # SUM: this sets the bot list type, so we can have siutaions set up
    if scenario is None:
        scenario = r"C:\Users\Sean\Documents\GitHub\OtherGarrettStuff\JHG-SC\offlineSimStuff\scenarioIndicator\somewhatMoreAwareGreedy"
    if chromosomes is None:
        chromosomes = r"C:/Users/Sean/Documents/GitHub/OtherGarrettStuff/JHG-SC/offlineSimStuff/chromosomes/bGStandard.csv"
    cycle = -1 # a negative cycle indicates to me that this is a test - that, or something is really really wrong.
    curr_round = -1

    sim = Social_Choice_Sim(7, 3, 0, cycle, curr_round, chromosomes, scenario, group)

    return sim


# if you attempt to run this, just know that it will
if __name__ == "__main__":
    num_rounds = 10
    num_cycles = 3
    create_graphs = True
    total_groups = ["", 0, 1, 2]
    chromosomes_directory = "testChromosome"
    group = ""
    scenario = "../../offlineSimStuff/scenarioIndicator/somewhatMoreAwareGreedy"
    chromosome = "../../offlineSimStuff/chromosomes/highestFromTesting"


    current_sim = create_sim(scenario, chromosome, group)
    updated_sim = run_trial(current_sim, num_rounds, num_cycles, create_graphs, group)
    current_visualizer = longTermGrapher()
    current_visualizer.draw_graph_from_sim(updated_sim)

    big_boy_json = {}
