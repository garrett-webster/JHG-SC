# testbed to test genes and display results in a human readable format.
import time
from Server.social_choice_sim import Social_Choice_Sim
import matplotlib.pyplot as plt
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


# starts the sim, could make this take command line arguments
# takes in a bot type, a number of rounds, and then runs it and plots the results. plans for expansion coming soon.
def run_trial(sim, num_rounds, num_cycles):
    cooperation_score = 0
    start_time = time.time()
    bot_type = sim.get_bot_type()

    results = {}
    for i in range(11): # total_players
        results[i] = [] # just throw in all the utilites

    for curr_round in tqdm(range(num_rounds)): # just a ridicuously large number
        current_start_time = time.time()

        sim.start_round() # creates the current current options matrix, makes da player nodes, sets up causes, etc.
        current_options_matrix = sim.get_current_options_matrix() # need this for JHG sim and bot votes.
        #bot_votes = sim.get_votes_single_chromosome() # this one is optimized for testing the results of a single chromosome.
        bot_votes = {}
        for cycle in range(num_cycles):
            #we start with this as a blank dict, update it and when it finishes it has the most recent bot votes after cycles.
            # set the cycle counter here, so that way I can keep track of it for graphing. there is a built in getter function for da graphign.
            print("this is the round under cycle! ", curr_round)
            bot_votes[cycle] = sim.get_votes(bot_votes, cycle)
            graph_nodes(sim, curr_round, cycle)
        # bot_votes = sim.get_votes()

        bot_votes = bot_votes[num_cycles-1] # grab just the last votes, they are the only ones that matter anyway.
        total_votes = len(bot_votes)
        winning_vote, round_results = sim.return_win(bot_votes)  # is all votes, works here
        if winning_vote != -1:  # keep track of how often they cooperate.
            cooperation_score += 1

        for bot in range(total_votes):
            results[bot].append(round_results[bot]) # this should work? I should have saved a stable version before hand.

        #print("this was the round time ", current_start_time - time.time())

    end_time = time.time()
    print("This was the total time ", end_time - start_time)

    sums_per_round = {}
    for bot in results:
        sums_per_round[bot] = []
        current_sum = 0
        for i, new_sum in enumerate(results[bot]):
            current_sum += new_sum
            sums_per_round[bot].append(current_sum)


    new_list = []
    for bot in sums_per_round:
        new_list.append(sums_per_round[bot][num_rounds-1])
    std = np.std(new_list)
    mean = np.mean(new_list)
    cv = std / abs(mean) # measures distribution bet  ter than, say, std or mean on their own.

    cooperation_score = cooperation_score / num_rounds # as a percent, how often we cooperated. (had a non negative cause pass)

    # Prepare the x-axis (rounds)
    rounds = range(num_rounds) # just generates a list so we can zip with it later

    # total score per round (for the black line)
    total_scores_per_round = [sum(results[player][round_num] for player in results) for round_num in rounds]

    # average score per round, by using the total score and num playres.
    num_players = len(results)  # Number of players (bots)
    average_scores_per_round = [total_score / num_players for total_score in total_scores_per_round]

    # cum average score and total score increase
    cumulative_average_score = [sum(average_scores_per_round[:i + 1]) for i in range(len(average_scores_per_round))]
    total_average_increase = cumulative_average_score[-1] / num_rounds

    # print statements go here.
    print("this was the total average increase ", total_average_increase)
    print("this was the cooperatino score ", cooperation_score)
    print("this was the cv ", cv)

    # create da plot
    plt.figure(figsize=(10, 6))

    # goes through that big ol fetcher and plots all the polayer socres per round
    for player, scores_list in sums_per_round.items():
        plt.plot(rounds, scores_list, marker='o', label=f'Player {player}')

    plt.plot(rounds, cumulative_average_score, marker='x', label='Cumulative Total Score', linewidth=3, color='black')

    plt.text(0.95, 0.90, f'Coefficient of Variation: {cv:.2f}', # should display the average standard deviation as well.
             horizontalalignment='right', verticalalignment='top',
             transform=plt.gca().transAxes, fontsize=12, color='black', weight='bold')

    plt.text(0.95, 0.95, f'Avg Increase: {total_average_increase:.2f}',
             horizontalalignment='right', verticalalignment='top',
             transform=plt.gca().transAxes, fontsize=12, color='black', weight='bold')

    plt.text(0.95, 0.85, f'Cooperation Score: {cooperation_score:.2f}',
             # should display the average standard deviation as well.
             horizontalalignment='right', verticalalignment='top',
             transform=plt.gca().transAxes, fontsize=12, color='black', weight='bold')

    # labels and a title
    plt.xlabel('Round')
    plt.ylabel('Score')
    plt.title('Scores per Round for Each Player With Algorithm ' + str(bot_type))
    plt.legend()

    # I would like to see the baby
    plt.grid(True)
    plt.tight_layout()

    bot_name = ""
    if bot_type == 1:
        bot_name = "Pareto"
    if bot_type == 2:
        bot_name = "Greedy"
    if bot_type == 3:
        bot_name = "Random"
    if bot_type == 4:
        bot_name = "betterGreedy"
    if bot_type == 5:
        bot_name = "limitedAwarenessGreedy"

    # what we are naming this new graph
    file_name = str(bot_name)
    # where do we put him.
    directory = r"C:\Users\Sean\Documents\GitHub\OtherGarrettStuff\JHG-SC\offlineSimStuff\Graphs"
    #directory = r"C:\Users\Sean\Documents\GitHub\IJCAI2024_SM\Code\GeneSimulation_py\Server\Graphs"

    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(directory, f"{file_name}.png")


    plt.savefig(file_path, dpi=300, bbox_inches='tight') # save the fetcher
    plt.show()


def graph_nodes(sim, curr_round, cycle):
    currVisualizer = causeNodeGraphVisualizer()
    currVisualizer.create_graph(sim, curr_round, cycle)


def create_sim():
    bot_type = 4 # 0 is random, 1 is pareto, 2 is greedy, 3 is betterGreedy, 4 is limitedAwareness, 5 is secondChoiceGreedy

    chromosomes = r"C:/Users/Sean/Documents/GitHub/OtherGarrettStuff/JHG-SC/offlineSimStuff/chromosomes/bGStandard.csv"
    # SUM: this sets the bot list type, so we can have siutaions set up
    scenario = r"C:\Users\Sean\Documents\GitHub\OtherGarrettStuff\JHG-SC\offlineSimStuff\scenarioIndicator\limitedAwareGreedy+secondChoice"
    cycle = -1 # a negative cycle indicates to me that this is a test - that, or something is really really wrong.

    sim = Social_Choice_Sim(11, 3, 0, bot_type, cycle, chromosomes, scenario)

    return sim



if __name__ == "__main__":
    num_rounds = 2
    num_cycles = 3
    current_sim = create_sim()
    run_trial(current_sim, num_rounds, num_cycles)
    # set up a fake round and then graph it
    current_sim.start_round()
    current_sim.get_votes() # literally just to place votes somewhere, yeah?
    #graph_nodes(current_sim)



