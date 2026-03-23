import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

COLORS = ["#6baed6", "#3182bd", "#08519c", "#31a354", "#e34a33", "#756bb1"]

agents_to_objects_dict = {
    "hare": 0,
    "stag": 1,
    "R0": 2,
    "R1": 3,
    "R2": 4,
}

cmap = ListedColormap(["White", "Gray", "Black", "#6baed6", "#3182bd", "#08519c"])


class GameGrapher():
    def __init__(self, stag_hare):
        self.stag_hare = stag_hare

    def create_game_graph(self, current_game_logger):
        # Create main figure
        fig = plt.figure(figsize=(15, 8))

        # Left plot takes 1/3 of width, full height
        ax_pop = plt.subplot2grid((3, 6), (0, 0), rowspan=3, colspan=2)

        # Right side subplots
        ax_hunt1 = plt.subplot2grid((3, 6), (0, 2), colspan=4)
        ax_hunt2 = plt.subplot2grid((3, 6), (1, 2), colspan=4)
        ax_hunt3 = plt.subplot2grid((3, 6), (2, 2), colspan=4)

        # Assume it's the last round at this point.
        round_state = self.stag_hare.state
        max_popularity = 0
        min_popularity = 200

        for i, player in enumerate(self.stag_hare.hunters):
            pops = list(zip(*self.stag_hare.popularity_over_time))
            y = pops[i]
            x = list(range(len(y)))

            ax_pop.plot(x, y, color=COLORS[i % len(COLORS)], linewidth=2)
            ax_pop.scatter(x, y, s=25, color=COLORS[i % len(COLORS)],
                           label=f"Player {player.id + 1}")

            max_popularity = max(max_popularity, max(y))
            min_popularity = min(min_popularity, min(y))

        ax_pop.set_xlim(0, round_state.round_num)
        ax_pop.set_ylim(min_popularity - 10, max_popularity + 10)

        # Process intent data for each player
        intent = list(zip(*current_game_logger.hare_hunting_history))

        # Plot intent for each player in their respective subplot
        hunt_axes = [ax_hunt1, ax_hunt2, ax_hunt3]

        for i, player_intent in enumerate(intent):
            if i < 3:
                x = list(range(len(player_intent)))
                y = player_intent

                # Plot JUST DOTS (no connecting lines)
                # Use scatter only, no plot()
                hunt_axes[i].scatter(x, y, s=50, color=COLORS[i % len(COLORS)],
                                     zorder=10, edgecolors='black', linewidth=0.5)

                # Optional: Add horizontal lines at y=0 and y=1 for reference
                hunt_axes[i].axhline(y=0, color='gray', linestyle='--', alpha=0.3, linewidth=0.5)
                hunt_axes[i].axhline(y=1, color='gray', linestyle='--', alpha=0.3, linewidth=0.5)

                # Set y-axis to only show 0 and 1 with custom labels
                hunt_axes[i].set_yticks([0, 1, 2])
                hunt_axes[i].set_yticklabels(['Stag (0)', 'Hare (1)', 'Null (2)'])

                # Set y-limits with small padding
                hunt_axes[i].set_ylim(-0.1, 2.1)

                # Set x-limits to match round count
                hunt_axes[i].set_xlim(-0.5, round_state.round_num - 0.5)

                # Customize grid
                hunt_axes[i].grid(True, axis='x', alpha=0.2)
                hunt_axes[i].grid(True, axis='y', alpha=0.2, linestyle=':')

                hunt_axes[i].set_title(f"Player {i + 1} Hunting Intent")
                hunt_axes[i].set_xlabel("Round")

        ax_pop.set_xlabel("Round")
        ax_pop.set_ylabel("Popularity")
        ax_pop.set_title("Popularity Over Time")
        ax_pop.legend()
        ax_pop.grid(True, alpha=0.3)

        # Adjust layout
        plt.tight_layout()
        plt.show()

    def playback_game(self, current_game_logger):
        height, width = current_game_logger.height, current_game_logger.width
        for round in range(current_game_logger.rounds):
            intent = current_game_logger.hare_hunting_history[round]
            positions = {}
            for key in current_game_logger.position_history:
                positions[key] = current_game_logger.position_history[key][round]

            array = self.create_array(height, width, intent, positions)
            self.create_round_from_matrix(array, intent, round, last_round=False)

    def create_array(self, height, width, intent, positions):
        nrows, ncols = height, width
        image = np.zeros((nrows, ncols))
        image.fill(-1)
        for agent_position in positions.items():
            image[agent_position[1][0], agent_position[1][1]] = agents_to_objects_dict[agent_position[0]]
        return image

    def create_round_from_matrix(self, image, intent, round_num, last_round=False):
        round_num = round_num if not last_round else "End"

        fig, ax = plt.subplots()
        nrows, ncols = image.shape

        im = ax.imshow(image, cmap=cmap, vmin=-1, vmax=4)

        # Grid lines
        for x in np.arange(-0.5, ncols, 1):
            ax.vlines(x=x, ymin=-0.5, ymax=nrows - 0.5, colors="black", linewidth=1.5)
        for y in np.arange(-0.5, nrows, 1):
            ax.hlines(y=y, xmin=-0.5, xmax=ncols - 0.5, colors="black", linewidth=1.5)

        # Set ticks and labels
        ax.set_xticks(range(ncols))
        ax.set_yticks(range(nrows))
        ax.set_xticklabels(range(ncols))
        ax.set_yticklabels(range(nrows))
        ax.xaxis.tick_top()
        ax.set_title("ROUND: " + str(round_num))

        # Add intent markers
        if intent is not None:
            for player_id in range(2, 5):  # Players are values 2, 3, 4 in the image
                player_positions = np.where(image == player_id)

                if len(player_positions[0]) > 0:
                    for y, x in zip(player_positions[0], player_positions[1]):
                        # Note: Fixed the color mapping - you had 0=Stag, 1=Hare
                        # but in your dict, hare=0, stag=1, and for display you want:
                        # 0 = Stag (green), 1 = Hare (red)

                        # Since your intent list is [player0_intent, player1_intent, player2_intent]
                        # and 0=Stag, 1=Hare in the intent data:
                        actual_player_id = player_id - 2  # Convert 2→0, 3→1, 4→2

                        if actual_player_id < len(intent):
                            intent_value = intent[actual_player_id]

                            # Color mapping: 0 = Stag = Green, 1 = Hare = Red
                            # on start up, we actually don't have an intent. make it blue.
                            # color = 'green' if intent_value == 0 else 'red'
                            # intent_text = 'S' if intent_value == 0 else 'H'
                            if intent_value == 0:
                                color = 'green'
                                intent_text = 'S'
                            elif intent_value == 1:
                                color = 'red'
                                intent_text = 'H'
                            else:
                                color = 'yellow'
                                intent_text = 'N'



                            ax.scatter(x, y, s=400, color=color, alpha=0.6,
                                       edgecolors='white', linewidth=2, zorder=10)
                            ax.text(x, y, intent_text, fontsize=12, color='white',
                                    fontweight='bold', ha='center', va='center', zorder=11)

        plt.show()