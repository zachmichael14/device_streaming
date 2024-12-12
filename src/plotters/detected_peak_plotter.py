import math
import sys
from typing import List

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QPen
from pyqtgraph import GraphicsLayoutWidget, PlotDataItem, PlotItem, mkPen, InfiniteLine
import numpy as np

from src.utils.colors import LabColors, DetectionWindowColors

# TODO: Dynamic detection algorithm
# TODO: Detection algorithm utils class?
class DetectedPeakPlotter(QMainWindow):
    """
    A plotter that plots peaks detected from multiple sensor data.
    
    Assumptions:
    1) Plot titles are sensor labels (from sensor map) and are listed in order 
    of appearance
    2) For bilateral plots, left side is listed first
    3) Plots in the same row share the same color
    4) All plots have the same y-axis label
    """

    PENS: List[QPen] = [mkPen(color) for color in LabColors.get_all_colors()]
    
    # This is used to space elements of displayed plot titles
    SPACING = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"

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

        self.detection_windows: List[InfiniteLine] = []

        # Subplot objects represent the actual plotting areas
        # Ops on labels, title, axes range, etc. are done on these objects
        self.subplots = self._create_subplots()

        self.main_plot = GraphicsLayoutWidget()
        self._arrange_subplots()

        # Subplot data objects represent the data for the subplots
        # Updating plot with new data is done on these objects
        self.subplot_data = self._init_subplot_data(sampling_rate, x_axis_max)


        self.setWindowTitle("Detected Peak Plotter")
        self.setCentralWidget(self.main_plot)

    def _create_subplots(self) -> List[PlotItem]:
        """
        Create subplots for each plot title.

        Returns:
            List of PlotItem objects
        """
        subplots: List[PlotItem] = []

        for title in self.plot_titles:
            detection_windows: List[InfiniteLine] = self._create_detection_windows()
            subplot = self._create_plot(title, detection_windows)
            subplots.append(subplot)
        return subplots
    
    def _create_detection_windows(self):
        m_response_start = self._create_detection_line(0.045,
                                                       DetectionWindowColors.PURPLE.value,
                                                       "|>")
        m_response_end = self._create_detection_line(0.058,
                                                     DetectionWindowColors.PURPLE.value,
                                                     "<|")
        h_response_start = self._create_detection_line(0.065,
                                                      DetectionWindowColors.BLUE.value,
                                                      "|>")
        h_response_end = self._create_detection_line(0.085,
                                                      DetectionWindowColors.BLUE.value,
                                                      "<|")
        detection_window = [m_response_start, m_response_end, h_response_start, h_response_end]

        self.detection_windows.append(detection_window)
        return detection_window

    def _create_plot(self,
                     plot_title: str,
                     detection_windows: List[InfiniteLine]) -> PlotItem:
        """
        Create a single plot item with styled title and configured axes.

        Args:
            plot_title: Title for the plot

        Returns:
            Configured PlotItem
        """
        styled_title = f"<b>{plot_title}</b>{self.SPACING}"\
                    f"<span style='font-size: 12pt; color: {DetectionWindowColors.PURPLE.value}'>ML={0:0.1f} ms, MA={0:0.3f} mV{self.SPACING}"\
                    f"<span style='color: {DetectionWindowColors.BLUE.value}'>HL={0:0.1f} ms, HA={0:0.3f} mV</span>"
        plot = PlotItem(title=styled_title)
        
        # Disable auto range for trigger plot
        if "trigger" not in plot_title.casefold():
            plot.enableAutoRange()
        
        self._configure_axes(plot)
        self._add_detection_windows(plot, detection_windows)

        return plot
    
    def _configure_axes(self, plot: PlotItem):
        plot.getAxis("left").setLabel(text=self.y_axis_text,
                                      units=self.y_axis_unit)
        plot.getAxis("bottom").setLabel(text="Time",
                                        units="s")
        plot.getAxis("bottom").setGrid(200)

    def _add_detection_windows(self,
                               plot: PlotItem,
                               detection_windows: List[InfiniteLine]) -> None:
        for line in detection_windows:
            plot.addItem(line)

    def _arrange_subplots(self) -> None:
        """
        Arrange subplots in the graphics layout widget.

        The trigger plot spans two columns.
        """
        for index, subplot in enumerate(self.subplots):
            row_index = int(index / self.column_quantity)
            column_index = index % 2

            # Trigger plot spans two columns
            if "trigger" in subplot.titleLabel.text.casefold():
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

        Plots in the same row are assigned the same color. 

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
            # Use the same color for all plots in the row
            row_index = int(index / self.column_quantity)

            curve: PlotDataItem = subplot.plot(x=default_x_values,
                                               y=default_y_values,
                                               pen=self.PENS[row_index])
            subplot_data.append(curve)
        return subplot_data
    
   

    def _create_detection_line(self,
                               position,
                               color,
                               marker: str,
                               movable=True,
                               angle=90):
        line = InfiniteLine(pos=position,
                            pen=color,
                            movable=movable,
                            angle=angle)
        line.addMarker(marker)
        line.sigPositionChangeFinished.connect(self._detection_window_updated)

        return line

    def _detection_window_updated(self, updated_line):
        print("Line moved")
        print(updated_line.name())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DetectedPeakPlotter(["foo", "bar", "Trigger"], "Voltage", "V", 2000)
    window.show()
    sys.exit(app.exec())