from typing import Optional

from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QGroupBox
from PySide6.QtCore import Signal

from src.devices.device_types import DeviceTypes
from src.ui.basic.slide_toggle import SlideToggle

class DeviceWidget(QWidget):
    signal_connection_toggled = Signal(DeviceTypes, str)
    signal_streaming_toggled = Signal(DeviceTypes, str)

    def __init__(self, device: Optional[DeviceTypes] = None):
        super().__init__()

        self.device = device if device else "Global"

        # Create labels and toggle switches
        self.connection_label = QLabel("Connection")
        self.connection_toggle = SlideToggle()

        self.streaming_label = QLabel("Streaming")
        self.streaming_toggle = SlideToggle()

        # Create layout for connection and streaming
        self.connection_streaming_layout = QVBoxLayout()
        self.connection_streaming_layout.addWidget(self.connection_label)
        self.connection_streaming_layout.addWidget(self.connection_toggle)
        self.connection_streaming_layout.addWidget(self.streaming_label)
        self.connection_streaming_layout.addWidget(self.streaming_toggle)

        # Add bounding box for plots
        self.plots_group_box = QGroupBox("Plots")
        self.plots_layout = QVBoxLayout()

        self.realtime_plot_checkbox = QCheckBox("Real-time Plot")
        self.detection_plot_checkbox = QCheckBox("Detection Plot")
        self.task_plot_checkbox = QCheckBox("Task Plot")

        self.plots_layout.addWidget(self.realtime_plot_checkbox)
        self.plots_layout.addWidget(self.detection_plot_checkbox)
        self.plots_layout.addWidget(self.task_plot_checkbox)

        self.plots_group_box.setLayout(self.plots_layout)

        # Arrange connection, streaming, and plots
        self.main_layout = QHBoxLayout()
        self.main_layout.addLayout(self.connection_streaming_layout)
        self.main_layout.addWidget(self.plots_group_box)

        # Set up main layout
        self.setLayout(self.main_layout)

        # Connect signals
        self._connect_signals()

    def _connect_signals(self):
        self.connection_toggle.signal_toggled.connect(self._connection_toggled)
        self.streaming_toggle.signal_toggled.connect(self._streaming_toggled)

    def _connection_toggled(self, is_connected: bool):
        self.signal_connection_toggled.emit(self.device, is_connected)
        print(f"Emitting: {self.device}, {is_connected}")

    def _streaming_toggled(self, is_streaming: bool):
        self.signal_streaming_toggled.emit(self.device, is_streaming)
        print(f"Emitting: {self.device}, {is_streaming}")