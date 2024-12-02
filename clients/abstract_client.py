from abc import ABCMeta, abstractmethod
from PySide6.QtCore import QObject

class QObjectABCMeta(ABCMeta, type(QObject)):
    """This class allows AbstractDeviceClient to inherit QObject.
    
    QObject is really only necessary if clients need to send signals.
    This class is necessary to avoid a metaclass conflict."""
    pass

class AbstractDeviceClient(QObject, metaclass=QObjectABCMeta):
    def __init__(self, parent=None):
        super().__init__(parent)

    @abstractmethod
    def connect(self):
        """Connect to device server."""
        pass

    @abstractmethod
    def disconnect(self):
        """Disconnect from device server."""
        pass

    @abstractmethod
    def start_streaming(self):
        """Start streaming data from the server."""
        pass

    @abstractmethod
    def stop_streaming(self):
        """Stop streaming data from the server."""
        pass

