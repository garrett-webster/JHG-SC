from matplotlib.patches import Circle as MlpCircle


class Circle:
    def __init__(self, center, radius, **kwargs):
        """
        Initializes an Arrow object
        :param start: Tuple (x, y) for the start of the arrow
        :param end: Tuple (x, y) for the end of the arrow
        :param kwargs: Additional parameters like color, width, and head size
        """
        self.center = center
        self.radius = radius
        self.color = kwargs.pop('color', 'black')  # Default to black if not provided
        self.line_thickness = kwargs.pop('line_thickness', 1)  # Default thickness
        self.kwargs = kwargs
        self.circle_patch = None

    def draw(self, ax):
        """
        Draw the arrow using FancyArrowPatch
        :param ax: Matplotlib Axes object to draw the arrow on
        """
        self.circle_patch = MlpCircle(
            self.center, self.radius,
            edgecolor=self.color,
            facecolor=self.kwargs.pop("facecolor", "none"), # default to no fill
            linewidth=self.line_thickness, # Arrow line thickness
            zorder=10,
            **self.kwargs
        )
        ax.add_patch(self.circle_patch)


    def remove(self):
        """
        Removes the arrow from the canvas (axes)
        :param ax: Matplotlib Axes object to remove the arrow from
        """
        if self.circle_patch:  # Check if the arrow exists
            self.circle_patch.remove()  # Remove the arrow from the axes
            self.circle_patch = None  # Reset the reference to the arrow
