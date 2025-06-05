# ok so -- what does this need? we are going to need
# the currentOptionsMatrix, and I think? thats it? maybe? that would be wild.
from Server.social_choice_sim import Social_Choice_Sim
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

class causeNodeGraphVisualizer:
    def __init__(self):
        pass

    #def create_graph(self, all_nodes, all_votes, winning_vote, current_options_matrix):
    def create_graph_with_sim(self, current_sim): # for right now, pass the cycle in. I might add him in later.
        all_nodes, all_votes, winning_vote_list, current_options_matrix, types_list, scenario, group, round, cycle, chromosome = current_sim.prepare_graph()
        self.create_graph(all_nodes, all_votes, winning_vote_list, current_options_matrix, types_list, scenario, group, round, cycle, chromosome)

    def create_graph_with_sim_vote_ovverride(self, current_sim, new_votes):
        all_nodes, all_votes, winning_vote_list, current_options_matrix, types_list, scenario, group, round, cycle, chromosome = current_sim.prepare_graph()
        self.create_graph(all_nodes, new_votes, winning_vote_list, current_options_matrix, types_list, scenario, group,
                          round, cycle, chromosome)


    def create_graph_given_file(self, dict):
        all_votes = dict["all_votes"]
        #all_nodes = dict["all_nodes"]
        winning_vote = dict["winning_vote"]
        current_options_matrix = dict["current_options_matrix"]
        scenario = dict["scenario"]
        group = dict["group"]
        curr_round = dict["curr_round"]
        cycle = dict["cycle"]
        types_list = dict["types_list"]
        chromosome = dict["chromosome"]
        #print("This is the curr_round we are passing in under cuaseNODeGraph", curr_round)
        num_bots = 9
        num_humans = 0
        total_order = []
        for bot in range(num_bots):
            total_order.append("B" + str(bot))
        for human in range(num_humans):
            total_order.append("P" + str(human))
        fake_scenario = r"C:\Users\Sean\Documents\GitHub\OtherGarrettStuff\JHG-SC\offlineSimStuff\scenarioIndicator\humanAttempt3"
        fake_chromosome = r"C:\Users\Sean\Documents\GitHub\OtherGarrettStuff\JHG-SC\offlineSimStuff\chromosomes\experiment"

        new_sim = Social_Choice_Sim(9, 3, 0, None, 0,0,fake_chromosome, fake_scenario, None, total_order)
        new_sim.set_new_options_matrix(current_options_matrix)
        new_sim.create_player_nodes()
        all_nodes = new_sim.get_nodes()
        new_nodes = []
        for node in all_nodes:
            new_nodes.append(node.to_json())
        self.create_graph(new_nodes, all_votes, winning_vote, current_options_matrix, types_list, scenario, group, curr_round, cycle, chromosome)


    def create_graph(self, all_nodes, all_votes, winning_vote_list, current_options_matrix, types_list, scenario, group, curr_round, cycle, chromosome):
        bot_color_map = {
            # -1 is player, 0 is random, 1 is socialWelfare, 2 is greedy, 3 is betterGreedy, 4 is limitedAwareness, 5 is secondChoice
            "-1": "lightgreen",
            "0": "purple",
            "1": "black",
            "2": "purple",
            "3": "blue",
            "4": "orange",
            "5": "plum",
            "6": "lightblue",
            "7" : "darkgreen",
            "8" : "green",
            "9" : "orange",
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
        }



        for cycle_key in all_votes.keys():
            curr_votes = all_votes[cycle_key]
            winning_vote = winning_vote_list[cycle_key]

            fig = plt.figure(figsize=(13, 6))  # Compact figure size
            gs = gridspec.GridSpec(1, 2, width_ratios=[0.8, 3.2])  # tighter left:right ratio

            # --- LEFT PANEL: Matrix + Vote (tight & aligned) ---
            ax_matrix = fig.add_subplot(gs[0])
            ax_matrix.axis('off')

            num_rows = len(current_options_matrix)
            matrix_array = np.array(current_options_matrix)
            col_sums = matrix_array.sum(axis=0)
            best_option = int(np.argmax(col_sums)) + 1  # gets the index of the best option and adds one to it



            for i in range(num_rows):
                vote = curr_votes.get(i) # tries to get it through an int first, from real time execution
                if vote is None: # if that fails, might be string
                    vote = curr_votes.get(str(i), "?") # if the string fails, we're fetched.

                player_id = i + 1
                options = current_options_matrix[i]

                # Use fixed-width formatting for alignment
                formatted_options = " ".join(f"{opt:>2}" for opt in options)
                row_text = f"{player_id:>2} | {formatted_options} | {int(vote) + 1:>2}"

                # Display as one boxed row with monospaced font
                ax_matrix.text(0, -i, row_text, ha='left', va='center', fontsize=12,
                               fontfamily='monospace',
                               bbox=dict(boxstyle='round,pad=0.2', facecolor='whitesmoke', edgecolor='gray'))

            # code to add teh column sums
            best_option = int(np.argmax(col_sums)) + 1  # +1 to match display indexing
            formatted_sums = " ".join(f"{val:>2}" for val in col_sums)
            sum_text = f"Σ  | {formatted_sums} | {best_option:>2}"

            ax_matrix.text(0, -num_rows, sum_text, ha='left', va='center', fontsize=12,
                           fontfamily='monospace',
                           bbox=dict(boxstyle='round,pad=0.2', facecolor='#e6f2ff', edgecolor='gray'))

            # Update the plot limits to make space for the sum row + winning vote
            ax_matrix.set_xlim(-1, 10)
            ax_matrix.set_ylim(-num_rows - 3, 1)

            # --- Add Winning Vote Text Below Matrix ---
            ax_matrix.text(1, -num_rows - 1, f"Winning vote: {winning_vote + 1}", ha='left', va='center',
                           fontsize=12, color='red')

            # --- RIGHT PANEL: Graph ---
            ax = fig.add_subplot(gs[1])
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
                ax.plot([x1, x2], [y1, y2], color='black', linewidth=2, alpha=0.8, zorder=1)

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
                    shape = patches.RegularPolygon((x, y), numVertices=3, radius=1.0, orientation=0,
                                                   color=color, ec='black', zorder=2)
                    ax.add_patch(shape)
                elif node_type == "PLAYER":
                    string = node["text"].split(" ")
                    id = types_list[int(string[1]) - 1]
                    used_bot_types.add(str(id))
                    color = bot_color_map[str(id)]

                    shape = plt.Circle((x, y), 0.7, color=color, ec='black', zorder=2, alpha=alpha)
                    ax.add_patch(shape)

                ax.text(x, y, str(number), ha='center', va='center', fontsize=14, weight='bold', zorder=3, alpha=alpha)

            for player_index, vote in curr_votes.items():
                player_label = f"Player {int(player_index) + 1}"
                cause_label = f"Cause {vote + 1}"  # for the off-by-one issue present in the votes.

                if player_label in node_positions and cause_label in node_positions:
                    x_start, y_start = node_positions[player_label]
                    x_end, y_end = node_positions[cause_label]

                    is_winning_vote = cause_label == "Cause " + str(winning_vote + 1)
                    arrow_color = 'red' if is_winning_vote else 'gray'

                    arrow = FancyArrowPatch((x_start, y_start), (x_end, y_end),
                                            arrowstyle='->', color=arrow_color,
                                            mutation_scale=15, lw=2, zorder=1)
                    ax.add_patch(arrow)

            fig.suptitle(
                f"Round: {str(int(curr_round))}   Situation: {scenario}   Cycle: {str(int(cycle_key)+1)}    Group: {group}",
                fontsize=16, fontweight='bold', y=0.98)

            # creates a legend that allows us to see which bot types are active, and which ones are what
            legend_elements = []

            for bot_type in sorted(used_bot_types):
                label = bot_name_map.get(bot_type, f"Type {bot_type}")
                color = bot_color_map.get(bot_type, bot_color_map["default"])
                legend_elements.append(Patch(facecolor=color, edgecolor='black', label=label))

            # You can put the legend on the right side of the graph area
            ax.legend(handles=legend_elements, loc='lower right', bbox_to_anchor=(1.0, -0.05),
                      ncol=2, fontsize=10, frameon=True, title="Bot Types")

            # Reduce space between matrix and graph and the overall layout
            fig.subplots_adjust(wspace=0.01, left=0.05, right=0.95, top=0.95, bottom=0.15)  # Adjust bottom margin
            # print("This is the round at the end!! ", curr_round)

            # Add circle patch behind nodes/arrows
            circle_patch = Circle((0, 0), radius=5, edgecolor='black', facecolor='none', linewidth=1, linestyle='--',
                                  zorder=0)
            ax.add_patch(circle_patch)
            circle_patch = Circle((0, 0), radius=10, edgecolor='black', facecolor='none', linewidth=1, linestyle='--',
                                  zorder=0)
            ax.add_patch(circle_patch)

            # Add dotted line "spokes" every 60 degrees
            for angle_deg in range(30, 390, 60):  # 30, 90, 150, ..., 330
                angle_rad = np.deg2rad(angle_deg)
                x = 10 * np.cos(angle_rad)
                y = 10 * np.sin(angle_rad)
                ax.plot([0, x], [0, y], color='black', linestyle=':', linewidth=1, zorder=0)

            my_path = os.path.dirname(os.path.abspath(__file__))
            scenario_str = f"scenario_{scenario}"
            group_str = f"group_{group}"
            file_name = f"round_{str(int(curr_round))}_cycle_{str(cycle_key)}.png"
            dir_path = os.path.join(my_path, "individualRoundGraphs", scenario_str, group_str)
            os.makedirs(dir_path, exist_ok=True)
            full_path = os.path.join(dir_path, file_name)

            plt.savefig(full_path, dpi=300)  # I want it to have the round, and cycle, and that shoudl do it
            plt.show()
            plt.close(fig) # make sure the fetcher dissapears, thats what I am saying.


