from queue import Queue

from abstract_client import DeviceManager
from trigno_client import TrignoClient

class TrignoManager(DeviceManager):

    def __init__(self, client: TrignoClient):
        self.trigno_client = client
        self.queue = Queue()

    async def connect(self):
        """Connect to the device."""
        pass

    async def start_streaming(self, queue: Queue):
        """Start streaming data."""
        pass

    async def stop_streaming(self):
        """Stop streaming data."""
        pass

    def get_device_name(self):
        """Return the device name."""
        pass
