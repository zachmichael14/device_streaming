from enum import Enum
from typing import List

from PySide6.QtGui import QColor

class LabColors(Enum):
    RED = QColor(253, 0, 58)
    CYAN = QColor(25, 222, 193)
    DARK_BLUE = QColor(19, 10, 241)
    ORANGE = QColor(254, 136, 33)
    PURPLE = QColor(177, 57, 255)
    LIGHT_BLUE = QColor(137, 137, 255)
    GREEN = QColor(0, 255, 0)

    @classmethod
    def get_all_colors(cls) -> List[QColor]:
        return [color.value for color in cls]


class DetectionWindowColors(Enum):
    """
    Plot titles use HTML while detection windows use QColors.
    To make these apply to both components, hexcodes were used.
    """
    PURPLE = "#9232BB" # (146, 51, 187)
    BLUE = "#00B4D8" # (0, 180, 216)
