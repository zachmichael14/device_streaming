from datetime import datetime
from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Dict, Optional

from PySide6.QtCore import QObject
from src.utils.message_utils import MessageUtils


@dataclass
class ConfigData:
    """
    Holds configuration data for the application.

    Attributes:
        subject_id: Identifier for the subject.
        save_directory: Directory where data will be saved.
        sensor_map_path: Path to the sensor mapping file.
        subject_dir: Derived directory path for the subject, set after initialization.
        creation_timestamp: Timestamp indicating when the configuration was created.
    """
    subject_id: str
    save_directory: Path
    sensor_map_path: Path
    subject_dir: Path = field(init=False)  # Derived; not required on init
    creation_timestamp: Optional[str] = field(init=False)

    def __post_init__(self) -> None:
        """
        Create subject dir and timestamp after init.
        
        Must happen after init since subject_dir is derived.
        """
        self.subject_dir = self.save_directory / self.subject_id
        self.creation_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class ConfigManager(QObject):
    """
    Manages config data, including importing, exporting, and setting config 
    attributes.
    """

    def __init__(self) -> None:
        super().__init__()
        self.config_data: Optional[ConfigData] = None

    def export_config(self) -> None:
        """Converts config data to JSON and writes to 'config.json'."""
        if not self.config_data:
            MessageUtils.show_error_message(
                None,
                "Configuration Export Error",
                "Failed to Export Configuration",
                "Config data is not set within the config manager"
            )
            return

        config_file_path = self.config_data.subject_dir / "config.json"

        if not self._create_subject_directory():
            return

        # If the config file exists, prompt the user for overwrite permissions
        if config_file_path.exists() and not MessageUtils.confirm_overwrite(None, str(config_file_path)):
            return

        self._write_config_file(config_file_path)

    def _create_subject_directory(self) -> bool:
        """
        Ensures the subject directory exists, creating it if necessary.

        Returns:
            bool: True if the directory exists or is created successfully, False otherwise.
        """
        try:
            self.config_data.subject_dir.mkdir(parents=True, exist_ok=True)
            return True
        
        except IOError as e:
            MessageUtils.show_error_message(
                None,
                "Directory Creation Error",
                "Failed to Create Directory",
                f"An error occurred while creating the directory: {e}"
            )
            return False

    def _write_config_file(self, config_file_path: Path) -> None:
        """
        Writes the configuration data to a JSON file.

        Args:
            config_file_path (Path): The path where the configuration file will be saved.
        """
        try:
            with open(config_file_path, 'w') as file:
                serializable = self._serialize_config_data()
                json.dump(serializable, file, indent=4)

            MessageUtils.show_info_message(
                None,
                "Export Successful",
                "Configuration Saved",
                f"Configuration successfully saved to {config_file_path}"
            )

        except IOError as e:
            MessageUtils.show_error_message(
                None,
                "Export Error",
                "Failed to Save Configuration",
                f"An error occurred while writing the configuration file: {e}"
            )

    def _serialize_config_data(self) -> Dict[str, str]:
        """
        Converts Path objects in config data to strings for JSON dump.

        Returns:
            Dict[str, str]: A dictionary containing the configuration data as 
            strings.
        """
        config_data_serializable = {}

        for key, value in self.config_data.__dict__.items():
            if isinstance(value, Path):
                config_data_serializable[key] = str(value)
            else:
                config_data_serializable[key] = value

        return config_data_serializable
    
    def set_config(self, config_data: Dict[str, str]) -> None:
        """
        Parses config dictionary and updates the manager's ConfigData instance.

        Args:
            config_data (Dict[str, str]): A dictionary containing
            configuration data.
        """
        try:
            self.config_data = ConfigData(
                subject_id=config_data["subject_id"],
                save_directory=Path(config_data["save_directory"]),
                sensor_map_path=Path(config_data["sensor_map"]),
            )
        except KeyError as e:
            MessageUtils.show_error_message(
                None,
                "Configuration Error",
                "Missing Configuration Field",
                f"Configuration data is missing the required field: {e}"
            )
