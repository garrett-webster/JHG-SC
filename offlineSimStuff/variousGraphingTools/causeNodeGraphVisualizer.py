# ok so -- what does this need? we are going to need
# the currentOptionsMatrix, and I think? thats it? maybe? that would be wild.
from Server.social_choice_sim import Social_Choice_Sim
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch
import matplotlib.gridspec as gridspec

class causeNodeGraphVisualizer:
    def __init__(self):
        pass

    def create_graph(self, all_nodes, all_votes, winning_vote, current_options_matrix):
        fig = plt.figure(figsize=(13, 6))  # Compact figure size
        gs = gridspec.GridSpec(1, 2, width_ratios=[0.8, 3.2])  # tighter left:right ratio

        # --- LEFT PANEL: Matrix + Vote (tight & aligned) ---
        ax_matrix = fig.add_subplot(gs[0])
        ax_matrix.axis('off')

        num_rows = len(current_options_matrix)
        max_cols = max(len(row) for row in current_options_matrix) if current_options_matrix else 0

        for i in range(num_rows):
            player_id = i + 1
            options = current_options_matrix[i]
            vote = all_votes.get(i, "?")

            # Use fixed-width formatting for alignment
            formatted_options = " ".join(f"{opt:>2}" for opt in options)
            row_text = f"{player_id:>2} | {formatted_options} | {vote + 1:>2}"

            # Display as one boxed row with monospaced font
            ax_matrix.text(0, -i, row_text, ha='left', va='center', fontsize=12,
                           fontfamily='monospace',
                           bbox=dict(boxstyle='round,pad=0.2', facecolor='whitesmoke', edgecolor='gray'))

        ax_matrix.set_xlim(-1, 10)
        ax_matrix.set_ylim(-num_rows, 1)

        # --- Add Winning Vote Text Below Matrix ---
        ax_matrix.text(1, -num_rows - 1, f"Winning vote: {winning_vote+1}", ha='left', va='center',
                       fontsize=12, color='red')

        # --- RIGHT PANEL: Graph ---
        ax = fig.add_subplot(gs[1])
        ax.set_xlim(-12, 12)
        ax.set_ylim(-12, 12)
        ax.set_aspect('equal')
        ax.axis('off')

        node_positions = {node["text"]: (node["x_pos"], node["y_pos"]) for node in all_nodes}
        node_types = {node["text"]: node["type"] for node in all_nodes}

        for node in all_nodes:
            x, y = node["x_pos"], node["y_pos"]
            label = node["text"]
            node_type = node["type"]

            try:
                number = int(label.split()[-1])
            except ValueError:
                number = label

            if node_type == "CAUSE":
                color = 'red' if label == "Cause " + str(winning_vote+1) else 'lightblue'
                shape = patches.RegularPolygon((x, y), numVertices=3, radius=1.0, orientation=0,
                                               color=color, ec='black', zorder=2)
                ax.add_patch(shape)
            elif node_type == "PLAYER":
                shape = plt.Circle((x, y), 0.7, color='lightgreen', ec='black', zorder=2)
                ax.add_patch(shape)

            ax.text(x, y, str(number), ha='center', va='center', fontsize=14, weight='bold', zorder=3)

        for player_index, vote in all_votes.items():
            player_label = f"Player {player_index + 1}"
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

        # Reduce space between matrix and graph and the overall layout
        fig.subplots_adjust(wspace=0.01, left=0.05, right=0.95, top=0.95, bottom=0.15)  # Adjust bottom margin

        plt.show()