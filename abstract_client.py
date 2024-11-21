from abc import ABC, abstractmethod
import asyncio
import multiprocessing
from queue import Queue

class DeviceManager(ABC):
    def __init__(self, device_client):
        self.device_client = device_client
        self.stream_queue = None

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
