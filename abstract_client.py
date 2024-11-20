from abc import ABC, abstractmethod
import asyncio
import multiprocessing
from queue import Queue

class DeviceManager(ABC):
    @abstractmethod
    async def connect(self):
        """Connect to the device."""
        pass

    @abstractmethod
    async def start_streaming(self, queue: Queue):
        """Start streaming data."""
        pass

    @abstractmethod
    async def stop_streaming(self):
        """Stop streaming data."""
        pass

    @abstractmethod
    def get_device_name(self):
        """Return the device name."""
        pass
