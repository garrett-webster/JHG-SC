from PyQt6.QtCore import Qt, QMimeData, QTimer
from PyQt6.QtGui import QDrag
from PyQt6.QtWidgets import QLabel, QWidget, QSizePolicy, QVBoxLayout, QSplitter, QFrame, QScrollArea


# Draggable panel widget
class DraggablePanel(QWidget):
    def __init__(self, content_widget: QWidget, title: str):
        super().__init__()

        # Outer layout for the whole DraggablePanel
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # Create the frame that will include both title and content
        self.frame = QFrame()
        self.frame.setObjectName("panelFrame")

        # Inner layout inside the frame
        frame_layout = QVBoxLayout()
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(0)

        # Title bar
        self.title_bar = QLabel(title)
        self.title_bar.setStyleSheet("""
            background-color: #333;
            color: white;
            padding: 5px;
            font-size: 14px;
            text-align: center;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        """)
        self.title_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Content widget
        self.content_widget = content_widget
        self.content_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Add both title and content to the frame
        frame_layout.addWidget(self.title_bar)
        frame_layout.addWidget(self.content_widget)
        self.frame.setLayout(frame_layout)

        # Add the styled frame to the main layout
        outer_layout.addWidget(self.frame)

        self.setAcceptDrops(True)
        self.setMinimumSize(450, 400)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def start_flashing(self, num_flashes=6):
        self.disable_highlight()
        self.flash_on = False
        self.flashes = 0
        self.num_flashes = num_flashes

        if not hasattr(self, "flash_timer"):
            self.flash_timer = QTimer(self)
            self.flash_timer.timeout.connect(self.flash_border)

        self.flash_border()
        self.flash_timer.start(500)

    def flash_border(self):
        self.frame.setProperty("flashing", self.flash_on)
        self.frame.style().unpolish(self.frame)
        self.frame.style().polish(self.frame)
        self.flash_on = not self.flash_on

        self.flashes += 1
        if self.flashes == self.num_flashes:
            self.flash_timer.stop()
            self.frame.setProperty("flashing", False)
            self.enable_highlight()
            self.flash_on = False


    def disable_highlight(self):
        self.frame.setProperty("active", False)
        self.frame.style().unpolish(self.frame)
        self.frame.style().polish(self.frame)

    def enable_highlight(self):
        self.frame.setProperty("active", True)
        self.frame.style().unpolish(self.frame)
        self.frame.style().polish(self.frame)



    def mousePressEvent(self, event):
        # Only start dragging when the title bar is clicked
        if event.button() == Qt.MouseButton.LeftButton and self.title_bar.rect().contains(event.pos()):
            drag = QDrag(self)
            mime = QMimeData()

            # Attach the widget itself (could be customized to carry more data)
            mime.setText(self.objectName())  # We can use custom data if needed
            mime.setData('application/x-widget', self.objectName().encode())  # Example custom data

            drag.setMimeData(mime)
            drag.exec(Qt.DropAction.MoveAction)

    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        source_widget = event.source()
        if source_widget and isinstance(source_widget, DraggablePanel):
            target_widget = self
            self.swap_widgets(source_widget, target_widget)
            event.acceptProposedAction()

    def swap_widgets(self, source, target):
        source_parent = source.parent()
        target_parent = target.parent()

        if not isinstance(source_parent, QSplitter) or not isinstance(target_parent, QSplitter):
            return

        source_index = source_parent.indexOf(source)
        target_index = target_parent.indexOf(target)

        # Save current sizes
        source_sizes = source_parent.sizes()
        target_sizes = target_parent.sizes()

        # Perform the swap
        if source_parent is target_parent and source_index < target_index:
            target_parent.insertWidget(target_index, source)
            target_parent.insertWidget(source_index, target)
        else:
            source_parent.insertWidget(source_index, target)
            target_parent.insertWidget(target_index, source)

        # Restore sizes to maintain layout balance
        source_parent.setSizes(source_sizes)
        if source_parent != target_parent:
            target_parent.setSizes(target_sizes)


# The container that holds the four corners
class CornerContainer(QWidget):
    def __init__(self, bottom_left_widget, bottom_right_widget):
        super().__init__()

        # Create draggable panels
        # scrollable_top_left = self.make_scrollable(top_left_widget, min_height=top_left_widget.property("min-height"))
        scrollable_bottom_left = self.make_scrollable(bottom_left_widget, min_height=bottom_left_widget.property("min-height"))

        # Create draggable panels
        # self.top_left = DraggablePanel(scrollable_top_left, "Junior High Game")
        # self.top_left.setMinimumHeight(400)
        # self.top_right = DraggablePanel(top_right_widget, "JHG Graphs")
        self.bottom_left = DraggablePanel(scrollable_bottom_left, "Social Choice Voting")
        self.bottom_right = DraggablePanel(bottom_right_widget, "Social Choice Graphs")


        # # Splitter for top row
        # top_splitter = QSplitter(Qt.Orientation.Horizontal)
        # top_splitter.addWidget(self.top_left)
        # top_splitter.addWidget(self.top_right)
        # top_splitter.setCollapsible(0, False)
        # top_splitter.setCollapsible(1, False)

        # Splitter for bottom row
        bottom_splitter = QSplitter(Qt.Orientation.Horizontal)
        bottom_splitter.addWidget(self.bottom_left)
        bottom_splitter.addWidget(self.bottom_right)
        bottom_splitter.setCollapsible(0, False)
        bottom_splitter.setCollapsible(1, False)

        # Main vertical splitter
        # main_splitter = QSplitter(Qt.Orientation.Vertical)
        # main_splitter.addWidget(top_splitter)
        # main_splitter.addWidget(bottom_splitter)
        # main_splitter.setCollapsible(0, False)
        # main_splitter.setCollapsible(1, False)

        # Set initial sizes (ratios)
        # main_splitter.setSizes([1, 1])
        # top_splitter.setSizes([1, 1])
        bottom_splitter.setSizes([1, 1])

        # Layout for the container
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(bottom_splitter)

        self.setLayout(layout)

    def make_scrollable(self, widget, min_height=400):
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(widget)

        widget.setMinimumHeight(min_height)  # Content wants to scroll
        wrapper.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        scroll_area = QScrollArea()
        scroll_area.setWidget(wrapper)
        scroll_area.setWidgetResizable(True)

        scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        scroll_area.setMinimumSize(0, 0)
        scroll_area.setMaximumHeight(10000000)

        return scroll_area