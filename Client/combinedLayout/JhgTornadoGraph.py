import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from Client.combinedLayout.colors import COLORS


class JhgTornadoGraph(FigureCanvas):
    def __init__(self, num_players):
        self.figure = Figure(figsize=(5, 4), dpi=100)
        super().__init__(self.figure)
        self.num_players = num_players
        self.figure.patch.set_facecolor("#282828")
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor("#282828")
        self.ax.tick_params(color="#EBEBEB")
        self.ax.xaxis.set_tick_params(labelcolor="white")  # Set x-axis tick labels to white
        self.ax.yaxis.set_tick_params(labelcolor="white")  # (Optional) Set y-axis tick labels to white
        for spine in self.ax.spines.values():
            spine.set_color("#EBEBEB")


    def update_jhg_tornado(self, influence_mat, init_pop_influence):
        self.ax.cla()
        y_positions = np.arange(self.num_players)[::-1]
        max_extent = 0  # To determine symmetric x-axis limits
        x_to_graph = 0


        # Creates a bar for each player
        for current_player in range(self.num_players):
            positive_influence_total = init_pop_influence
            negative_influence_total = 0
            influences = influence_mat[:, current_player]

            self.ax.barh(y_positions[current_player], positive_influence_total, left=0, color="#7a7a7a")
            for player_id, influence in enumerate(influences):
                # Sets where to graph the next bar (whether it should be at the tail of the positive or negative bar)
                if influence > 0:
                    x_to_graph = positive_influence_total
                    positive_influence_total += influence
                elif influence < 0:
                    x_to_graph = negative_influence_total
                    negative_influence_total += influence

                self.ax.barh(y_positions[current_player], influence, left=x_to_graph, color=COLORS[player_id])
                # Update max extent for symmetric x-axis
                max_extent = max(max_extent, abs(positive_influence_total), abs(negative_influence_total))

        # Set symmetric x-axis limits
        self.ax.set_xlim(-max_extent + 100, max_extent)

        # Set labels and title
        self.ax.set_yticklabels([])
        for i, y_pos in enumerate(y_positions):
            self.ax.text(-max_extent * 1.05, y_pos, f"Player {i + 1}", va='center', ha='right', fontsize=10, color=COLORS[i])

        self.ax.axvline(0, color='#EBEBEB', linewidth=2, linestyle='-')
        self.ax.figure.canvas.draw_idle()  # Redraw the figure
