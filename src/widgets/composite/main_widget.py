from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget)

from src.ui.composite.config_widget import ConfigWidget
from src.ui.composite.trial_widget import TrialWidget
from src.ui.composite.device_tab import DeviceWidget
from src.devices.device_types import DeviceTypes


class TabbedWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.addTab(DeviceWidget(), "Global")
        self.addTab(DeviceWidget(DeviceTypes.QTM), "QTM")
        self.addTab(DeviceWidget(DeviceTypes.TRIGNO), "Trigno")
        self.addTab(DeviceWidget(DeviceTypes.USBAMP), "USBAmp")

class TopWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QHBoxLayout()

        left_side_layout = QVBoxLayout()

        self.config_widget = ConfigWidget()
        self.trial_widget = TrialWidget()

        left_side_layout.addWidget(self.config_widget)
        left_side_layout.addWidget(self.trial_widget)


        self.tabbed_widget = TabbedWidget()

        # Add first third
        main_layout.addLayout(left_side_layout, 1)  # Stretch factor 1 for first third

        # Add second and third thirds (TabbedWidget)
        main_layout.addWidget(self.tabbed_widget, 2)  # Stretch factor 2 for second and third thirds

        self.setLayout(main_layout)


class BottomTabbedWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Adding tabs
        self.addTab(QWidget(), "Pulse")
        self.addTab(QWidget(), "Continuous")


class MainWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()

        self.top_widget = TopWidget()
        self.bottom_tabbed_widget = BottomTabbedWidget()

        layout.addWidget(self.top_widget, 2)  # Top half stretch factor 2
        layout.addWidget(self.bottom_tabbed_widget, 1)  # Bottom half stretch factor 1

        self.setLayout(layout)