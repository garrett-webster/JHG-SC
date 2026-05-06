"""
the goal of this script is to make a JHG engine that can run
and then from there, I can test the allocations and whatnot from that JHG script to try and understand intent
I want to see if the staghunt_to_jhg function is broken or what.
steps: get just a jhg game running and make sure it works
track the allocations
run them through the thing, track intents
measure with various bots.
break.
"""
from tqdm import tqdm
from offlineSimStuff.runningTools.runnerHelper import * # get all the functions
from Server.Engine.simulator import GameSimulator
from stagHare.environment.jhgToStaghunt import allocation_to_movement, allocation_to_intent

if __name__ == "__main__":
    bots = ["gen_Z.csv", "gen_199.csv"]
    # bots = ["16x16round4.csv"]
    forcedRandom = True
    enforce_majority = True
    random_agents = True

    num_players = 3
    num_humans = 0

    jhg_bot_type = 0
    num_vanilla_bots = 10

    popularity_to_log = []
    num_attempts = 200
    total_order = create_total_order(num_players,
                                     num_humans)  # unfortunately we have to make that in here now just bc we are changing the num players
    add_agents = [] # make this empty.
    num_rounds = 10
    intents = [[] for _ in range(num_players)] # creates a list of lists


    for bot in bots:
        for attempt in tqdm(range(num_attempts)):
            current_jhg_engine = create_jhg_engine(3) # there are 3 players.

            agents = create_genetic_agents(num_players, [], bot, forcedRandom, random_agents)

            for curr_round in range(num_rounds):
                                    # I am kicking myself for some of these naming conventions lol.
                allocations = run_jhg_stuff_allocations(current_jhg_engine, curr_round, agents, len(agents))
                for i, allocation in enumerate(allocations):

                    intents[i].append(allocation_to_intent(allocation, i, num_players)) # should store things in a list of lists and append to it. maybe.

        coop_scores = np.mean(intents, axis=1)
        print("here are the coop scores ", coop_scores, " for bot ", bot)

