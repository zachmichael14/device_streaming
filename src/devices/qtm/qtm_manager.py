from src.devices.qtm.qtm_client import QTMClient

class QTMManager:
    def __init__(self, client: QTMClient):
        self.client = client

    def connect(self):
        """Synchronous connection through manager."""
        return self.client.connect()

    def disconnect(self):
        """Synchronous disconnection through manager."""
        return self.client.disconnect()
    
    def start_streaming(self):
        """Start streaming data through the QTM client."""
        self.client.start_streaming()

    def stop_streaming(self):
        """Stop streaming data through the QTM client."""
        self.client.stop_streaming()

   

c = QTMClient("10.229.96.105", 22223, "1.22")
q = QTMManager(c)
import time
q.connect()
q.disconnect()
# q.connect()
# q.disconnect()
# time.sleep(2)
# q.client.get_parameters(["analog"])



# q.disconnect()



