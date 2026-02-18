from offlineSimStuff.runningTools.runnerHelper import create_jhg_engine
from stagHare.agents.agent import Agent
from stagHare.agents.alegaatr import AlegAATr
from stagHare.agents.cabAgentThing import CabAgent
from stagHare.agents.prey import Prey
from stagHare.agents.qalegaatr import QAlegAATr
from stagHare.environment.state import State
import numpy as np
from typing import List
from stagHare.utils.utils import HARE_NAME, N_HUNTERS, STAG_NAME
from stagHare.environment.allocationTranslator import allocation_to_movement
from stagHare.agents.hareAgent import HareAgent
from stagHare.agents.stagAgent import StagAgent
from stagHare.environment.jhgToStaghunt import jhg_to_staghunt
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

        # ok we are going to need a way to actually process the allocations.
        # lets start at the highest possible level and work our way down.
        # this means no real layer translator -- it won't be the most sensbile but it will get
        # infrastructure in place.
        self.engine = create_jhg_engine(3) # its always 3 players.
        self.popularity_over_time = [[100 for _ in range(len(self.hunters))]] # bars??
        # self.popularity_over_time = [] # bars??


    def transition(self) -> List[float]:
        # we need to split this into an init and 2 stages
        if isinstance(self.agents[4], AlegAATr) or isinstance(self.agents[4], QAlegAATr):
            rewards = self.transition_ethan()
        else:
            rewards = self.transition_sean()
        return rewards # PLEASE PLEASE PLEASE.


    def transition_sean(self):
        # first, lets just set and init some stuff.
        action_map, hunting_hare_map = {}, {}
        round_num = self.state.round_num
        rewards = [0] * len(self.agent_names)
        # there has GOT to be a more elegant way to do this. I swear.
        for agent in self.agents:
            if isinstance(agent, CabAgent):
                agent.set_helpers(self.engine) # sets all the JHG engine stuff.

        # first, lets run the JHG to staghunt portion

        action_map, hunting_hare_map, old_allocations = jhg_to_staghunt(self.agents, self.state, rewards,
                                                                        round_num)  # this does contain the hare and stag.

        # print("These were the old allocations ", old_allocations)
        # print("This was the hunting hare map \n", hunting_hare_map)

        # now, we need to actually execute the moves.

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
        # print("Here were the interpreted allocations \n", allocations)
        self.update_engine(allocations, round_num)

        influence = self.engine.get_influence()
        # print("here is the current influence: \n", influence) # not sure how much this will actually tell me.
        return self.rewards  # return the rewards.


    def update_action_map(self, action_map) -> dict:
        pass

    def update_engine(self, allocations, round_num):

        influence_matrix = self.iterate_engine(allocations, round_num, self.hunters, 3)
        self.popularity_over_time.append(self.engine.get_popularity())





    # this was my semi updated one. it works, albeit its just a proof of concept.
    # the concept has been proven. time to throw the wrench at it.
    # def transition(self) -> List[float]:
    #     # Randomize the order in which the agents will act
    #     indices = list(range(len(self.agents)))
    #     # np.random.shuffle(indices) # lets add this bakc in later, but for now keep it out.
    #     action_map, hunting_hare_map = {}, {}
    #     round_num = self.state.round_num
    #
    #     total_allocations = []
    #
    #     for i in indices:
    #         agent = self.agents[i]
    #
    #         reward = 0 if (i == 0 or i == 1) else self.rewards[i]
    #         # this where stuff gets... strange.
    #         # leave this as is, as the HareAgent and StagAgent are essentially cats and social welfare.
    #         if isinstance(agent, HareAgent) or isinstance(agent, StagAgent):
    #             id = int(agent.name[-1]) # this won't work for more than 10 agents. keep that in mind.
    #             new_allocation = agent.create_allocation(i, self.state)
    #             new_row, new_col, movement_type = allocation_to_movement(new_allocation, id, self.state)
    #             total_allocations.append(new_allocation)
    #
    #         # this is where the real modifications come in clutch.
    #         elif isinstance(agent, CabAgent):
    #             id = int(agent.name[-1])
    #             agent.set_helpers(self.engine)
    #             new_allocation = agent.act(self.state, reward, round_num)
    #             # print("id: ", id, " new_allocation: ", new_allocation)
    #             new_row, new_col, movement_type = allocation_to_movement(new_allocation, id, self.state)
    #             agent.set_hunt(movement_type)
    #             total_allocations.append(new_allocation)
    #
    #
    #         else:
    #             new_row, new_col = agent.act(self.state, reward, round_num)
    #
    #
    #         action_map[agent.name] = (new_row, new_col)
    #         hunting_hare_map[agent.name] = agent.is_hunting_hare()
    #
    #     influence_matrix = self.iterate_engine(total_allocations, round_num, self.hunters, 3)
    #     self.popularity_over_time.append(self.engine.get_popularity())
    #
    #     # print('this here be the influence matrix ', influence_matrix)
    #
    #
    #     if not self.is_over():
    #         self.state.update_intent(hunting_hare_map)
    #         self.rewards = self.state.process_actions(action_map)
    #
    #     return self.rewards



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
