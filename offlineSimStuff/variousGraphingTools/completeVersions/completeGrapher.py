import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch
import matplotlib.gridspec as gridspec
from pathlib import Path
from matplotlib.patches import Patch
import os
import numpy as np # for col sums

from matplotlib.patches import Circle
from itertools import combinations
from pathlib import Path

from Client.combinedLayout.ui_functions.StudyScripts.network import NodeNetwork # just for graphing the influence matrix node edges.
from Client.combinedLayout.colors import COLORS
from matplotlib.collections import LineCollection
from matplotlib.colors import to_rgba
from matplotlib.colors import LinearSegmentedColormap, Normalize
import json


class CompleteGrapher():
    def __init__(self):
        pass

    def create_graphs_with_file(self, file_path):
        # so the JSON saves everything and this is sort fo supposed to get called round by round
        # so breaking this down might be a little weird.
        with open(file_path, "r") as f:
            data = json.load(f)

        for curr_round in data:
            if "JHG_STUFF" in data[curr_round]:
                jhg = data[curr_round].get("JHG_STUFF")
                allocations, popularity, influence, old_popularity = self.extract_keys(jhg, ["T", "Popularity", "Influence", "Old_Popularity"])
                self.create_jhg_graphs(allocations, popularity, influence, curr_round, old_popularity)
            if "SC_STUFF" in data[curr_round]:
                sc = data[curr_round].get("SC_STUFF")
                all_nodes, all_votes, winning_vote_list, current_options_matrix, types_list, scenario, group, curr_round, cycle, chromosome, influence_matrix, results_sums, results, peeps = (
                    self.extract_keys(sc, ["all_nodes", "all_votes", "winning_vote", "current_options_matrix", "types_list", "scenario", "group", "curr_round", "cycle", "chromosome", "influence_matrix", "results_sums", "results", "peeps"]))
                self.create_sc_graphs(all_nodes, all_votes, winning_vote_list, current_options_matrix, types_list, scenario, group, curr_round, cycle, chromosome, influence_matrix, results_sums, results, peeps)

    def create_graph_with_sims(self, curr_round, sc_sim, jhg_sim, sc_played, jhg_played):
        if jhg_played:# very important that this comes first, as we alwas PLAY this one first, makes sure the graphs are printed in the right order. for now. might need to adjust some stuff.
            allocations, popularity, influence, old_popularity = jhg_sim.individual_round_deets_for_logger(curr_round)
            #self.create_jhg_graphs(allocations, popularity, influence, curr_round, old_popularity)

        if sc_played:
            all_nodes, all_votes, winning_vote_list, current_options_matrix, types_list, scenario, group, round, cycle, chromosome, influence_matrix, results_sums, results, peeps = sc_sim.prepare_graph()
            self.create_sc_graphs(all_nodes, all_votes, winning_vote_list, current_options_matrix, types_list, scenario,  group, round, cycle, chromosome, influence_matrix, results_sums, results, peeps)


    def create_sc_graphs(self, all_nodes, all_votes, winning_vote_list, current_options_matrix, types_list, scenario, group, curr_round, cycle, chromosome, influence_matrix, results_sums, results, peeps):
        bot_color_map, bot_name_map = self.build_bot_mappings()
        influence_matrix = np.array(influence_matrix)

        for cycle_key in all_votes.keys():
            curr_votes = all_votes[cycle_key]
            winning_vote = winning_vote_list[cycle_key]

            fig = plt.figure(figsize=(13, 6)) # not entirely sure what those numbers mean.
            gs = gridspec.GridSpec(1, 3, width_ratios=[0.8, 3.0, 1.5])

            ax_matrix = fig.add_subplot(gs[0])
            self.draw_matrix_panel(ax_matrix, current_options_matrix, curr_votes, winning_vote, peeps, results_sums)

            ax_graph = fig.add_subplot(gs[1])
            self.draw_node_graph(ax_graph, all_nodes, curr_votes, winning_vote, types_list, bot_color_map, bot_name_map)

            ax_inf = fig.add_subplot(gs[2])
            self.draw_influence_panel(ax_inf, influence_matrix, results_sums)

            # hopefully this is the exactly the same as before. if not I can check and restore as necessary.
            fig.suptitle(f"Round: {curr_round}  Situation: {scenario}  Cycle: {int(cycle_key) + 1}  Group: {group}", fontsize=16, fontweight='bold', y=0.98)
            # Reduce space between matrix and graph and the overall layout
            fig.subplots_adjust(wspace=0.01, left=0.05, right=0.95, top=0.95, bottom=0.15)  # Adjust bottom margin

            path = self.build_save_path(scenario, group, curr_round, cycle_key)
            self.save_figure(fig, path)

    def extract_keys(self, d, keys, default=None):
        return tuple(d.get(k, default) for k in keys)

    def create_jhg_graphs(self, allocations, popularity, influence, curr_round, old_popularities):

        fig = plt.figure(figsize=(15, 5))
        gs = gridspec.GridSpec(1, 3, width_ratios=[1.2, 2, 2.2])  # L, C, R

        ax_popularity = fig.add_subplot(gs[0])
        self.plot_popularity_changes(ax_popularity, popularity, old_popularities)

        ax_allocations = fig.add_subplot(gs[1])
        self.plot_allocations_matrix(ax_allocations, allocations)

        ax_influence = fig.add_subplot(gs[2])
        self.plot_influence_graph(ax_influence, influence, popularity)

        fig.suptitle(f"Round {curr_round}: Popularity, Allocations, Influence", fontsize=16, weight="bold")
        plt.tight_layout()
        plt.show()

    def draw_matrix_panel(self, ax_matrix, current_options_matrix, curr_votes, winning_vote, peeps, results_sums):
        ax_matrix.axis('off')

        num_rows = len(current_options_matrix)
        matrix_array = np.array(current_options_matrix)
        col_sums = matrix_array.sum(axis=0)
        best_option = int(np.argmax(col_sums)) + 1  # gets the index of the best option and adds one to it
        x_start = 6
        spacing = 3

        for k, creator in enumerate(peeps):
            x = x_start + k * spacing
            ax_matrix.text(x, 1, f"{creator}", ha='left', va='bottom',
                           fontsize=12, fontfamily='monospace', fontweight='bold', color='black')

        # lets put the peeps at the top
        # for i in range(len(peeps)):
        #     player_id = peeps[i]
        #     ax_matrix.text(0, -i*spacing, f"{player_id}:>2 |", ha="left", va="center", fontsize=12, fontfamily='monospace')


        for i in range(num_rows):
            vote = curr_votes.get(i)  # tries to get it through an int first, from real time execution
            if vote is None:  # if that fails, might be string
                vote = curr_votes.get(str(i), "?")  # if the string fails, we're fetched.

            player_id = i + 1
            options = current_options_matrix[i]

            # Use fixed-width formatting for alignment
            ax_matrix.text(0, -i, f"{player_id:>2}, {results_sums[i]} |", ha='left', va='center', fontsize=12,
                           fontfamily='monospace')

            formatted_options = ""
            for k, opt in enumerate(options):
                x = x_start + k * spacing
                color = "black"
                if k == winning_vote:
                    color = "green" if opt > 0 else "red"
                ax_matrix.text(x, -i, f"{opt:>2}", ha='center', va='center', fontsize=12,
                               fontfamily='monospace', color=color)

            ax_matrix.text(x_start + len(options) * spacing, -i, f"| {int(vote + 1):>2}", ha='left', va='center',
                           fontsize=12, fontfamily='monospace', fontweight='bold')

        # code to add teh column sums
        sum_y = -num_rows  # y-coordinate below the last row
        for k, val in enumerate(col_sums):
            x = x_start + k * spacing
            color = "black"
            if winning_vote != 0 and k == winning_vote:
                color = "green"
            ax_matrix.text(x, sum_y, f"{int(val):>2}", ha='center', va='center',
                           fontsize=12, fontfamily='monospace', color=color)


        ax_matrix.text(x_start - spacing, sum_y, "  Σ |", ha='center', va='center',
                       fontsize=12, fontfamily='monospace', fontweight='bold')

        x += spacing
        ax_matrix.text(x, -num_rows, "    |  " + str(winning_vote+1),
                       ha='center', va='center', fontsize=12, fontfamily='monospace', fontweight='bold')

        # Update the plot limits to make space for the sum row + winning vote
        ax_matrix.set_xlim(-1, 10)
        ax_matrix.set_ylim(-num_rows - 3, 2)

        # --- Add Winning Vote Text Below Matrix ---
        ax_matrix.text(1, -num_rows - 1, f"Winning vote: {winning_vote + 1}", ha='left', va='center',
                       fontsize=12, color='red')


    def draw_node_graph(self, ax, all_nodes, curr_votes, winning_vote, types_list, bot_color_map, bot_name_map):
        x_offset = 2
        ax.set_xlim(-12, 12)
        ax.set_ylim(-12, 12)
        ax.set_aspect('equal')
        ax.axis('off')

        node_positions = {node["text"]: (node["x_pos"], node["y_pos"]) for node in all_nodes}
        node_types = {node["text"]: node["type"] for node in all_nodes}
        used_bot_types = set()

        cause_nodes = [node for node in all_nodes if node["type"] == "CAUSE"]
        cause_positions = [(node["x_pos"], node["y_pos"]) for node in cause_nodes]

        # Draw lines between every pair of cause nodes
        for (x1, y1), (x2, y2) in combinations(cause_positions, 2):
            ax.plot([x1+x_offset, x2+x_offset], [y1, y2], color='black', linewidth=2, alpha=0.8, zorder=1)

        for node in all_nodes:
            x, y = node["x_pos"], node["y_pos"]
            label = node["text"]
            node_type = node["type"]
            alpha = 0.5 if node["negatives_flag"] else 1.0

            try:
                number = int(label.split()[-1])
            except ValueError:
                number = label

            if node_type == "CAUSE":
                color = 'red' if label == "Cause " + str(winning_vote + 1) else 'darkgrey'
                shape = patches.RegularPolygon((x+x_offset, y), numVertices=3, radius=1.0, orientation=0,
                                               color=color, ec='black', zorder=2)
                ax.add_patch(shape)
            elif node_type == "PLAYER":
                string = node["text"].split(" ")
                id = types_list[int(string[1]) - 1]
                used_bot_types.add(str(id))
                color = bot_color_map[str(id)]

                shape = plt.Circle((x+x_offset, y), 0.7, color=color, ec='black', zorder=2, alpha=alpha)
                ax.add_patch(shape)

            ax.text(x+x_offset, y, str(number), ha='center', va='center', fontsize=14, weight='bold', zorder=3,
                    alpha=alpha)

        for player_index, vote in curr_votes.items():
            player_label = f"Player {int(player_index) + 1}"
            cause_label = f"Cause {vote + 1}"  # for the off-by-one issue present in the votes.

            if player_label in node_positions and cause_label in node_positions:
                x_start, y_start = node_positions[player_label]
                x_end, y_end = node_positions[cause_label]

                is_winning_vote = cause_label == "Cause " + str(winning_vote + 1)
                arrow_color = 'red' if is_winning_vote else 'gray'

                arrow = FancyArrowPatch((x_start+x_offset, y_start), (x_end+x_offset, y_end),
                                        arrowstyle='->', color=arrow_color,
                                        mutation_scale=15, lw=2, zorder=1)
                ax.add_patch(arrow)

        # creates a legend that allows us to see which bot types are active, and which ones are what
        legend_elements = []

        for bot_type in sorted(used_bot_types):
            label = bot_name_map.get(bot_type, f"Type {bot_type}")
            color = bot_color_map.get(bot_type, bot_color_map["default"])
            legend_elements.append(Patch(facecolor=color, edgecolor='black', label=label))

        # You can put the legend on the right side of the graph area
        ax.legend(handles=legend_elements, loc='lower right', bbox_to_anchor=(1.0, -0.05),
                  ncol=2, fontsize=10, frameon=True, title="Bot Types")


        # print("This is the round at the end!! ", curr_round)

        # Add circle patch behind nodes/arrows
        circle_patch = Circle((0+x_offset, 0), radius=5, edgecolor='black', facecolor='none', linewidth=1,
                              linestyle='--',
                              zorder=0)
        ax.add_patch(circle_patch)
        circle_patch = Circle((0+x_offset, 0), radius=10, edgecolor='black', facecolor='none', linewidth=1,
                              linestyle='--',
                              zorder=0)
        ax.add_patch(circle_patch)

        # Add dotted line "spokes" every 60 degrees
        for angle_deg in range(30, 390, 60):  # 30, 90, 150, ..., 330
            angle_rad = np.deg2rad(angle_deg)
            x = 10 * np.cos(angle_rad)
            y = 10 * np.sin(angle_rad)
            ax.plot([0+x_offset, x+x_offset], [0, y], color='black', linestyle=':', linewidth=1, zorder=0)

    def draw_influence_panel(self, ax, influence_matrix, results_sums):
        net = NodeNetwork()
        net.setupPlayers([f"{i}" for i in range(np.shape(results_sums)[0])])
        net.initNodes(
            init_pops=results_sums)  # not sure if this is actually getting used the way that I think its getting used, but we are sure trying.
        net.update(influence_matrix, results_sums)

        node_positions = np.array([node.position[-1] for node in net.nodes])

        ax.set_aspect("equal")
        ax.axis("off")
        for i, (x, y) in enumerate(node_positions):
            color = COLORS[i % len(COLORS)]
            ax.scatter(x, y, s=150, c=color, edgecolors="none", zorder=2)
            ax.text(x, y, str(i), fontsize=10, ha="center", va="center", color="black", zorder=3)

        min_weight = np.min(np.abs(influence_matrix))
        max_weight = np.max(np.abs(influence_matrix))

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
            for j, weight in enumerate(influence_matrix[
                                           i]):  # yeah I think this will graph to much, I htink I need to do this at just the mcfreakin uhh curr Round.
                if weight != 0:
                    x0, y0 = node_positions[i]
                    x1, y1 = node_positions[j]
                    color, alpha = get_edge_color_and_opacity(weight)
                    segments.append([(x0, y0), (x1, y1)])
                    colors.append(to_rgba(color, alpha))

        lc = LineCollection(segments, colors=colors, zorder=1)
        ax.add_collection(lc)

    def build_save_path(self, scenario, group, curr_round, cycle_key):
        my_path = os.path.dirname(os.path.abspath(__file__))
        scenario_str = f"scenario_{scenario}"
        group_str = f"group_{group}"
        file_name = f"round_{str(int(curr_round))}_cycle_{str(cycle_key)}.png"
        dir_path = os.path.join(my_path, "individualRoundGraphs", scenario_str, group_str)
        os.makedirs(dir_path, exist_ok=True)
        full_path = os.path.join(dir_path, file_name)
        return full_path

    def save_figure(self, fig, path):
        fig.subplots_adjust(wspace=0.01, left=0.05, right=0.95, top=0.95, bottom=0.15)
        fig.savefig(path, dpi=300)
        plt.show()

    def build_bot_mappings(self):
        bot_color_map = {
            # -1 is player, 0 is random, 1 is socialWelfare, 2 is greediest, 3 is betterGreedy, 4 is limitedAwareness, 5 is secondChoice
            "-1": "lightgreen",
            "0": "purple",
            "1": "black",
            "2": "purple",
            "3": "blue",
            "4": "orange",
            "5": "plum",
            "6": "lightblue",
            "7": "darkgreen",
            "8": "green",
            "9": "orange",
            "10": "violet",
            "default": "gray"
        }

        bot_name_map = {
            "-1": "player",
            "0": "random",
            "1": "socialWelfare",
            "2": "Greedy",
            "3": "betterGreedy",
            "4": "limitedAwareness",
            "5": "secondChoice",
            "6": "somewhatMoreAwareness",
            "7": "optimalHuman",
            "8": "humanAttempt2",
            "9": "humanAttempt3",
            "10": "cheetahBot",
        }
        return bot_color_map, bot_name_map

    def plot_popularity_changes(self, ax_popularity, popularity, old_popularities):
        ax_popularity.clear()
        ax_popularity.axis('off')  # Hide axes

        n = len(popularity)

        # Headers
        headers = ["Plyr", "Old", "New", "Delta"]
        col_x = [0, 1, 2, 3]
        y_start = 0

        # Plot headers
        for col, header in zip(col_x, headers):
            ax_popularity.text(col, y_start, header, fontsize=12, fontweight='bold', ha='center', va='bottom')

        # Plot each player's data, one row per player
        for i in range(n):
            y = y_start - (i + 1)  # rows go downwards

            old_pop = old_popularities[i]
            new_pop = popularity[i]
            change = new_pop - old_pop

            # Player index
            ax_popularity.text(col_x[0], y, str(i + 1), ha='center', va='center')
            # Old popularity
            ax_popularity.text(col_x[1], y, f"{old_pop:.3f}", ha='center', va='center')
            # New popularity
            ax_popularity.text(col_x[2], y, f"{new_pop:.3f}", ha='center', va='center')
            # Change with color
            color = "green" if change > 0 else ("red" if change < 0 else "black")
            ax_popularity.text(col_x[3], y, f"{change:+.3f}", color=color, ha='center', va='center', fontweight='bold')

        # Set limits to fit the table nicely
        ax_popularity.set_xlim(-0.5, 3.5)
        ax_popularity.set_ylim(-n - 1, 1)


    def plot_allocations_matrix(self, ax, T):
        ax.axis("off")
        T = np.array(T)
        n = T.shape[0]

        cmap = LinearSegmentedColormap.from_list(
            "red_white_blue",
            [(0.0, "red"), (0.5, "white"), (1.0, "blue")]
        )
        norm = Normalize(vmin=-1, vmax=1) # always use -1 to 1 and hope for the best.

        for i in range(n):
            for j in range(n):
                val = T[i, j]
                color = cmap(norm(val))
                ax.add_patch(plt.Rectangle((j, -i), 1, 1, color=color))
                ax.text(j + 0.5, -i + 0.5, f"{val:.3f}", color="black", ha="center", va="center", fontsize=8)

        # Column labels (top)
        for j in range(n):
            ax.text(j + 0.5, 1.0, f"{j + 1}", ha="center", va="bottom", fontsize=10, fontweight='bold')

        # Row labels (left)
        for i in range(n):
            ax.text(-0.5, -i + 0.5, f"{i + 1}", ha="right", va="center", fontsize=10, fontweight='bold')


        ax.set_xlim(-1, n)
        ax.set_ylim(-n, 1)

    def plot_influence_graph(self, ax, influence_matrix, popularity):
        influence_matrix = np.array(influence_matrix)
        net = NodeNetwork()
        net.setupPlayers([f"{i}" for i in range(np.shape(popularity)[0])])
        net.initNodes(
            init_pops=popularity)  # not sure if this is actually getting used the way that I think its getting used, but we are sure trying.
        net.update(influence_matrix, popularity)

        node_positions = np.array([node.position[-1] for node in net.nodes])
        # ax is already defined
        ax.set_aspect("equal")
        ax.axis("off")
        for i, (x, y) in enumerate(node_positions):
            color = COLORS[i % len(COLORS)]
            ax.scatter(x, y, s=150, c=color, edgecolors="none", zorder=2)
            ax.text(x, y, str(i), fontsize=10, ha="center", va="center", color="black", zorder=3)

        min_weight = np.min(np.abs(influence_matrix))
        max_weight = np.max(np.abs(influence_matrix))

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
            for j, weight in enumerate(influence_matrix[
                                           i]):  # yeah I think this will graph to much, I htink I need to do this at just the mcfreakin uhh curr Round.
                if weight != 0:
                    x0, y0 = node_positions[i]
                    x1, y1 = node_positions[j]
                    color, alpha = get_edge_color_and_opacity(weight)
                    segments.append([(x0, y0), (x1, y1)])
                    colors.append(to_rgba(color, alpha))

        lc = LineCollection(segments, colors=colors, zorder=1)
        ax.add_collection(lc)






