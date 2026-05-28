from Server.Engine.completeBots.humanagent import HumanAgent
from legacy.outDated.jhg_tools import popularity_over_time
from offlineSimStuff.runningTools.runnerHelper import create_jhg_engine
from stagHare.agents.agent import Agent
from stagHare.agents.cabAgentThing import CabAgent
from stagHare.agents.fetcherBot import FetcherBot
from stagHare.agents.hareAgent import HareAgent
from stagHare.agents.prey import Prey
from stagHare.agents.stagAgent import StagAgent
from stagHare.environment.state import State
import numpy as np
from typing import List

from stagHare.loggingStuff.stagHareLogger import GameInformationObject
from stagHare.utils.utils import HARE_NAME, N_HUNTERS, STAG_NAME
from stagHare.environment.jhgToStaghunt import *
from stagHare.environment.staghuntToJHG import *
from copy import deepcopy

class StagHare:
    def __init__(self, height: int, width: int, hunters: List[Agent]) -> None:

        self.height = height
        self.width = width
        # I don't really want to keep track of the actual hunter objects, there's gotta be a better way to do that.

        # Make sure we can set the grid up properly
        n_hunters = len(hunters)

        if n_hunters != N_HUNTERS:
            raise Exception(f'There have to be {N_HUNTERS} hunters')

        if height * width < n_hunters + 2:
            raise Exception(f'Not enough cells in the grid for the hare, stag, and {n_hunters} hunters')

        # Generate a list of agents (the hunters, hare, and stage)
        self.agents = [Prey(HARE_NAME), Prey(STAG_NAME)] + hunters
        self.hunters = hunters # I just want this somewhere. this makes sense to me.

        # Initialize the state and rewards
        self.agent_names = [agent.name for agent in self.agents]
        self.state = State(height, width, self.agent_names)
        self.rewards = [0] * len(self.agent_names)
        self.new_action_map = None

        # ok we are going to need a way to actually process the allocations.
        # lets start at the highest possible level and work our way down.
        # this means no real layer translator -- it won't be the most sensbile but it will get
        # infrastructure in place.
        self.engine = create_jhg_engine(3) # its always 3 players.
        self.popularity_over_time = [[100 for _ in range(len(self.hunters))]] # bars??

        self.coop_success_list = []
        self.agent_positions_list = []
        self.intent_list = [] # we can get the hare intent percent per player from this actually.
        self.hunting_hare_map = {} # this is gonna be a dict, just wait around for it.
        self.scores = []
        self.allocations = [] # I will need some sort of var that controls when this gets activated, becuase this is a lot of information to store otherwise.



    def create_intents_from_hunting_hare_map(self, hunting_hare_map):
        intents = [[] for _ in range(3)]
        for key in hunting_hare_map:
            if key not in ("stag", "hare"):
                index = int(key[-1])
                intents[index] = 0 if hunting_hare_map[key] == False else 1

        return intents

    # this is better -- it still has a bad code smell tho. Might want to separate this out.
    def update_intents_and_get_rewards(self, action_map, hunting_hare_map):
        if not self.is_over():
            self.state.update_intent(hunting_hare_map) # make sure it can understand who killed what.
            self.rewards = self.state.process_actions(action_map)
            self.hunting_hare_map = hunting_hare_map
            self.intent_list.append(self.create_intents_from_hunting_hare_map(hunting_hare_map))
            self.popularity_over_time.append(self.engine.get_popularity())

        return self.rewards  # return the rewards.


    # TODO: make sure this gets thrown in the actual functino somewhere before I forget.
    def update_agent_positions(self, agent_positions):
        # update intents
        # go ahead and ask the engine for the current popularity
        self.agent_positions_list.append(agent_positions)



    # the reality of this is, this supports both already. not a good reason to not just have it all route through here.
    # this si the version with uncertainty.

    def set_final_variables(self) -> None:
        if self.state.hare_captured():
            # capturing the hare means no cooperation
            self.coop_success_list.append(0)
        else:
            # capturing the stag means cooperation.
            self.coop_success_list.append(1)
        self.scores.append(self.create_new_score())

    # transition function that has been retrofitted to also do JHG stuff.
    def transition(self):
        round_num = self.state.round_num
        rewards = [0] * len(self.agent_names)
        for agent in self.agents:
            if isinstance(agent, CabAgent):
                agent.set_helpers(self.engine)

        # jhg_to_staghunt returns moves, hunting_hare_map, and the raw allocations (dict)
        action_map, hunting_hare_map, raw_allocations = jhg_to_staghunt(
            self.agents, self.state, rewards, round_num, self.engine
        )

        self.action_map = action_map
        old_agent_positions = self.state.agent_positions.copy()
        old_state = deepcopy(self.state)

        if not self.is_over():
            self.state.update_intent(hunting_hare_map)
            self.rewards = self.state.process_actions(action_map)

        # --- REPLACE the staghunt_to_jhg call with direct raw allocation passing ---
        # raw_allocations is a dict like {"H0": vec, "H1": vec, "H2": vec}
        # Build an ordered list that the engine expects (player 0, player 1, player 2)
        allocation_list = [None, None, None]
        for agent_name, alloc_vector in raw_allocations.items():
            idx = int(agent_name[-1])  # "H0" -> 0, "H1" -> 1, "H2" -> 2
            allocation_list[idx] = alloc_vector

        # (Optional) Normalise if needed – but the pure JHG code does NOT normalise before
        # play_round(), so leaving the raw vector exactly as is should be fine.
        # If you find the engine behaves oddly, uncomment the next two lines:
        # for i, alloc in enumerate(allocation_list):
        #     allocation_list[i] = [x / sum(abs(alloc)) for x in alloc]

        # Send the exact same allocations the agents intended directly to the engine
        if allocation_list != [None, None, None]: # make sure that the agents actually made allocations.
            # this won't handle mixes well but I don't care!
            self.update_engine(allocation_list, round_num)
        # ---------------------------------------------------------------------------
        # print("Here is the current influence ", self.engine.engine.get_influence())
        return self.rewards, allocation_list, old_agent_positions




    def update_engine(self, allocations, round_num):
        self.iterate_engine(allocations, round_num, self.hunters, 3)

        # need:
        # scneario type (under the init actually) and agent names and hunters (kind of? I shouldn't need the actual hunter object, just the names) height, width
        # coop score is now a list of successes vs non successes
        # scores per player is a different fucntion
        # hare intent percent player is here
        # agent positions needs to be kept track of on every frame
        # end popularities is weird, we do need to keep track of the popularity over time
        # intents. BOOM.


    def get_action_map(self):
        return self.action_map


    # # This was for Ethan's transition algorithm. I'm gonna need to tweak it a fair bit
    def transition_ethan(self) -> List[float]:
        # Randomize the order in which the agents will act
        indices = list(range(len(self.agents)))
        np.random.shuffle(indices)
        action_map, hunting_hare_map = {}, {}
        round_num = self.state.round_num

        for i in indices:
            agent = self.agents[i]
            reward = 0 if (i == 0 or i == 1) else self.rewards[i]
            new_row, new_col = agent.act(self.state, reward, round_num)
            action_map[agent.name] = (new_row, new_col)
            hunting_hare_map[agent.name] = agent.is_hunting_hare()

        if not self.is_over():
            self.state.update_intent(hunting_hare_map)
            self.rewards = self.state.process_actions(action_map)

        return self.rewards

    def iterate_engine(self, transactions, curr_round, agents, num_players):
        self.engine.play_round(transactions)
        influence = self.engine.get_influence()
        return influence # this is all we need for now.


    def is_over(self) -> bool:
        # As soon as one of the prey agents is captured, we're done
        # if self.state.stag_captured():
        #     print("STAG DEATH!! WHAT ")
        return self.state.hare_captured() or self.state.stag_captured()

    def return_state(self):
        return self.state

    def get_cooperation_score(self):
        coop_score = sum(self.coop_success_list) / len(self.coop_success_list)
        return coop_score

    def create_new_score(self):
        # optional last round printing thing... I think.
        # current_round_grapher.create_round_graph(stag_hare)

        if self.state.stag_captured():
            return [2, 2, 2]  # stag score

        else:
            # current_game_logger.add_round(stag_hare.state)

            new_score = [0 for _ in range(3)]  # only ever have 3 playuers.
            # gotta figure out WHO did it.
            hare_x, hare_y = self.state.agent_positions["hare"]
            # possible_hare_captures = stag_hare.state.neighboring_positions(hare_x, hare_y)
            possible_hare_captures = self.get_possible_agent_captures(hare_x, hare_y,
                                                                 self.state.height)  # if its not square kill me
            for agent in self.state.agent_positions:
                if agent == "hare" or agent == "stag":
                    pass
                else:
                    agent_position = self.state.agent_positions[agent]
                    if list(agent_position) in possible_hare_captures:
                        id = int(agent[-1])
                        new_score[id] = 1  # add a rabbit to that thing.

            return new_score

    def get_possible_agent_captures(self, hare_x, hare_y, board_size):
        # possible_moves_col = [[0, -1], [0, 1]]
        # possible_moves_row = [[-1, 0], [1, 0]]

        # all possible move combinations
        # col moves        # row moves
        deltas = [[0, -1], [0, 1], [-1, 0], [1, 0]]

        neighboring_moves = []

        for delta in deltas:
            new_x, new_y = hare_x + delta[0], hare_y + delta[1]

            if new_x < 0:
                new_x = board_size - 1
            elif new_x == board_size:
                new_x = 0

            if new_y < 0:
                new_y = board_size - 1
            elif new_y == board_size:
                new_y = 0

            neighboring_moves.append([new_x, new_y])

        return neighboring_moves

    def process_scores(self, scores):

        score_per_player = list(zip(*scores))

        scores_per_player = []  # empty list, will hold tuples.
        for i, player in enumerate(score_per_player):
            new_score = [0 for _ in range(3)]  # three different types of animals
            for entry in player:
                new_score[entry] += 1
            scores_per_player.append(new_score)

        # cooperation_score = sum([2, 2, 2] == score for score in scores) / len(scores)

        # # I should be doing this in a json logger thing but I don't care.
        # print("here was the cooperation score \n", cooperation_score)
        # print("here was the scores per player \n", scores_per_player)
        # print("here were the total scores \n", total_sum_per_player)

        return scores_per_player # ignore the cooperation score



    def get_hare_intent_percent_per_player(self) -> tuple[int, list]:
        current_intents = [self.intent_list] # GOSH I really hope this works.
        # this gets rid of the 2,2,2, which is easier to do when we are still thinking of them as a list of games of rounds of intents.
        filtered_and_flattened = [round_list for game_list in current_intents for round_list in game_list if round_list != [2, 2, 2]]  # https://klipy.com/gifs/steamed-hams-aurora-borealis--k01KRPQ1FRHG7YGM0DP1D247NG5
        # this just then gets me the raw score.
        transposed = list(zip(*filtered_and_flattened))
        new_sum = np.sum(transposed, axis=1)
        num_rounds = len(filtered_and_flattened)
        column_percentages = new_sum / num_rounds
        return column_percentages  # we ONLY want the column ones. for reasons.

    def get_game_information(self):
        scenario_type = "TODO: FINISH THIS"
        cooperation_score = self.get_cooperation_score()
        scores_per_player = self.process_scores(self.scores) # I THINK?? that works?
        agent_names = ["", "", ""] # TODO: add this
        hare_intent_percent_player = self.get_hare_intent_percent_per_player()
        agent_positions = self.agent_positions_list.copy()
        end_popularities = self.popularity_over_time[-1].copy() # I think thats how that works.
        hunters = [] # I DON"T WANNA.


        game_information = GameInformationObject(scenario_type, cooperation_score, scores_per_player, agent_names,
                                                 hare_intent_percent_player, agent_positions, end_popularities, hunters,
                                                 self.height, self.width, self.intent_list, self.popularity_over_time)

        return game_information



def allocations_dict_to_list(allocations_dict):
    new_allocations = [v for k, v in sorted(allocations_dict.items(), key=lambda x: int(x[0][1:]))]
    return new_allocations # IDK if this works all the way, I'll have to debug it. Grr.