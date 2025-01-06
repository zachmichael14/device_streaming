from enum import auto, Enum
import logging
from queue import Queue
import threading
import time
import xml.etree.ElementTree as ET

from src.devices.abstract_manager import DeviceManager
from src.clients.trigno.trigno_client import TrignoClient

class StreamState(Enum):
    STOPPED = auto()
    RUNNING = auto()
    PAUSED = auto()


class TrignoManager(DeviceManager):
    logging.basicConfig(filename="test_log.log", level=logging.INFO, format="%(asctime)s [%(threadName)s] %(message)s")

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

        # query devices

    def disconnect(self):
        """
        Streaming must be stopped before disconnecting to avoid a WinError 10038 caused by trying to read data from an closed socket.
        """
        if self.stream_state != StreamState.STOPPED:
            self.stop_streaming()

        self.client.disconnect()

    def start_streaming(self):
        """Start streaming data."""

        # Resuming after pause does not need to recreate a thread.
        # Therefore, only start streaming if it's currently stopped.
        if self.stream_state != StreamState.STOPPED:
            return
    
        self.client.start_streaming()
        
        self.stream_state = StreamState.RUNNING
        self.stream_thread = threading.Thread(target=self._stream_data,
                                            #   daemon=True
                                              )
        self.stream_thread.start()
        print("Start streaming ddone")

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
                    logging.info(frame)
                    print("logging")
                    self.streamed_data_queue.put(frame)
                except Exception as e:
                    print(f"Streaming Error: {e}")
                    self.stop_streaming()
                    break

            else:
                print("in else")
                # Yield CPU time while paused
                time.sleep(0.01)

if __name__ == "__main__":
    client = TrignoClient
    manager = TrignoManager(client)
    manager.connect()
    # manager.client.get_sensors()


    # manager.start_streaming()
    
    # # Example of streaming control
    # time.sleep(1)  # Stream for 5 seconds
    # manager.pause_streaming()
    # time.sleep(1)  # Pause for 2 seconds
    # manager.resume_streaming()
    # time.sleep(1)  # Stream for 3 more seconds
    # manager.stop_streaming()

    # manager.disconnect()
