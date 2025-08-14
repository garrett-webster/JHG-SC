from matplotlib.patches import FancyArrowPatch


class Arrow:
    def __init__(self, start, end, **kwargs):
        """
        Initializes an Arrow object
        :param start: Tuple (x, y) for the start of the arrow
        :param end: Tuple (x, y) for the end of the arrow
        :param kwargs: Additional parameters like color, width, and head size
        """
        self.start = start
        self.end = end
        self.color = kwargs.pop('color', 'black')  # Default to black if not provided
        self.line_thickness = kwargs.pop('line_thickness', 1)  # Default thickness

        self.kwargs = kwargs

        self.arrow_patch = None

    def draw(self, ax):
        """
        Draw the arrow using FancyArrowPatch
        :param ax: Matplotlib Axes object to draw the arrow on
        """
        self.arrow_patch = FancyArrowPatch(
            posA=self.start, posB=self.end,
            arrowstyle='->', color=self.color,
            mutation_scale=self.kwargs.get('mutation_scale', 15),  # Adjust arrowhead size
            linewidth=self.line_thickness, # Arrow line thickness
            zorder=10,
            **self.kwargs
        )
        ax.add_patch(self.arrow_patch)


    def remove(self):
        if self.arrow_patch and self.arrow_patch.axes:
            try:
                self.arrow_patch.remove()
            except Exception as e:
                print(f"Error removing arrow: {e}")
            self.arrow_patch = None