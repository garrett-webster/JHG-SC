import math
import matplotlib.pyplot as plt
import copy


class GroupGrapher():
    def __init__(self):
        pass
        self.rad = 1 # just go with something ig.

    def create_graph(self, group_data):
        print("this is the len of group_data ", len(group_data))
        group_data_transposed = list(zip(*group_data)) # we want the data by player and then by round, so we fix the matrix to do that for us.
        num_players = len(group_data_transposed) # how many players (rows) we are going to have
        num_rounds = len(group_data_transposed[0]) # how many columns (rounds) we are going to have
        positions = self.create_circle_positions(num_players) # creates the positions in a circle for hte nodes that we are looking for
        # basically in each "cell" we will have a circular graph of nodes as dictated by the functions below. I want those thne stacked in rows for players and columsn for rounds.
        fig, axs = plt.subplots(num_players, num_rounds, figsize=(3 * num_rounds, 3 * num_players))

        for row_idx, player in enumerate(group_data_transposed):
            for col_idx, curr_round in enumerate(player):
                ax = axs[row_idx, col_idx]
                self.draw_circle_graph(ax, curr_round, positions, row_idx)
                ax.set_xticks([])
                ax.set_yticks([])
                ax.set_xlim(-1.5, 1.5)
                ax.set_ylim(-1.5, 1.5)
                ax.set_aspect("equal")

        plt.tight_layout()
        plt.show()

    def draw_circle_graph(self, ax, round_data, positions, player_id):
        """Draws only black dots at fixed positions for players active in the round."""
        active_players = range(len(round_data))  # indexes of players in this group

        for i in active_players:
            if i == player_id:
                x,y = positions[-1]
            else:
                x, y = positions[i]
            ax.plot(x, y, 'ko')  # black dot at that player's fixed position

    def create_circle_positions(self, num_players):

        displacement = (2 * math.pi) / num_players  # need an additional "0" cause.
        new_positions = []
        for i in range(num_players):  # 3 is the number of causes
            new_x = math.cos(displacement * i) * self.rad
            new_y = math.sin(displacement * i) * self.rad
            new_positions.append((new_x, new_y)) # make this a tuple
        new_positions.append((0, 0)) # have a zero tuple for when we need to zero something out.

        return new_positions  # no need to return the midpoints


