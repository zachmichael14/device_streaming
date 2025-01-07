from PySide6.QtWidgets import QMessageBox


class MessageUtils:
    """Utility class for displaying informative dialog boxes to the user.

    This class provides static methods for showing error and informational
    messages using message boxes.
    """

    @staticmethod
    def show_error_message(parent,
                           window_title: str,
                           message_title: str,
                           message: str) -> None:
        """
        Displays an error message dialog.

        :param parent: The parent widget for the message box.
        :param window_title: The title of the message box window.
        :param message_title: The title of the error message.
        :param message: The error message to display.
        """
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Warning)

        msg_box.setWindowTitle(window_title)
        msg_box.setText(message_title)
        msg_box.setInformativeText(message)

        msg_box.exec()

    @staticmethod
    def show_info_message(parent,
                           window_title: str,
                           message_title: str,
                           message: str) -> None:
        """
        Displays an informational message dialog.

        :param parent: The parent widget for the message box.
        :param window_title: The title of the message box window.
        :param message_title: The title of the informational message.
        :param message: The informational message to display.
        """
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Information)

        msg_box.setWindowTitle(window_title)
        msg_box.setText(message_title)
        msg_box.setInformativeText(message)

        msg_box.exec()

    @staticmethod
    def confirm_overwrite(parent, file_path: str) -> bool:
        """
        Displays a confirmation dialog asking if the user wants to overwrite an existing file.

        Arguments:
            parent: The parent widget for the message box.
            file_path: The path of the file that might be overwritten.

        Returns:
            True if the user confirms overwriting, False otherwise.
        """
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Confirm Overwrite")
        msg_box.setText("File Already Exists")
        msg_box.setInformativeText(f"The file at {file_path} already exists. Do you want to overwrite it?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        return msg_box.exec() == QMessageBox.Yes