from tqdm import tqdm

from offlineSimStuff.runningTools.runnerHelper import create_jhg_sim, create_total_order, create_jhg_engine
from stagHare.agents.cabAgentThing import CabAgent
from stagHare.agents.fetcherBot import FetcherBot
from stagHare.environment.world import StagHare
from stagHare.environment.allocationTranslator import allocation_to_movement, movement_to_allocation
from stagHare.loggingStuff.stagHareLogger import stagHareLogger
from stagHare.visualziationTools.batchLogger import BatchLogger
from stagHare.visualziationTools.inviduvalRoundGrapher import IndividualRoundGrapher
from stagHare.visualziationTools.gameGrapher import GameGrapher
from stagHare.visualziationTools.gameLogger import GameLogger


# so what do we actually need to do
# lets create some cab agents
# and get them to play this fetcher
# we also need to work on the trnaslation machinery as well
# so that will be interesting.
# this is going ot be strange bc the simulator is VERY different from what I have worked with before
# the SC sim I created and the JHG sim was sort of built for cab agents
# this one has not been built for either of those things.


from stagHare.runnerHelper import *

if __name__ == '__main__':

    height, width = 16, 16 # lets start there, not too big but there.
    forced_random = True
    random_agents = True # better for human distribution

    num_players = 3 # as dictated by the stag hare thing
    num_humans = 0 # yeah...

    num_attempts = 1 # don't worry about this

    # with that out of the way, its time to angrily insert the logger in here.
    curr_logger = stagHareLogger()

    # agent_names = ["6x6Round1.csv", "gen_Z.csv", "homoJHGSelfPlay.csv", "homoSCselfPlayMFalse.csv", "homoSCselfPlayMTrue.csv", "mixedJHGSelfPlay.csv", "mixedSCselfPlayMFalse.csv", "mixedSCselfPlayMTrue.csv"]
    agent_names = ["6x6Round3.csv"]

    # keep this as cab for now. we will figure out the rest later.
    # this only works assuming that we are doing self play. use the agent scenario instead.
    agent_type = 3 # -1 is ALLEGATR, 0 is a random agent, 1 is the hare greedy agent, 2 is stag greedy agent, 3 is CAB
    # 0 is standard, 1 is nothing, 2 is 2 of whatever bots with a fectcher bot, 3 is a cab with 2 stag and 4 is a cab with 2 hares.
                                                                     # 5 is 2 cabs with 1 stag and 6 is 2 cabs with 1 hare.
    agent_scenario = 0 # normal whatever I say goes type beat.
    scores = []
    intents = []

    num_rounds_per_game = 10 # lets start here.

    for agent_name in agent_names:
        # print("Agent name: " + agent_name)
        current_batch_logger = BatchLogger()

        for attempt in range(num_attempts):
            current_game_logger = GameLogger(height, width) # need this per game, not per batch.
            hunters = create_hunters(agent_type, random_agents, forced_random, agent_name, agent_scenario)
            current_round_grapher = IndividualRoundGrapher()

            while True:
                stag_hare = StagHare(height, width, hunters)
                if not stag_hare.is_over():
                    break


            for i in range(num_rounds_per_game):

                # does this suck? possibly.
                stag_hare.state.hunting_hare_map = {"R"+str(i) : 2 for i in range(3)} # value that it can never be, sort of a NAN.

                # just run the fetcher.
                new_score, new_intents = run_trial_graphing(stag_hare, current_round_grapher, current_game_logger)

                # just set up a new state that doesn't break immediatel.y
                while True:
                    stag_hare.state.reset_positions() # maybe this will work?
                    if not stag_hare.is_over():
                        break

                scores.append(new_score)
                intents.append(new_intents)
                current_batch_logger.add_game(stag_hare)


            game_grapher = GameGrapher(stag_hare)

            # game_grapher.playback_game(current_game_logger)
            game_grapher.create_game_graph(current_game_logger)

        cooperation_score, scores_per_player = process_scores(scores)
        print(len(intents))  # how many games?
        print(len(intents[0]))  # how many rounds in first game?
        print(intents[0][0])  # what does one round look like?
        hare_intent_percent_total, hare_intent_percent_player = process_intents(intents)
        curr_logger.add_information_game(agent_scenario, cooperation_score, scores_per_player, agent_name, hare_intent_percent_total, hare_intent_percent_player)


