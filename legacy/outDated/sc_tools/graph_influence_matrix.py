import numpy as np
from Client.combinedLayout.ui_functions.StudyScripts.network import NodeNetwork # just for graphing the influence matrix node edges.
from Client.combinedLayout.colors import COLORS
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import to_rgba

class influenceGrapher:
    def __init__(self, num_players):
        self.num_players = num_players

    def create_graph(self, I, results_sums, curr_round):
        # make sure that results sums is insialized to 0
        curr_I = np.array(I[curr_round])  # make this an array as well.
        net = NodeNetwork()
        net.setupPlayers([f"{i}" for i in range(np.shape(results_sums)[0])])
        net.initNodes(init_pops=results_sums) # not sure if this is actually getting used the way that I think its getting used, but we are sure trying.
        net.update(curr_I, results_sums)

        node_positions = np.array([node.position[-1] for node in net.nodes])

        fig, ax = plt.subplots(figsize=(8, 8))
        for i, (x, y) in enumerate(node_positions):
            color = COLORS[i % len(COLORS)]
            ax.scatter(x, y, s=150, c=color, edgecolors="none", zorder=2)
            ax.text(x, y, str(i), fontsize=10, ha="center", va="center", color="black", zorder=3)

        min_weight = np.min(np.abs(curr_I))
        max_weight = np.max(np.abs(curr_I))

        def get_edge_color_and_opacity(weight):
            if max_weight != min_weight:
                normalized = (abs(weight) - min_weight) / (max_weight - min_weight)
            else:
                normalized = 0
            color = (0, 1, 0) if weight > 0 else (1, 0, 0)
            alpha = normalized
            return color, alpha

        segments = []
        colors = []
        for i, node in enumerate(net.nodes):
            for j, weight in enumerate(curr_I[
                                           i]):  # yeah I think this will graph to much, I htink I need to do this at just the mcfreakin uhh curr Round.
                if weight != 0:
                    x0, y0 = node_positions[i]
                    x1, y1 = node_positions[j]
                    color, alpha = get_edge_color_and_opacity(weight)
                    segments.append([(x0, y0), (x1, y1)])
                    colors.append(to_rgba(color, alpha))

        lc = LineCollection(segments, colors=colors, zorder=1)
        ax.add_collection(lc)

        ax.set_aspect("equal")
        ax.axis("off")
        plt.tight_layout()
        plt.show()