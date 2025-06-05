# so this allows me to run the fetcher and create visualizations based off of scenarios and whatnot.
import time
from Server.social_choice_sim import Social_Choice_Sim
from tqdm import tqdm

from offlineSimStuff.variousGraphingTools.causeNodeGraphVisualizer import causeNodeGraphVisualizer
from offlineSimStuff.variousGraphingTools.longTermGrapher import longTermGrapher
from offlineSimStuff.variousGraphingTools.simLogger import simLogger
from Server.OptionGenerators.generators import generator_factory


# starts the sim, could make this take command line arguments
# takes in a bot type, a number of rounds, and then runs it and plots the results. plans for expansion coming soon.
def run_trial(sim, num_rounds, num_cycles, create_graphs, group):
    # we need to get the groups, where we can have no groups or a variety of groups.
    current_logger = simLogger(sim)
    sim.set_rounds(num_rounds) # for graphing purposes
    start_time = time.time() # so we can calculate total time. not entirely necessary.
    sim.set_group(group)

    #for curr_round in tqdm(range(1, num_rounds+1)): # do this outside the sim, could make it inside but I like it outside.
    for curr_round in (range(1, num_rounds+1)): # do this outside the sim, could make it inside but I like it outside.
        # force it to start at 1 instead of 0 -- helps prevent off by one errors later in the code.
    #for curr_round in (range(num_rounds)): # do this outside the sim, could make it inside but I like it outside.

        sim.start_round() # creates the current current options matrix, makes da player nodes, sets up causes, etc.
        bot_votes = {}
        for cycle in range(num_cycles):
            print("*****************STARTING CYCLE " + str(cycle+1) + "************************")
            bot_votes[cycle] = sim.get_votes(bot_votes, curr_round, cycle, num_cycles)
            sim.record_votes(bot_votes[cycle], cycle)

        all_votes = bot_votes
        bot_votes = bot_votes[num_cycles-1] # grab just the last votes, they are the only ones that matter anyway.
        total_votes = len(bot_votes)
        # keep this out just in case.
        winning_vote, round_results = sim.return_win(bot_votes)  # is all votes, works here
        #if sim.get_last_option() == 3: # I just wanna understand why this happens.
            #print("This was the winning vote ", winning_vote+1)
            #graph_nodes(sim)  # only do this for specific rounds
        # this saves everything to the JSON that we need. I mean it saves it to the sim, I can change that so we can log it instead.
        if create_graphs:  # only do this once, makes sense for jsoning stuff.
            graph_nodes(sim)  # only do this for specific rounds

        sim.save_results()
        #print("this is the round numb we are adding ", int(curr_round))
        #current_logger.add_round_to_sim(int(curr_round)) # make it start at one instead of zero.
        #current_logger.record_individual_round()

    end_time = time.time()
    #sim.print_col_passing() # this shows us the breakdown of the number distro. incredibly fascinating! look at it later.
    #current_logger.record_big_picture()
    #filename = "madMessign'"
    #current_logger.finish_json(filename)
    #print("This was the total time ", end_time - start_time)
    return sim


def graph_nodes(sim):
    currVisualizer = causeNodeGraphVisualizer()
    currVisualizer.create_graph_with_sim(sim)


def create_sim(scenario=None, chromosomes=None, group=""):

    # SUM: this sets the bot list type, so we can have siutaions set up
    if scenario is None:
        scenario = r"C:\Users\Sean\Documents\GitHub\OtherGarrettStuff\JHG-SC\offlineSimStuff\scenarioIndicator\humanAttempt3"
    if chromosomes is None:
        chromosomes = r"C:/Users/Sean/Documents/GitHub/OtherGarrettStuff/JHG-SC/offlineSimStuff/chromosomes/highestFromTesting.csv"
    cycle = -1 # a negative cycle indicates to me that this is a test - that, or something is really really wrong.
    curr_round = -1
    total_order = []
    total_players = 9
    num_causes = 3
    num_humans = 0
    num_bots = total_players - num_humans
    total_order = []
    for bot in range(num_bots):
        total_order.append("B" + str(bot))
    for human in range(num_humans):
        total_order.append("P" + str(human))

    generator = generator_factory(2, total_players, 5, 10, -10, 3, None, None)

    sim = Social_Choice_Sim(total_players, num_causes, num_humans, generator, cycle, curr_round, chromosomes, scenario, group, total_order)

    return sim



if __name__ == "__main__":
    num_rounds = 1
    num_cycles = 3
    create_graphs = True
    total_groups = ["", 0, 1, 2]
    chromosomes_directory = "testChromosome"
    group = ""
    scenario = r"C:\Users\Sean\Documents\GitHub\OtherGarrettStuff\JHG-SC\offlineSimStuff\scenarioIndicator\humanAttempt1"
    chromosome = r"C:\Users\Sean\Documents\GitHub\OtherGarrettStuff\JHG-SC\offlineSimStuff\chromosomes\experiment"

    current_sim = create_sim(scenario, chromosome, group)
    updated_sim = run_trial(current_sim, num_rounds, num_cycles, create_graphs, group)
    #current_visualizer = longTermGrapher()
    #current_visualizer.draw_graph_from_sim(updated_sim)


    big_boy_json = {}




# legacy code for testing every chromosome that I generated in the chromsome repo. Don't worry about it too much.
# for chromosome_path in os.listdir(chromosomes_directory):
#     chromosome = os.path.join(chromosomes_directory, chromosome_path)
#     current_sim = create_sim(scenario, chromosome, group)
#
#     updated_sim = run_trial(current_sim, num_rounds, num_cycles, create_graphs, group)
#     current_visualizer = longTermGrapher()
#     current_visualizer.draw_graph_from_sim(updated_sim)
#     current_logger = simLogger(updated_sim)
#     current_logger.log_stuff_for_chromosome(big_boy_json)
#
# final_logger = simLogger()
# final_logger.write_a_json_to_file(big_boy_json)




# legacy code for testing every scenario and every round. Right now I am more interested in no groups, my bot

# num_rounds = 10000
# num_cycles = 3
# create_graphs = False
# total_groups = ["", 0, 1, 2]
# scenario_directory = "scenarioIndicator"
# group = ""
# for scenario_path in os.listdir(scenario_directory):
#     scenario = os.path.join(scenario_directory, scenario_path)
#     for group in total_groups:
#         # current_sim = create_sim(scenario)
#         current_sim = create_sim()  # if no sim
#
#         current_sim = run_trial(current_sim, num_rounds, num_cycles, create_graphs, group)
#         current_visualizer = longTermGrapher()
#         current_visualizer.draw_graph_from_sim(current_sim)


# legacy code for generating all the test chromosome:
    #
    #
    # output_dir = "testChromosome"
    # os.makedirs(output_dir, exist_ok=True)
    #
    # chromosome_1_options = [0.01, 0.1, 0.2, 0.5, 0.9, 1, 2, 5, 10]
    # chromosome_2_options = [0.01, 0.1, 0.5, 0.9, 1, 2, 5, 10]
    # chromosome = []
    # for chromsome_1 in chromosome_1_options:
    #     for chromsome_2 in chromosome_2_options:
    #         filename = f"{chromsome_1},{chromsome_2}.txt"
    #         filename = os.path.join(output_dir, filename)
    #         with open(filename, "w") as f:
    #             for i in range(1, 11+1):
    #                 f.write(f"{i},{chromsome_1},{chromsome_2}\n")