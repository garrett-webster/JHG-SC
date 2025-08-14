import numpy as np

from Client.combinedLayout.hoverScatter import HoverScatter
from Client.combinedLayout.ui_functions.StudyScripts.network import NodeNetwork
from Client.combinedLayout.colors import COLORS
import pyqtgraph as pg

def update_sc_network_graph(main_window, I, results_sums, curr_round):
    # Create the node network and initialize with current popularity
    curr_I = np.array(I) # numpy arrays aren't json serializable so we swap it at the other end of the stream
    net = NodeNetwork()
    net.setupPlayers([f"{i}" for i in range(np.shape(results_sums)[0])])
    net.initNodes(init_pops=results_sums)
    net.update(curr_I, results_sums) # Update the network with the influence matrix and current popularity

    # Set up the graph in the PyQtGraph widget
    main_window.sc_influence.clear()  # Clear any existing items # how tho
    node_positions = np.array([node.position[-1] for node in net.nodes])  # Create a scatter plot for the nodes

    spots = []
    for i, (x, y) in enumerate(node_positions):
        data = str(i + 1)
        if (i + i) == main_window.round_state.client_id:
            data = "You (" + str(i + 1) + ")"
        color = COLORS[i % len(COLORS)]  # Cycle through COLORS
        spots.append({
            'pos': (x, y),
            'size': 15,
            'brush': pg.mkBrush(color),
            'pen': None,
            'data': f"{data}"  # Tooltip text
        })

    scatter = HoverScatter(spots=spots)
    main_window.sc_influence.addItem(scatter)

    # Normalize the influence weights for color mapping and opacity
    min_weight = np.min(np.abs(curr_I))
    max_weight = np.max(np.abs(curr_I))

    def get_edge_color_and_opacity(weight):
        """Map influence weight to color and opacity."""
        # Normalize the weight to a 0-1 range
        normalized = (weight - min_weight) / (max_weight - min_weight) if max_weight != min_weight else 0

        # Green for positive, Red for negative
        if weight > 0:
            color = (0, 255, 0)  # Green for positive
        else:
            color = (255, 0, 0)  # Red for negative

        # Opacity scales with connection strength (stronger = more opaque)
        opacity = int(abs(255 * normalized))  # Full opacity (255) for strong connections, 0 for weak/no connection

        return color, opacity

    # Create edges based on the influence matrix
    for i, node in enumerate(net.nodes):
        for j, weight in enumerate(curr_I[i]):
            if weight != 0:
                edge_color, opacity = get_edge_color_and_opacity(weight)
                pen = pg.mkPen(color=edge_color + (opacity,), width=2)

                # Create edge (PlotDataItem)
                line = pg.PlotDataItem([node_positions[i, 0], node_positions[j, 0]],
                                       [node_positions[i, 1], node_positions[j, 1]],
                                       pen=pen)  # Apply color and opacity

                line.setZValue(-1)  # Ensure edges are below the nodes
                main_window.sc_influence.addItem(line)

    main_window.sc_influence.scene().update()