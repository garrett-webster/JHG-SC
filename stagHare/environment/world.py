from stagHare.agents.agent import Agent
from stagHare.agents.alegaatr import AlegAATr
from stagHare.agents.prey import Prey
from stagHare.environment.state import State
import numpy as np
from typing import List
from stagHare.utils.utils import HARE_NAME, N_HUNTERS, STAG_NAME
from stagHare.environment.allocationTranslator import allocation_to_movement
from stagHare.agents.hareAgent import HareAgent
from stagHare.agents.stagAgent import StagAgent


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


    def transition(self) -> List[float]:
        # Randomize the order in which the agents will act
        indices = list(range(len(self.agents)))
        # np.random.shuffle(indices) # lets add this bakc in later, but for now keep it out.
        action_map, hunting_hare_map = {}, {}
        round_num = self.state.round_num

        for i in indices:
            agent = self.agents[i]
            if isinstance(agent, AlegAATr):
                pass # just for refernce rn.

            reward = 0 if (i == 0 or i == 1) else self.rewards[i]
            # this where stuff gets... strange.
            if isinstance(agent, HareAgent) or isinstance(agent, StagAgent):
                id = int(agent.name[-1]) # this won't work for more than 10 agents. keep that in mind.
                new_allocation = agent.create_allocation(i, self.state)
                new_row, new_col = allocation_to_movement(new_allocation, id, self.state)

            else:
                new_row, new_col = agent.act(self.state, reward, round_num)


            action_map[agent.name] = (new_row, new_col)
            hunting_hare_map[agent.name] = agent.is_hunting_hare()

        if not self.is_over():
            self.state.update_intent(hunting_hare_map)
            self.rewards = self.state.process_actions(action_map)

        return self.rewards



    # # This was for Ethan's transition algorithm. I'm gonna need to tweak it a fair bit
    # def transition(self) -> List[float]:
    #     # Randomize the order in which the agents will act
    #     indices = list(range(len(self.agents)))
    #     np.random.shuffle(indices)
    #     action_map, hunting_hare_map = {}, {}
    #     round_num = self.state.round_num
    #
    #     for i in indices:
    #         agent = self.agents[i]
    #         reward = 0 if (i == 0 or i == 1) else self.rewards[i]
    #         new_row, new_col = agent.act(self.state, reward, round_num)
    #         action_map[agent.name] = (new_row, new_col)
    #         hunting_hare_map[agent.name] = agent.is_hunting_hare()
    #
    #     if not self.is_over():
    #         self.state.update_intent(hunting_hare_map)
    #         self.rewards = self.state.process_actions(action_map)
    #
    #     return self.rewards

    def is_over(self) -> bool:
        # As soon as one of the prey agents is captured, we're done
        return self.state.hare_captured() or self.state.stag_captured()

    def return_state(self):
        return self.state
