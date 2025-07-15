import pyqtgraph as pg
from Client.combinedLayout.ui_functions.jhg_network_graph import update_jhg_network_graph
from Client.combinedLayout.colors import COLORS
from Client.combinedLayout.hoverScatter import HoverScatter
from PyQt6.QtCore import QTimer
import time

def update_jhg_ui_elements(main_window):
    jhg_widgets = main_window.round_state.jhg_widgets
    for i in range(main_window.round_state.num_players):
        if i == int(main_window.round_state.client_id):
            jhg_widgets[i].kept_number_label.setText(str(int(main_window.round_state.received[i])))
        else:
            jhg_widgets[i].received_label.setText(str(int(main_window.round_state.received[i])))
            jhg_widgets[i].sent_label.setText(str(int(main_window.round_state.sent[i])))

        main_window.round_state.allocations[i] = 0
        jhg_widgets[i].popularity_label.setText(
            str(round(main_window.round_state.message["POPULARITY"][i])))
        main_window.round_state.players[i].popularity_over_time.append(main_window.round_state.message["POPULARITY"][i])
        jhg_widgets[i].allocation_box.setText("0")

        QTimer.singleShot(0, lambda: update_jhg_popularity_graph(main_window.round_state, main_window.jhg_popularity_graph))


def update_jhg_popularity_graph(round_state, jhg_popularity_graph):
    jhg_popularity_graph.clear()
    try:
        jhg_popularity_graph.useOpenGL(False)
    except:
        pass

    max_popularity = 0
    all_spots = []

    for i, player in enumerate(round_state.players):
        color = COLORS[i]
        pen = pg.mkPen(color, width=2)

        x = list(range(len(player.popularity_over_time)))
        y = player.popularity_over_time

        line = jhg_popularity_graph.plot(x, y, pen=pen)

        player_spots = [
            {
                'pos': (x[j], y[j]),
                'data': f"Player {player.id + 1} (Round {j}): {y[j]}",
                'brush': pg.mkBrush(color),
                'size': 8,
                'pen': None
            }
            for j in range(len(x))
        ]
        all_spots.extend(player_spots)
        max_popularity = max(max_popularity, max(y))

    scatter = HoverScatter(spots=all_spots)
    jhg_popularity_graph.addItem(scatter)

    view_box = jhg_popularity_graph.getViewBox()
    view_box.setLimits(
        xMin=0,
        xMax=round_state.jhg_round_num + 1,
        yMin=0,
        yMax=max_popularity + 10,
    )
    jhg_popularity_graph.setXRange(0, round_state.jhg_round_num + 1, padding=0)
    jhg_popularity_graph.setYRange(0, max_popularity + 10, padding=0)
    #view_box.autoRange()
    jhg_popularity_graph.repaint()


def jhg_over(main_window, is_last, init_pop_influence):
    update_jhg_network_graph(main_window)
    #print("THIS IS GOING OFF NOW AND IS LAST IS ", is_last)
    if not is_last:
        start_jhg_round(main_window)
    else:
        #main_window.disable_jhg_buttons(main_window.JHG_panel) # PLEASE
        for button in main_window.jhg_buttons:
            button.setEnabled(False)

        for button in main_window.SC_voting_grid.buttons:
            if button.objectName() != "clear_button":
                button.setEnabled(True)

        main_window.round_state.sc_cycle = 1
        main_window.SC_cause_graph.update_cycle_label(1, True)

        main_window.dockWidget.bottom_left.start_flashing()
        main_window.dockWidget.top_left.disable_highlight()
        main_window.SC_panel.setTabText(0, "Current Round")
        main_window.SC_panel.setCurrentIndex(0)

    main_window.JHG_tornado_graph.update_jhg_tornado(main_window.round_state.influence_mat, init_pop_influence)


def start_jhg_round(main_window):
    main_window.round_state.tokens = main_window.round_state.tokens_per_player * main_window.num_players
    main_window.round_state.allocations = [0 for _ in range(main_window.num_players)]

    main_window.dockWidget.top_left.start_flashing()
    main_window.dockWidget.bottom_left.disable_highlight()

    for button in main_window.jhg_buttons:
        if button.objectName() == "JHGSubmitButton":
            button.setText("Submit")
        button.setEnabled(True)

    main_window.setWindowTitle(f"JHG: Round {main_window.round_state.jhg_round_num + 1}")
