import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

COLORS = ["#6baed6", "#3182bd", "#08519c", "#31a354", "#e34a33", "#756bb1"]

agents_to_objects_dict = {
    "hare": 0,  # np.zeros is our blank backround
    "stag": 1,
    "R0": 2,  # first agent
    "R1": 3,  # second agent
    "R2": 4,  # third agent
}

cmap = ListedColormap(["White", "Gray", "Black", "#6baed6", "#3182bd", "#08519c"])
                    # backround, hare,   stag,    p1        p2          p3

class GameGrapher():
    def __init__(self, stag_hare):
        self.stag_hare = stag_hare

    def create_game_graph(self, current_game_logger):
        # Create main figure with 1 row, 2 columns
        # Increase figsize to accommodate the right side subplots

        # Or alternative using subplot2grid (cleaner for complex layouts):
        fig = plt.figure(figsize=(15, 8))

        # Left plot takes 1/3 of width, full height
        ax_pop = plt.subplot2grid((1, 6), (0, 0), colspan=2)

        # Right side subplots - each takes 1/3 of the remaining space
        ax_hunt1 = plt.subplot2grid((3, 6), (0, 2), colspan=4, rowspan=1)
        ax_hunt2 = plt.subplot2grid((3, 6), (1, 2), colspan=4, rowspan=1)
        ax_hunt3 = plt.subplot2grid((3, 6), (2, 2), colspan=4, rowspan=1)

        # Assume it's the last round at this point.
        round_state = self.stag_hare.state  # rename for clarity
        max_popularity = 0
        min_popularity = 200

        for i, player in enumerate(self.stag_hare.hunters):
            # problem: y right now is everything, I need to get, say, specifically player 2.
            pops = list(zip(*self.stag_hare.popularity_over_time))  # bit of a jump here.
            y = pops[i]
            x = list(range(len(y)))

            ax_pop.plot(x, y, color=COLORS[i % len(COLORS)], linewidth=2)
            ax_pop.scatter(x, y, s=25, color=COLORS[i % len(COLORS)], label=f"Player {player.id + 1}")

            max_popularity = max(max_popularity, max(y))
            min_popularity = min(min_popularity, min(y))

        ax_pop.set_xlim(0, round_state.round_num)
        ax_pop.set_ylim(min_popularity - 10, max_popularity + 10)

        # Process intent data for each player
        intent = list(zip(*current_game_logger.hare_hunting_history))

        # Plot intent for each player in their respective subplot
        hunt_axes = [ax_hunt1, ax_hunt2, ax_hunt3]

        for i, player_intent in enumerate(intent):
            if i < 3:  # Only plot first 3 players (as you have 3 subplots)
                x = list(range(len(player_intent)))
                y = player_intent

                # Plot on the corresponding subplot
                hunt_axes[i].plot(x, y, color=COLORS[i % len(COLORS)], linewidth=2)
                hunt_axes[i].scatter(x, y, s=25, color=COLORS[i % len(COLORS)])
                hunt_axes[i].set_title(f"Player {i + 1} Hunting Intent")
                hunt_axes[i].set_xlabel("Round")
                hunt_axes[i].set_ylabel("Intent Value")

                # Set consistent y-limits for comparison
                # You might want to calculate min/max across all intents
                all_intents_flat = [item for sublist in intent for item in sublist]
                if all_intents_flat:  # Check if not empty
                    hunt_axes[i].set_ylim(min(all_intents_flat) - 0.1, max(all_intents_flat) + 0.1)

                hunt_axes[i].grid(True, alpha=0.3)

        ax_pop.set_xlabel("Round")
        ax_pop.set_ylabel("Popularity")
        ax_pop.set_title("Popularity Over Time")
        ax_pop.legend()

        # Adjust layout to prevent overlapping
        plt.tight_layout()

        plt.show()

    def playback_game(self, current_game_logger):
        height, width = current_game_logger.height, current_game_logger.width
        for round in range(current_game_logger.rounds):
            intent = current_game_logger.hare_hunting_history[round]
           #positions = current_game_logger.position_history[round]
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
        if last_round == False:
            round_num = round_num
        else:
            # literally just so we now whats going on
            round_num = "End"


        fig, ax = plt.subplots()

        nrows, ncols = image.shape

        im = ax.imshow(image, cmap=cmap, vmin=-1, vmax=4)

        # Now set up your grid lines and ticks
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

        # Add intent markers if provided
        if intent is not None:
            # intent_data should be a dict like {player_id: (intent_value, cell_x, cell_y)}
            # where intent_value: 0 = Hare, 1 = Stag

            # First, find all cells containing players
            for player_id in range(2, 6):  # Assuming 3 players max
                # Find where this player is in the grid
                player_positions = np.where(image == player_id)

                if len(player_positions[0]) > 0:
                    for y, x in zip(player_positions[0], player_positions[1]):
                        # Get intent for this player at this position

                        # Add colored dot based on intent
                        color = 'red' if intent[player_id-2] == 1 else 'green'  # red=hare, green=stag
                        ax.scatter(x, y, s=400, color=color, alpha=0.6,
                                   edgecolors='white', linewidth=2, zorder=10)

                        # Add text label
                        intent_text = 'H' if intent[player_id-2] == 1 else 'S'
                        ax.text(x, y, intent_text, fontsize=12, color='white',
                                fontweight='bold', ha='center', va='center', zorder=11)

        plt.show()