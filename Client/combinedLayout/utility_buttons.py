from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QHBoxLayout
from PyQt6.QtWidgets import QPushButton

class MinusButtonUtility(QWidget):
    updateUtility = pyqtSignal()
    updateGraph = pyqtSignal()

    def on_minus_button_clicked(self, event):
        self.updateUtility.emit()
        self.updateGraph.emit()

    def __init__(self):
        super().__init__()
        self.minus_button = QPushButton("-")
        self.minus_button.setFixedWidth(self.minus_button.fontMetrics().horizontalAdvance("-") + 20)
        self.minus_button.setMinimumWidth(30)
        self.minus_button.setMaximumWidth(30)
        self.minus_button.clicked.connect(self.on_minus_button_clicked)

        layout = QHBoxLayout()
        layout.addWidget(self.minus_button)
        self.setLayout(layout)


class PlusButtonUtility(QWidget):
    updateUtility = pyqtSignal()
    updateGraph = pyqtSignal()

    def on_plus_button_clicked(self, event):
        self.updateUtility.emit()
        self.updateGraph.emit()

    def __init__(self):
        super().__init__()

        self.plus_button = QPushButton("+")
        self.plus_button.setFixedWidth(self.plus_button.fontMetrics().horizontalAdvance("+") + 20)
        self.plus_button.clicked.connect(self.on_plus_button_clicked)

        layout = QHBoxLayout()
        layout.addWidget(self.plus_button)
        self.setLayout(layout)