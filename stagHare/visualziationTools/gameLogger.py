
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
        self.scores = []



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

        new_score = self.create_new_score(new_state)
        self.scores.append(new_score)
        return new_score

    def create_new_score(self, new_state):
        # optional last round printing thing... I think.
        # current_round_grapher.create_round_graph(stag_hare)

        if new_state.stag_captured():
            return [2, 2, 2]  # stag score

        if new_state.hare_captured():
            # current_game_logger.add_round(stag_hare.state)

            new_score = [0 for _ in range(3)]  # only ever have 3 playuers.
            # gotta figure out WHO did it.
            hare_x, hare_y = new_state.agent_positions["hare"]
            # possible_hare_captures = stag_hare.state.neighboring_positions(hare_x, hare_y)
            possible_hare_captures = get_possible_agent_captures(hare_x, hare_y,
                                                                 new_state.height)  # if its not square kill me
            for agent in new_state.agent_positions:
                if agent == "hare" or agent == "stag":
                    pass
                else:
                    agent_position = new_state.agent_positions[agent]
                    if list(agent_position) in possible_hare_captures:
                        id = int(agent[-1])
                        new_score[id] = 1  # add a rabbit to that thing.

            return new_score


def get_possible_agent_captures(hare_x, hare_y, board_size):
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
