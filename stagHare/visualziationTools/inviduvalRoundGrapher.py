import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

agents_to_objects_dict = {
    "hare": 1, # np.zeros is our blank backround
    "stag": 2,
    "R0": 3, # first agent
    "R1": 4, # second agent
    "R2": 5, # third agent
}

cmap = ListedColormap(["White", "Gray", "Black", "#6baed6", "#3182bd", "#08519c"])

class IndividualRoundGrapher():
    def __init__(self):
        pass
        # not sure what we are goiing to need here.

    def create_round_graph(self, stag_hare):
        state = stag_hare.state
        nrows, ncols = state.height, state.width
        image = np.zeros((nrows, ncols))
        for agent_position in state.agent_positions.items():
            image[agent_position[1][0], agent_position[1][1]] = agents_to_objects_dict[agent_position[0]]

        fig, ax = plt.subplots()

        # Use imshow instead of matshow on the axes we created
        im = ax.imshow(image, cmap=cmap, vmin=0, vmax=5)

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

        plt.show()