import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

cmap = ListedColormap(["White", "Gray", "Black", "#6baed6", "#3182bd", "#08519c"])
                    # backround, hare,   stag,    p1        p2          p3

COLORS = ["#6baed6", "#3182bd", "#08519c", "#31a354", "#e34a33", "#756bb1"]


class IndividualRoundGrapher():
    def __init__(self):
        pass
        # not sure what we are goiing to need here.

    def create_round_graph(self, stag_hare, last_round=False):
        state = stag_hare.state
        declarations = stag_hare.state.hunting_hare_map
        new_bool = stag_hare.is_over()
        nrows, ncols = state.height, state.width
        image = state.return_as_array()
        if last_round == False:
            fig, ax = plt.subplots()
            round_num = stag_hare.state.round_num
        else:
            round_num = "End"
            fig, (ax, ax_pop) = plt.subplots(1, 2) # one for the end state, one for the popularity.
            # actually thats still not really helpful.

        # Use imshow instead of matshow on the axes we created
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

        if last_round:
            round_state = stag_hare.state  # rename for clarity
            max_popularity = 0
            min_popularity = 200

            for i, player in enumerate(stag_hare.hunters):
                # problem: y right now is everything, I need to get, say, specifically player 2.
                pops = list(zip(*stag_hare.popularity_over_time)) # bit of a jump here.
                y = pops[i]
                x = list(range(len(y)))

                ax_pop.plot(x, y, color=COLORS[i % len(COLORS)], linewidth=2)
                ax_pop.scatter(x, y, s=25, color=COLORS[i % len(COLORS)], label=f"Player {player.id + 1}")

                max_popularity = max(max_popularity, max(y))
                min_popularity = min(min_popularity, min(y))

            ax_pop.set_xlim(0, round_state.round_num)
            ax_pop.set_ylim(min_popularity - 10, max_popularity + 10)

            ax_pop.set_xlabel("Round")
            ax_pop.set_ylabel("Popularity")
            ax_pop.set_title("Popularity Over Time")
            ax_pop.legend()

        plt.show()
