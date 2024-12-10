from PySide6.QtCore import (
     Property, QEasingCurve, QPropertyAnimation, QRect, Qt, Signal
)
from PySide6.QtGui import  QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QWidget

class SlideToggle(QWidget):
    """
    A custom toggle switch widget that animates between ON and OFF states.

    Emits a signal when the toggle state changes.
    """
    signal_toggled = Signal(bool)

    GREEN = QColor(89, 229, 75)  # Color of ON state
    GRAY = QColor(200, 200, 200)  # Color of OFF state

    def __init__(self,
                 width = 60,
                 height = 30,
                 parent: QWidget = None) -> None:
        """
        Initializes the SlideToggle widget.

        Args:
            parent (QWidget, optional): The parent widget of this toggle. Defaults to None.
        """
        super().__init__(parent)

        self._toggle_width = width
        self._toggle_height = height
        self.setFixedSize(self._toggle_width, self._toggle_height)

        self._is_checked = False
        self._handle_position = 4

        self._animation = QPropertyAnimation(self, b"handle_position")  
        # Smooth animation
        self._animation.setEasingCurve(QEasingCurve.InOutCubic) 
        self._animation.setDuration(200)

    @Property(float)
    def handle_position(self) -> float:
        """Gets the current position of the toggle handle."""
        return self._handle_position

    @handle_position.setter
    def handle_position(self, pos: float) -> None:
        """Sets the position of the toggle handle and triggers a repaint.

        Args:
            pos (float): The new position of the handle
        """
        self._handle_position = pos
        self.update()

    def mousePressEvent(self, event) -> None:
        """Handles mouse press events to toggle the switch state.

        Overrides superclass's mousePressEvent method.

        Args:
            event: The mouse event containing information about the press
        """
        if event.button() == Qt.LeftButton:
            self._is_checked = not self._is_checked
            self._animate()
            self.signal_toggled.emit(self._is_checked)  

    def paintEvent(self, event) -> None:
        """Handles the painting of the toggle widget.

        Overrides the superclass's paintEvent method.

        Args:
            event: The paint event used to trigger the paint operation
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # Enable anti-aliasing for smoother edges

        self._draw_background(painter)
        self._draw_handle(painter)
        self._draw_on_off_text(painter)

    def isChecked(self) -> bool:
        """Checks if the toggle is currently in the ON state.

        Returns:
            bool: True if checked (ON), False otherwise
        """
        return self._is_checked

    def setChecked(self, checked: bool) -> None:
        """Sets the toggle state and updates the UI accordingly.

        True if ON/checked, False otherwise.

        Args:
            checked (bool): The new state of the toggle
        """
        if self._is_checked != checked:
            self._is_checked = checked
            self._handle_position = 34 if checked else 4
            self.update()
            self.signal_toggled.emit(self._is_checked)

    def _animate(self) -> None:
        """Animate the handle movement based on checked state."""
        self._animation.setStartValue(self._handle_position)
        self._animation.setEndValue(34 if self._is_checked else 4)
        self._animation.start()

    def _draw_background(self, painter: QPainter) -> None:
        """Draws the background of the toggle (the part that changes color).

        Args:
            painter (QPainter): The painter used for drawing the background
        """
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.GREEN if self._is_checked else self.GRAY)
        painter.drawRoundedRect(0, 0,
                                self._toggle_width, self._toggle_height,
                                15, 15)

    def _draw_handle(self, painter: QPainter) -> None:
        """Draws the handle of the toggle.

        Args:
            painter (QPainter): The painter used for drawing the handle
        """
        painter.setPen(QPen(Qt.white, 1))
        painter.setBrush(Qt.white)
        painter.drawEllipse(QRect(int(self._handle_position), 4, 22, 22))

    def _draw_on_off_text(self, painter: QPainter) -> None:
        """Draws the ON and OFF text labels on the toggle.

        Args:
            painter (QPainter): The painter used for drawing the text
        """
        painter.setFont(QFont("Arial", 8))

        if self._is_checked:
            painter.setPen(Qt.white)
            painter.drawText(QRect(4, 0, 26, self._toggle_height),
                             Qt.AlignCenter,
                             "ON")
        else:
            painter.setPen(QColor(124,124,124))
            painter.drawText(QRect(30, 0, 26, self._toggle_height),
                             Qt.AlignCenter,
                             "OFF")
    def is_checked(self) -> bool:
        return self._is_checked
