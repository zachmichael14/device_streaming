import math
import sys
from typing import List

from PySide6.QtGui import QPen
from PySide6.QtWidgets import QApplication, QMainWindow
from pyqtgraph import GraphicsLayoutWidget, PlotDataItem, PlotItem, mkPen, QPen
import numpy as np

from src.utils.colors import LabColors

# TODO: Make sampling rate configurable in GUI
# TODO: Make x_axis range dynamic (longer/shorter than 3 seconds)
# TODO: Why no autorange on trigger?
class RealTimePlotter(QMainWindow):
    """
    A real-time plotter for multiple sensor data with configurable layout.
    
    Assumptions:
    1) Plot titles are sensor labels (from sensor map) and are listed in order 
    of appearance
    2) For bilateral plots, left side is listed first
    3) Plots in the same row share the same color
    4) All plots have the same y-axis label
    """

    PENS: List[QPen] = [mkPen(color) for color in LabColors.get_all_colors()]

    def __init__(self,
                 plot_titles: List[str],
                 y_axis_text: str,
                 y_axis_unit: str,
                 sampling_rate: int,
                 x_axis_max: float = 3.0,
                 plots_are_bilateral: bool = True):
        """
        Initialize the real-time plotter.

        Args:
            plot_titles: List of titles for each subplot
            y_axis_text: Text label for y-axis
            y_axis_unit: Unit for y-axis values
            sampling_rate: Number of samples per second
            x_axis_max: Maximum time range for x-axis (default 3 seconds)
            plots_are_bilateral: Whether plots are arranged in two columns
        """
        super().__init__()

        # Assuming labels are in the same order in which they should be plotted
        self.plot_titles = plot_titles
        self.y_axis_text = y_axis_text
        self.y_axis_unit = y_axis_unit

        self.column_quantity = 2 if plots_are_bilateral else 1

        # Always round up to ensure all plots fit
        self.row_quantity = math.ceil(len(plot_titles) / self.column_quantity)

        # Subplot objects represent the actual plotting areas
        # Ops on labels, title, axes range, etc. are done on these objects
        self.subplots = self._create_subplots()

        self.main_plot = GraphicsLayoutWidget()
        self._arrange_subplots()

        # Subplot data objects represent the data for the subplots
        # Updating plot with new data is done on these objects
        self.subplot_data = self._init_subplot_data(sampling_rate, x_axis_max)

        self.setWindowTitle("Real Time Plot")
        self.setCentralWidget(self.main_plot)

    def _create_subplots(self) -> List[PlotItem]:
        """
        Create subplots for each plot title.

        Returns:
            List of PlotItem objects
        """
        subplots: List[PlotItem] = [self._create_plot(title) for title in self.plot_titles]
        return subplots

    def _create_plot(self, plot_title: str) -> PlotItem:
        """
        Create a single plot item with styled title and configured axes.

        Args:
            plot_title: Title for the plot

        Returns:
            Configured PlotItem
        """
        styled_title = f'<span style="color: #FFF;">{plot_title}</span>'
        plot = PlotItem(title=styled_title)

        plot.getAxis("left").setLabel(text=self.y_axis_text,
                                      units=self.y_axis_unit)
        
        # Disable auto range for trigger plot
        if plot_title.casefold() != "trigger":
            plot.enableAutoRange()
        return plot
    
    def _arrange_subplots(self) -> None:
        """
        Arrange subplots in the graphics layout widget.

        The trigger plot spans two columns.
        """
        for index, subplot in enumerate(self.subplots):
            row_index = int(index / self.column_quantity)
            column_index = index % 2

            # Trigger plot spans two columns
            if subplot.titleLabel.text.casefold() == "trigger":
                self.main_plot.addItem(subplot,
                                       row=row_index,
                                       col=column_index,
                                       colspan=2)
            else:
                self.main_plot.addItem(subplot,
                                       row=row_index,
                                       col=column_index)
    
    def _init_subplot_data(self,
                           sampling_rate: int,
                           x_axis_max: float) -> List[PlotDataItem]:
        """
        Initialize subplot data with default x and y values.

        Args:
            sampling_rate: Number of samples per second
            x_axis_max: Maximum time range

        Returns:
            List of PlotDataItem objects
        """
        default_x_values = np.arange(0, x_axis_max, (1 / sampling_rate))
        default_y_values = np.zeros_like(default_x_values)

        subplot_data: List[PlotDataItem] = []
        for index, subplot in enumerate(self.subplots):
            row_index = int(index / self.column_quantity)

            curve: PlotDataItem = subplot.plot(x=default_x_values,
                                               y=default_y_values,
                                               pen=self.PENS[row_index])
            subplot_data.append(curve)
        return subplot_data
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RealTimePlotter(["foo", "bar", "Trigger"], "Voltage", "V", 2000)
    window.show()
    sys.exit(app.exec())