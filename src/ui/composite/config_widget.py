import json
from pathlib import Path
from typing import Dict, Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLabel,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QVBoxLayout,
    QWidget,
)

from src.utils.message_utils import MessageUtils


class ConfigWidget(QWidget):
    """
    A widget for configuring trial settings.
    
    This widget includes input fields for subject ID, functionality for import/export of configuration files, 
    sensor map upload, directory selection, and configuration setup.

    Attributes:
        subject_id_input: QLineEdit for entering subject ID.
        upload_sensor_map_label: QLabel displaying the selected sensor map path.
        directory_label: QLabel displaying the selected directory path.
    """
    signal_export_config = Signal(dict)
    signal_sensor_map_upload = Signal(Path)
    signal_set_config = Signal(dict)

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initializes the configuration widget.

        Args:
            parent (Optional[QWidget]): The parent widget.
        """
        super().__init__(parent)

        self.subject_id_input = QLineEdit(self)
        self.upload_sensor_map_label = QLabel("No sensor map selected", self)
        self.directory_label = QLabel("No save directory selected", self)

        self.set_config_button = QPushButton("Set Config", self)
        self._setup_set_config_button()

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)

        main_layout.addLayout(self._create_import_export_section())
        main_layout.addWidget(self._create_config_section())
        main_layout.addWidget(self.set_config_button)

        self.setLayout(main_layout)

    def _create_import_export_section(self) -> QHBoxLayout:
        """Creates the layout for import/export buttons."""
        import_export_layout = QHBoxLayout()

        import_button = QPushButton("Import", self)
        import_button.clicked.connect(self._handle_import)

        export_button = QPushButton("Export", self)
        export_button.clicked.connect(self._handle_export)

        import_export_layout.addWidget(import_button)
        import_export_layout.addWidget(export_button)

        return import_export_layout

    def _create_config_section(self) -> QGroupBox:
        """Creates the main configuration group box containing input fields."""
        config_groupbox = QGroupBox("New Configuration", self)
        config_layout = QFormLayout(config_groupbox)
        config_layout.setSpacing(10)

        config_layout.addRow(QLabel("Subject ID:", self), self.subject_id_input)
        config_layout.addRow(self._create_sensor_map_section())
        config_layout.addRow(self._create_directory_section())

        return config_groupbox

    def _create_sensor_map_section(self) -> QVBoxLayout:
        """Creates the section for uploading the sensor map."""
        upload_layout = QVBoxLayout()

        upload_sensor_map_button = QPushButton("Upload Sensor Map", self)
        upload_sensor_map_button.clicked.connect(self._handle_upload_sensor_map)

        upload_layout.addWidget(self.upload_sensor_map_label)
        upload_layout.addWidget(upload_sensor_map_button)

        return upload_layout

    def _create_directory_section(self) -> QVBoxLayout:
        """Creates the section for selecting a save directory."""
        directory_layout = QVBoxLayout()

        directory_button = QPushButton("Select Save Directory", self)
        directory_button.clicked.connect(self._handle_select_directory)

        directory_layout.addWidget(self.directory_label)
        directory_layout.addWidget(directory_button)

        return directory_layout

    def _setup_set_config_button(self) -> None:
        """Initializes the 'Set Config' button."""
        self.set_config_button.clicked.connect(self._handle_set_config)
        self.set_config_button.setStyleSheet("background-color: gray; color: white;")
        self.set_config_button.setEnabled(False)  # Initially disabled

    def _handle_import(self) -> None:
        """Handles the import action to load a configuration file and populate fields."""
        file_path, _ = QFileDialog.getOpenFileName(self,
                                                   "Select Configuration File",
                                                   "",
                                                   "JSON Files (*.json);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    config_data = json.load(file)
                    self._populate_with_imported_config(config_data)

            except Exception as e:
                MessageUtils.show_error_message(self,
                                                "Import Error",
                                                "Failed to import configuration.",
                                                str(e))

    def _populate_with_imported_config(self, imported_config: Dict) -> None:
        """
        Populates the widget's fields with data from an imported configuration.

        Args:
            imported_config (Dict): A dictionary containing the imported configuration data.
        """
        self.subject_id_input.setText(imported_config.get("subject_id",
                                                          ""))
        self.upload_sensor_map_label.setText(imported_config.get("sensor_map_path", "No sensor map selected"))
        self.directory_label.setText(imported_config.get("save_directory",
                                                         "No save directory selected"))
        self._update_set_config_button_state()

    def _handle_export(self) -> None:
        """Handles the export action, gathering configuration data and emitting a signal."""
        config_data = self._get_config_data()
        is_valid, failed_field = self._validate_non_empty_config(config_data)

        if is_valid:
            self.signal_export_config.emit(config_data)
        else:
            MessageUtils.show_error_message(
                self,
                "Export Error",
                "Cannot Export Configuration",
                f"Cannot validate <{failed_field}>. Ensure it's a non-default value."
            )

    def _handle_upload_sensor_map(self) -> None:
        """Handles the upload of a sensor map file and updates the corresponding label."""
        file_path, _ = QFileDialog.getOpenFileName(self,
                                                   "Select Sensor Map",
                                                   "",
                                                   "CSV Files (*.csv);;All Files (*)")
        if file_path:
            self.upload_sensor_map_label.setText(file_path)
            self.signal_sensor_map_upload.emit(Path(file_path))
            self._update_set_config_button_state()

    def _handle_select_directory(self) -> None:
        """Handles the selection of a directory and updates the corresponding label."""
        directory = QFileDialog.getExistingDirectory(self,
                                                     "Select Save Directory")
        if directory:
            self.directory_label.setText(directory)
            self._update_set_config_button_state()

    def _handle_set_config(self) -> None:
        """
        Validates the fields and emits a signal with the configuration data if valid.

        Displays an error message if validation fails.
        """
        config_data = self._get_config_data()
        is_valid, failed_field = self._validate_non_empty_config(config_data)

        if is_valid:
            self.signal_set_config.emit(config_data)
        else:
            error_messages = {
                "subject_id": "Subject ID is required.",
                "sensor_map": "A sensor map must be uploaded.",
                "save_directory": "A save directory must be selected."
            }
            MessageUtils.show_error_message(
                self,
                "Configuration Error",
                "Validation Failed",
                error_messages[failed_field]
            )

    def _validate_non_empty_config(self,
                                   config_data: Dict) -> tuple[bool,
                                                               Optional[str]]:
        """
        Validates that all configuration fields have non-empty, non-default values.

        Args:
            config_data (Dict): A dictionary containing the current configuration.

        Returns:
            tuple: (is_valid, failed_field)
                - is_valid: Boolean indicating if validation passed.
                - failed_field: Name of the field that failed validation, or None if all fields are valid.
        """
        validation_rules = {
            "subject_id": lambda x: bool(x),
            "sensor_map": lambda x: x != "No sensor map selected",
            "save_directory": lambda x: x != "No save directory selected"
        }

        for field, validator in validation_rules.items():
            if not validator(config_data[field]):
                return False, field

        return True, None

    def _get_config_data(self) -> Dict:
        """
        Gathers the current configuration data into a dictionary for export.

        Returns:
            Dict: A dictionary containing the current configuration data.
        """
        return {
            "subject_id": self.subject_id_input.text().strip(),
            "sensor_map": self.upload_sensor_map_label.text().strip(),
            "save_directory": self.directory_label.text().strip(),
        }

    def _update_set_config_button_state(self) -> None:
        """Updates the enabled state of the 'Set Config' button based on the validity of current configuration values."""
        config_data = self._get_config_data()
        is_valid, _ = self._validate_non_empty_config(config_data)

        self.set_config_button.setEnabled(is_valid)
        if is_valid:
            self.set_config_button.setStyleSheet("background-color: green; color: white;")
