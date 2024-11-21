from enum import auto, Enum
from queue import Queue
import threading
import time

from abstract_client import DeviceManager
from trigno_client import TrignoClient

class StreamState(Enum):
    STOPPED = auto()
    RUNNING = auto()
    PAUSED = auto()


class TrignoManager(DeviceManager):

    def __init__(self, 
                 client: TrignoClient,
                 host_ip: str = "10.229.96.105",
                 ):
        self.client = client(host_ip)

        self.streamed_data_queue = Queue()
        self.stream_state = StreamState.STOPPED
        self.stream_thread = None

    def connect(self):
        """Establish a connection to the Trigno server"""
        self.client.connect()

    def start_streaming(self):
        """Start streaming data."""

        # Streaming can only be started if it's currently stopped
        # This is because resuming after pause does not need to recreate 
        # a thread
        if self.stream_state != StreamState.STOPPED:
            return
        self.client.start_streaming()
        
        self.stream_state = StreamState.RUNNING
        self.stream_thread = threading.Thread(target=self._stream_data)
        # self.client.start_streaming()
        self.stream_thread.start()

    def pause_streaming(self):
        if self.stream_state == StreamState.RUNNING:
            self.stream_state = StreamState.PAUSED

    def resume_streaming(self):
        if self.stream_state == StreamState.PAUSED:
            self.stream_state = StreamState.RUNNING

    def stop_streaming(self):
        """
        Stop Trigno sensor data streaming.

        Joins the thread and sends stop command to Trigno server.

        This method requires a particular order of events:
            1) Set stream state to STOPPED before joining thread or it will 
            run indefinitely while trying to join thread.
            2) Join thread before sending stop command to server to avoid a
            TimeoutError caused by the thread requesting data after the socket is closed.
            3) Send stop command to server after the above is completed
        """
        self.stream_state = StreamState.STOPPED

        # Stream state must be set to STOPPED before joining thread
        if self.stream_thread:
            self.stream_thread.join()
            self.stream_thread = None

        # Thread must be joined before calling client's stop method
        self.client.stop_streaming()

    def _stream_data(self):
        while self.stream_state != StreamState.STOPPED:
            if self.stream_state == StreamState.RUNNING:
                try:
                    frame = self.client.receive_emg_frame()
                    print(frame)
                    self.streamed_data_queue.put(frame)
                except Exception as e:
                    print(f"Streaming Error: {e}")
                    self.stop_streaming()
                    break

            else:
                # Yield CPU time while paused
                time.sleep(0.01)

if __name__ == "__main__":
    client = TrignoClient
    manager = TrignoManager(client)
    manager.connect()
    manager.start_streaming()
    
    # Example of streaming control
    time.sleep(2)  # Stream for 5 seconds
    manager.pause_streaming()
    time.sleep(2)  # Pause for 2 seconds
    manager.resume_streaming()
    time.sleep(2)  # Stream for 3 more seconds
    manager.stop_streaming()