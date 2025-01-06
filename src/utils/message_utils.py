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
