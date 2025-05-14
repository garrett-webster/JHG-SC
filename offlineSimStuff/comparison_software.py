# the purpose of this program is to take in json and compare how close they are
# I think we should just focus on the comparison of votes between the two
# we will still need a way to custom set the current options matrix before every round
# from the other json
# so lets get it
import os
import json
from Server.social_choice_sim import Social_Choice_Sim # gets me the actual sim
from Server.simLogger import simLogger
from offlineSimStuff.variousGraphingTools.fromJsonToGraph import create_stuff # tis just a funciton but here we are
import textdistance
from datetime import datetime

if __name__ == "__main__":

    directory = "../../JHG-SC/Server/sc_logs_repo" # once again
    now = datetime.now()
    filename = datetime.now().strftime("%Y%m%d_%H%M%S") + "human_study_results.json"
    filepath = os.path.join(directory, filename)
    with open(filepath, 'r') as f:
        big_boy_data = json.load(f)

    old_votes_json = {}


    # lets get some defaults up in this mess
    total_players = 11
    num_causes = 3
    num_humans = 0
    cycle = 0
    round = 0
    chromosomes = ""
    scenario = ""
    group = ""


    for round in big_boy_data:
        if round != "Conclusion":
            current_fetcher = big_boy_data[round]["all_votes"]
            #current_fetcher["winning_vote"] = big_boy_data[round]["winning_vote"] # get rid of the winningVote for now
            old_votes_json[round] = current_fetcher

        elif round == "Conclusion":
            total_players = len(big_boy_data["Conclusion"]["bot_type"]) # bot typoe is measling heere, contains the player padding as well.
            num_causes = 3 # not gonna work backwards on that one.
            num_humans = 0 # this is testing bot preformance
            cycle = -1
            round = -1
            chromosomes = big_boy_data["Conclusion"]["chromosome"]
            chromosomes =  r"C:/Users/Sean/Documents/GitHub/OtherGarrettStuff/JHG-SC/offlineSimStuff/chromosomes/" + chromosomes
            # well this is going to be an ABSOLLUTE royal pain. need to make sure that this file path mathces. Grr.

            scenario = big_boy_data["Conclusion"]["scenario"]
            scenario =  r"C:/Users/Sean/Documents/GitHub/OtherGarrettStuff/JHG-SC/offlineSimStuff/scenarioIndicator/" + scenario
            group = "" # no groups, at least for now)
        else:
            print("Aight this is the round ", round)

    new_sim = Social_Choice_Sim(total_players, num_causes, num_humans, cycle, round, chromosomes, scenario, group)
    new_sim.set_group(group)
    curr_logger = simLogger(new_sim)
    num_cycles = 3 # TODO: change this to actually pull from json instead of hard coding.

    new_votes_json = {}

    for curr_round in big_boy_data:
        if curr_round != "Conclusion": # don't run the last round, doesn't actually mean anything.
            current_options_matrix = big_boy_data[curr_round]["current_options_matrix"]
            new_sim.start_round() # creates player nodes and new options matrix - ovveride options matrix.
            new_sim.set_new_options_matrix(current_options_matrix)
            bot_votes = {}
            for cycle in range(num_cycles): # might actually need to extrapolate this from json
                bot_votes[cycle] = new_sim.get_votes(bot_votes, curr_round, cycle)
                # can graph stuff here. lets jsut write it to json and call it a day.

            bot_votes = bot_votes[num_cycles-1]
            current_fetcher = bot_votes

            new_sim.return_win(bot_votes)
            new_sim.save_results()
            new_sim.set_rounds(int(curr_round)) # set the max round in to allow us to map out the cooperation score, make sure to map to int
            curr_logger.add_round_to_sim(curr_round)

    filename = "machine_comparison"

    curr_logger.finish_json(filename) # this should write everything where I want it to go. maybe. # make sure it doesn't overwrite!

    filename += ".json"



    # now I need to assemble the big dict
    directory = "../../JHG-SC/Server/sc_logs_repo"
    filepath = os.path.join(directory, filename)


    with open(filepath, 'r') as f:
        new_boy_data = json.load(f)

    for curr_round in new_boy_data:
        if curr_round != "Conclusion":
            current_fetcher = new_boy_data[curr_round]["all_votes"]
            #current_fetcher["winning_vote"] = new_boy_data[curr_round]["winning_vote"] # get rid of the wining_vote for now
            new_votes_json[curr_round] = current_fetcher


    # ok lets flatten these votes
    flattened_old_votes = []
    flattened_new_votes = []
    for round in old_votes_json:
        for vote in old_votes_json[round]:
            flattened_new_votes.append(str(new_votes_json[round][vote]))
            flattened_old_votes.append(str(old_votes_json[round][vote]))

    #distance = textdistance.levenshtein.distance(flattened_old_votes, flattened_new_votes) # distance doesn't make any sense in this context. here for reference only.
    similarity = textdistance.levenshtein.normalized_similarity(flattened_old_votes, flattened_new_votes)

    print("old ", flattened_old_votes)
    print("new ", flattened_new_votes)

    print(f"Normalized similarity: {similarity:.2f}")
