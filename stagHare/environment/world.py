from offlineSimStuff.runningTools.runnerHelper import create_jhg_engine
from stagHare.agents.agent import Agent
from stagHare.agents.cabAgentThing import CabAgent
from stagHare.agents.prey import Prey
from stagHare.environment.state import State
import numpy as np
from typing import List
from stagHare.utils.utils import HARE_NAME, N_HUNTERS, STAG_NAME
from stagHare.environment.jhgToStaghunt import jhg_to_staghunt, \
    allocation_to_intent  # allocation_to_intent is no longer something we use, ignore it.
from stagHare.environment.staghuntToJHG import staghunt_to_jhg
from copy import deepcopy

class StagHare:
    def __init__(self, height: int, width: int, hunters: List[Agent]) -> None:
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
        # self.popularity_over_time = [] # bars??

    def transition_debug(self):
        # we need to split this into an init and 2 stages
        # if ethan_bool: # or isinstance(self.agents[4], QAlegAATr):
        #     rewards = self.transition_ethan()
        # print("using ethans transition function")
        # else:
        # ok so
        # I think the way to make this work is as follows:
        # this is for anything that has to do with the cab agents.
        # if you want it NOT to od that, use hte other code.
        # else:
        # print("using seans transition function")
        rewards = self.transition_sean_debug()

        return rewards  # PLEASE PLEASE PLEASE.

    def transition_sean_debug(self):
        round_num = self.state.round_num
        rewards = [0] * len(self.agent_names)
        for agent in self.agents:
            if isinstance(agent, CabAgent):
                agent.set_helpers(self.engine)  # sets all the JHG engine stuff.

        # first, lets run the JHG to staghunt portion
        action_map, hunting_hare_map, old_allocations = jhg_to_staghunt(self.agents, self.state, rewards,
                                                                        round_num)  # this does contain the hare and stag.

        self.action_map = action_map
        old_agent_positions = self.state.agent_positions.copy()  # make a copy of this, trust me.
        old_state = deepcopy(self.state)  # this SHOULD work?
        # process the actions IG

        if not self.is_over():
            self.state.update_intent(hunting_hare_map)
            self.rewards = self.state.process_actions(action_map)

        # turn this into something that the JHG engine can understand and slam that through. or something like that.
        hare_captured = self.state.hare_captured  # we use this for the differing hare allocation upon capture. Not sure if it really matters.
        allocations = staghunt_to_jhg(self.state, action_map, old_agent_positions, old_state,
                                      hare_captured)  # need the action map to do things.

        new_intents = [-1 for _ in range(len(self.hunters))]
        for i, allocation in enumerate(allocations):
            # this returns 0 - 3
            new_intents[i] = (allocation_to_intent(allocation, i, len(self.hunters)))

        self.update_engine(allocations, round_num)

        return self.rewards, new_intents  # return the rewards.

    # this is the version that just passes everything straight through.
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
        self.update_engine(allocation_list, round_num)
        # ---------------------------------------------------------------------------
        # print("Here is the current influence ", self.engine.engine.get_influence())
        return self.rewards


    # the reality of this is, this supports both already. not a good reason to not just have it all route through here.
    # this si the version with uncertainty.
    def transition_noisy(self):

        round_num = self.state.round_num
        rewards = [0] * len(self.agent_names)
        # there has GOT to be a more elegant way to do this. I swear.
        for agent in self.agents:
            if isinstance(agent, CabAgent):
                agent.set_helpers(self.engine) # sets all the JHG engine stuff.

        # first, lets run the JHG to staghunt portion
        action_map, hunting_hare_map, old_allocations = jhg_to_staghunt(self.agents, self.state, rewards,
                                                                        round_num, self.engine)  # this does contain the hare and stag.

        self.action_map = action_map
        old_agent_positions = self.state.agent_positions.copy()  # make a copy of this, trust me.
        old_state = deepcopy(self.state)  # this SHOULD work?
        # process the actions IG

        if not self.is_over():
            self.state.update_intent(hunting_hare_map)
            self.rewards = self.state.process_actions(action_map)

        # turn this into something that the JHG engine can understand and slam that through. or something like that.
        hare_captured = self.state.hare_captured  # we use this for the differing hare allocation upon capture. Not sure if it really matters.
        allocations = staghunt_to_jhg(self.state, action_map, old_agent_positions, old_state,
                                      hare_captured)  # need the action map to do things.


        self.update_engine(allocations, round_num)
        # print("Here is the current influence ", self.engine.engine.get_influence())

        return self.rewards  # return the rewards.


    def update_action_map(self, action_map) -> dict:
        pass

    def update_engine(self, allocations, round_num):

        influence_matrix = self.iterate_engine(allocations, round_num, self.hunters, 3)
        self.popularity_over_time.append(self.engine.get_popularity())


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
        return self.state.hare_captured() or self.state.stag_captured()

    def return_state(self):
        return self.state
