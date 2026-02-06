from tqdm import tqdm

from offlineSimStuff.runningTools.runnerHelper import create_jhg_sim, create_total_order, create_jhg_engine
from stagHare.agents.cabAgentThing import CabAgent
from stagHare.environment.world import StagHare
from stagHare.environment.allocationTranslator import allocation_to_movement, movement_to_allocation
from stagHare.visualziationTools.batchLogger import BatchLogger
from stagHare.visualziationTools.inviduvalRoundGrapher import IndividualRoundGrapher
from stagHare.visualziationTools.gameGrapher import GameGrapher
from stagHare.visualziationTools.gameLogger import GameLogger
from stagHare.agents.random_agent import Random
from stagHare.agents.hareAgent import HareAgent
from stagHare.agents.stagAgent import StagAgent
from stagHare.agents.alegaatr import AlegAATr # litmus test

from concurrent.futures import ProcessPoolExecutor, as_completed


from stagHare.environment.state import State
# so what do we actually need to do
# lets create some cab agents
# and get them to play this fetcher
# we also need to work on the trnaslation machinery as well
# so that will be interesting.
# this is going ot be strange bc the simulator is VERY different from what I have worked with before
# the SC sim I created and the JHG sim was sort of built for cab agents
# this one has not been built for either of those things.
def run_trial_graphing(stag_hare, current_round_grapher, current_game_logger):
    while True: # the way this gets run is VERY VERY weird.

        current_game_logger.add_round(stag_hare.state)
        # have this generate right off the bat
        # current_round_grapher.create_round_graph(stag_hare)
        rewards = [0] * 5 # 3 hunters, 2 other peeps
        # this is a reminder to check the action map to make sure that we are hunting what we think we are.

        round_rewards = stag_hare.transition()
        for i, reward in enumerate(round_rewards):
            rewards[i] += reward



        if stag_hare.is_over():
            current_game_logger.add_round(stag_hare.state)
            # print("something has been captured! 2")
            # print("Hare? ", stag_hare.state.hare_captured())
            # print("Stag? ", stag_hare.state.stag_captured())
            # current_round_grapher.create_round_graph(stag_hare, True)
            return



def create_hunters(agent_type, agent_name=""):
    new_hunters = []
    for i in range(3):
        new_name = "R" + str(i)

        if agent_type == -1:
            new_hunters.append(AlegAATr(name=new_name, lmbda=0.0, ml_model_type='knn', enhanced=True))

        if agent_type == 0:
            new_hunters.append(Random(name=new_name))

        if agent_type == 1:
            new_hunters.append(HareAgent(name=new_name))

        if agent_type == 2:
            new_hunters.append(StagAgent(name=new_name))

        if agent_type == 3:
            new_hunters.append(CabAgent(i, new_name, agent_name))


    return new_hunters # just make sure to get those new guys in somewhere.


if __name__ == '__main__':

    forcedRandom = True
    random_agents = True # better for human distribution

    # no round list unfortunately, doesn't work that way

    num_players = 3 # as dictated by the stag hare thing
    num_humans = 0 # yeah...
    # for testing purposes right off the bat, lets work with social welfare. that wi
    jhg_bot_type = 2 # 0 is gene bots, 2 is social welfare and 3 is random. 4 is the new social welfare that I am developing that is just a hair smarter.
    num_attempts = 1 # don't worry about this
    # don't add cats yet, we will worry about that later.
    # agent_name = "mixedJHGSelfPlay.csv"
    # agent_names = ["gen_99.csv", "gen_Z.csv", "homoJHGSelfPlay.csv", "homoSCselfPlayMFalse.csv", "homoSCselfPlayMTrue.csv", "mixedJHGSelfPlay.csv", "mixedSCselfPlayMFalse.csv", "mixedSCselfPlayMTrue.csv"]
    agent_names = ["homoJHGSelfPlay.csv"]


    # agents = [CabAgent(i, "H"+str(i), agent_name) for i in range(num_players)] # they need names or something.
    addAgents = []
    new_agents = []

    height, width = 6, 6 # lets start there, not too big but there.
    agent_type = 3 # -1 is ALLEGATR, 0 is a random agent, 1 is the hare greedy agent, 2 is stag greedy agent.


    for agent_name in agent_names:
        print("Agent name: " + agent_name)
        current_batch_logger = BatchLogger()

        for attempt in tqdm(range(num_attempts)):
            current_game_logger = GameLogger(height, width) # need this per game, not per batch.
            total_order = create_total_order(num_players, num_humans)
            current_jhg_engine = create_jhg_engine(num_players)
            # current_jhg_sim = create_jhg_sim(num_humans, num_players, total_order, jhg_bot_type, addAgents, new_agents, current_jhg_engine)
            hunters = create_hunters(agent_type, agent_name)
            current_round_grapher = IndividualRoundGrapher()
            while True:
                stag_hare = StagHare(height, width, hunters)
                if not stag_hare.is_over():
                    break

            # does this suck? possibly.
            stag_hare.state.hunting_hare_map = {"R"+str(i) : 2 for i in range(3)}

            # just run the fetcher.
            run_trial_graphing(stag_hare, current_round_grapher, current_game_logger)
            current_batch_logger.add_game(stag_hare)


            game_grapher = GameGrapher(stag_hare)

            game_grapher.playback_game(current_game_logger)
            game_grapher.create_game_graph(current_game_logger)

        new_num = current_batch_logger.get_results()
        print("the ration of stag to hare was ", new_num, " for agent ", agent_name)
