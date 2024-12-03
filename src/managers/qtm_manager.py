from src.clients.qtm_client import QTMClient

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
        self.client.start_streaming(self.q_analog, self.q_frame)

    def stop_streaming(self):
        """Stop streaming data through the QTM client."""
        self.client.stop_streaming()

    def configure(self):
        """Configure the QTM client."""
        asyncio.run(self.client.configure())

    def get_state_sync(self):
        """
        Synchronous wrapper for the asynchronous `get_state` function.

        This is helpful for debugging.
        
        Returns:
            Latest state change of QTM.
        """
        if self.client.connection is None:
            raise ConnectionError("No active connection to QTM.")

        # Use the existing event loop to run the asynchronous function
        loop = asyncio.get_event_loop()
        try:
            return loop.run_until_complete(self.client.connection.get_state())
        except Exception as e:
            print(f"Error getting state: {e}")
            return None


c = QTMClient("10.229.96.105", 22223, "1.22")
q = QTMManager(c)
import time
q.connect()

