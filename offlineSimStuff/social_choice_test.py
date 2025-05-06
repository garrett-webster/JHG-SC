# testbed to test genes and display results in a human readable format.
import time
from Server.social_choice_sim import Social_Choice_Sim

from collections import Counter
import statistics
import random
import numpy as np
import os
from pathlib import Path
from tqdm import tqdm
import pandas as pd
from Server.Node import Node

from offlineSimStuff.variousGraphingTools.causeNodeGraphVisualizer import causeNodeGraphVisualizer
from offlineSimStuff.variousGraphingTools.longTermGrapher import longTermGrapher


# starts the sim, could make this take command line arguments
# takes in a bot type, a number of rounds, and then runs it and plots the results. plans for expansion coming soon.
def run_trial(sim, num_rounds, num_cycles):
    sim.set_rounds(num_rounds)
    start_time = time.time()

    results = {}
    for i in range(11): # total_players
        results[i] = [] # just throw in all the utilites

    for curr_round in tqdm(range(num_rounds)): # just a ridicuously large number

        sim.start_round() # creates the current current options matrix, makes da player nodes, sets up causes, etc.
        bot_votes = {}
        for cycle in range(num_cycles):
            bot_votes[cycle] = sim.get_votes(bot_votes, curr_round, cycle)
            #print("We have printed a grpah your honor :salute")
            #graph_nodes(sim, curr_round, cycle) # only do this for specific rounds

        bot_votes = bot_votes[num_cycles-1] # grab just the last votes, they are the only ones that matter anyway.
        total_votes = len(bot_votes)
        winning_vote, round_results = sim.return_win(bot_votes)  # is all votes, works here

        for bot in range(total_votes):
            results[bot].append(round_results[bot]) # this should work? I should have saved a stable version before hand.

    end_time = time.time()
    print("This was the total time ", end_time - start_time)
    sim.set_results(results)
    return sim


def graph_nodes(sim, curr_round, cycle):
    print("do we make it here, ")
    currVisualizer = causeNodeGraphVisualizer()
    currVisualizer.create_graph(sim, curr_round, cycle)


def create_sim():
    bot_type = 4 # 0 is random, 1 is pareto, 2 is greedy, 3 is betterGreedy, 4 is limitedAwareness, 5 is secondChoiceGreedy

    chromosomes = r"C:/Users/Sean/Documents/GitHub/OtherGarrettStuff/JHG-SC/offlineSimStuff/chromosomes/bGStandard.csv"
    # SUM: this sets the bot list type, so we can have siutaions set up
    scenario = r"C:\Users\Sean\Documents\GitHub\OtherGarrettStuff\JHG-SC\offlineSimStuff\scenarioIndicator\limitedAwareGreedy+secondChoice"
    cycle = -1 # a negative cycle indicates to me that this is a test - that, or something is really really wrong.
    curr_round = -1

    sim = Social_Choice_Sim(11, 3, 0, cycle, curr_round, chromosomes, scenario)

    return sim



if __name__ == "__main__":
    num_rounds = 1000
    num_cycles = 3

    current_sim = create_sim()
    current_sim = run_trial(current_sim, num_rounds, num_cycles)
    current_visualizer = longTermGrapher()
    current_visualizer.draw_graph(current_sim)


    # set up a fake round and then graph it
    current_sim.start_round()
    current_sim.get_votes() # literally just to place votes somewhere, yeah?
    #graph_nodes(current_sim)



