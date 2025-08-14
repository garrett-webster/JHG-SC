import pyqtgraph as pg
from PyQt6.QtCore import QPoint
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QToolTip


# Custom ScatterPlotItem that supports tooltips
class HoverScatter(pg.ScatterPlotItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptHoverEvents(True)


    def hoverEvent(self, event):
        if event.isExit():
            QToolTip.showText(QCursor.pos(), "")
            return
        points = self.pointsAt(event.pos())

        if len(points) > 0:
            point = points[0]
            cursor_pos = QCursor.pos()

            # Create an offset to show the tooltip to the right of the cursor
            offset = QPoint(10, -30)  # Adjust the (10, 0) values as needed for spacing

            # Set the tooltip position
            tooltip_position = cursor_pos + offset

            # Show the tooltip (default system look)
            QToolTip.showText(tooltip_position, str(point.data()))