import pyqtgraph as pg
from PyQt6.QtCore import QPoint, QTimer
from PyQt6.QtWidgets import QToolTip
from PyQt6.QtGui import QCursor

# Custom ScatterPlotItem that supports tooltips
class HoverScatter(pg.ScatterPlotItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptHoverEvents(True)
        self.last_point = None


    def hoverEvent(self, event):
        if event.isExit():
            QToolTip.hideText()
            self.last_point = None
            return
        else:
            points = self.pointsAt(event.pos())

            if len(points) > 0:
                point = points[0]
                if point != self.last_point:
                    self.last_point = point
                    cursor_pos = QCursor.pos()

                    # Create an offset to show the tooltip to the right of the cursor
                    offset = QPoint(15, -30)

                    # Set the tooltip position
                    tooltip_position = cursor_pos + offset

                    # Show the tooltip (default system look)
                    QToolTip.showText(tooltip_position, str(point.data()))


