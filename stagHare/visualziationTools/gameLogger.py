
class GameLogger():
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.game_history = {}
        # tracks all teh PLAYER intents across rounds (like who they are hunting)
        self.hare_hunting_history = []
        # Tracks everones positosn over time and we will use them to create a vector
        self.position_history = {}
        list = ["R0", "R1", "R2", "hare", "stag"]
        for agent in list:
            self.position_history[agent] = [] # give it a list
        self.rounds = 0



    def add_round(self, new_state):
        # we need to strip it to make our life easier to work with
        new_list = []
        for key in new_state.hunting_hare_map:
            if key not in ("hare", "stag"): # we aren't interested in their nefarious purposes
                # new_constant = 0 if new_state.hunting_hare_map[key] == 0 else 1
                if new_state.hunting_hare_map[key] == 0:
                    new_constant = 0
                elif new_state.hunting_hare_map[key] == 1:
                    new_constant = 1
                else:
                    new_constant = 2 # something is wrong, whatever, happens.
                new_list.append(new_constant) # just add what we are looking at
        self.hare_hunting_history.append(new_list)
        for agent in new_state.agent_positions:
            self.position_history[agent].append(new_state.agent_positions[agent])
        self.rounds += 1
