
import pygds as g

from src.clients.abstract_client import AbstractDeviceClient

class USBAmpClient(AbstractDeviceClient):
    # sampling rate, channels
    def __init__(self):
        self.connection = None
        self.sampling_rate = None
        self.is_streaming = False

    def connect(self):
        try:
            self.connection = g.GDS()
            rates = self.connection.GetSupportedSamplingRates()[0]
            self.sampling_rate = sorted(rates.items())[0][0]
            
            # Configure channels
            for ch in self.connection.Channels:
                ch.Acquire = True
            
            print(f"USBAmp connected. Sampling Rate: {self.sampling_rate}")
            return True
        except Exception as e:
            print(f"USBAmp connection failed: {e}")
            return False
        
    def disconnect(self):
        if self.connection:
            self.connection.Close()
            self.connection = None
            self.is_streaming = False
        
    def stop_streaming(self):
        """
        Set is_streaming bool to False.

        The API only provides a GetData method, which only returns a single
        frame. The only way to 'stream' data would be to thread this
        operation. However, that would better be managed by USBAmpManager.
        
        As such, this class merely keeps track of a streaming bool, but that
        may not be useful and may be removed. However, this method needs to be
        implemented to satisfy the AbstractDeviceClient requirements.Start streaming data from the server."""
        if self.is_streaming:
            self.is_streaming = False

    def start_streaming(self):
        """
        Set is_streaming bool to True.

        The API only provides a GetData method, which only returns a single
        frame. The only way to 'stream' data would be to thread this
        operation. However, that would better be managed by USBAmpManager.
        
        As such, this class merely keeps track of a streaming bool, but that
        may not be useful and may be removed. However, this method needs to be
        implemented to satisfy the AbstractDeviceClient requirements.
        """
        if not self.is_streaming:
            self.is_streaming = True

    def configure(self):
        # TODO:
        # - set sample rate
        # - set filters
        # - other config options
        pass

    def get_data(self):    
        if not self.connection:
            self.connect()
        return self.connection.GetData(self.sampling_rate)

    def get_number_of_channels(self):
        return len(self.connection.Channels) if self.connection else 0
    

