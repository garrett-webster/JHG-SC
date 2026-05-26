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
        # print("***********************")
        state = stag_hare.state
        intent_data = stag_hare.state.hunting_hare_map
        new_bool = stag_hare.is_over()
        nrows, ncols = state.height, state.width
        image = state.return_as_array()
        if last_round == False:
            round_num = stag_hare.state.round_num
        else:
            # literally just so we now whats going on
            round_num = "End"


        fig, ax = plt.subplots()

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





        plt.show()


    def create_round_from_matrix(self, image, round_num, last_round=False):
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

        plt.show()