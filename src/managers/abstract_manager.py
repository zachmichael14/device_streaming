from abc import ABC, abstractmethod
import asyncio
import multiprocessing
from queue import Queue

class AbstractDeviceManager(ABC):
    def __init__(self, device_client):
        self.device_client = device_client
        self.stream_queue = None

    @abstractmethod
    async def connect(self):
        """Connect to the device."""
        raise NotImplementedError(f"Concrete class {type(self).__name__} must implement connect() method.")

    @abstractmethod
    async def start_streaming(self, queue: Queue):
        """Start streaming data."""
        raise NotImplementedError(f"Concrete class {type(self).__name__} must implement start_streaming() method.")

    @abstractmethod
    async def stop_streaming(self):
        """Stop streaming data."""
        raise NotImplementedError(f"Concrete class {type(self).__name__} must implement stop_streaming() method.")
    
    @abstractmethod
    async def pause_streaming(self):
        """Pause streaming data."""
        raise NotImplementedError(f"Concrete class {type(self).__name__} must implement pause_streaming() method.")
    
    @abstractmethod
    async def resume_streaming(self):
        """Resume streaming data after a pause."""
        raise NotImplementedError(f"Concrete class {type(self).__name__} must implement stop_streaming() method.")
    

