from PySide6.QtCore import Signal

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QPushButton)


class TrialWidget(QWidget):
    signal_trial_name_updated = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        self.trial_name_label = QLabel("Trial Name")
        self.trial_name = QLineEdit()

        self.save_button = QPushButton("Save Session")
        self.delete_button = QPushButton("Delete Session")

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.delete_button)

        layout.addWidget(self.trial_name_label)
        layout.addWidget(self.trial_name)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _connect_signals(self):
        self.trial_name.textEdited.connect(self._trial_name_updated)

    def _trial_name_updated(self, trial_name: str):
        self.signal_trial_name_updated.emit(trial_name)
