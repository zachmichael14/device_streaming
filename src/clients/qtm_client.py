import qtm
import asyncio
import logging
import contextlib
from typing import Optional, Any

class ConnectionError(Exception):
    """Custom exception for connection-related errors."""
    pass

class QTMClient:
    def __init__(self, ip, port, version):
        self.ip = ip
        self.port = port
        self.version = version
        self._connection = None
        self._connection_lock = asyncio.Lock()
        self._connection_task: Optional[asyncio.Task] = None

    @property
    def connection(self):
        return self._connection
    
    def connect(self, timeout: float = 10.0) -> bool:
        """
        Synchronous wrapper for connect method.
        
        Handles running async method in different contexts.
        """
        loop = self._get_or_create_event_loop()

        try:
            return loop.run_until_complete(self._connect(timeout))
        except Exception as e:
            logging.error(f"Sync connection error: {e}")
            return False

    async def _connect(self, timeout: float = 10.0) -> bool:
        """
        Asynchronous connection method with advanced error handling.
        
        Args:
            timeout: Maximum time to wait for connection (default 10 seconds)
        
        Returns:
            Boolean indicating successful connection
        
        Raises:
            ConnectionError for connection-specific issues
        """
        # Prevent multiple simultaneous connection attempts
        async with self._connection_lock:
            # Cancel any existing connection task
            if self._connection_task and not self._connection_task.done():
                self._connection_task.cancel()
                try:
                    await self._connection_task
                except asyncio.CancelledError:
                    pass

            try:
                # Create a task with timeout
                self._connection_task = asyncio.create_task(
                    asyncio.wait_for(self._establish_connection(), 
                                     timeout=timeout)
                )

                # Wait for the connection task to complete
                self._connection = await self._connection_task
                return self._connection is not None

            except asyncio.TimeoutError:
                print(f"Connection to {self.ip}:{self.port} timed out")
                raise ConnectionError(f"Connection timeout after {timeout} seconds")
            except Exception as e:
                print(f"Connection error: {e}")
                raise ConnectionError(f"Failed to connect: {e}")

    async def _establish_connection(self) -> Any:
        """
        Internal method to establish the actual connection.
        
        Separated for cleaner error handling and potential retry logic.
        """
        try:
            connection = await qtm.connect(
                self.ip, 
                port=self.port, 
                version=self.version
            )
            
            if connection is None:
                print(f"Connection to {self.ip}:{self.port} returned None")
                return None
            
            return connection

        except Exception as e:
            logging.error(f"Connection establishment failed: {e}")
            raise

    def disconnect(self) -> bool:
        """
        Disconnect from the device.

        Args:
            force: Optional parameter for forced disconnection if needed

        Returns:
            Boolean indicating successful disconnection
        """
        if self._connection is None:
            return True

        try:
            # Non-async disconnection method
            if hasattr(self._connection, 'disconnect'):
                self._connection.disconnect()

            self._connection = None
            return True
    
        except Exception as e:
            print(f"Disconnection error: {e}")
            return False

    def _get_or_create_event_loop(self):
        try:
            # Attempt to use existing event loop
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # Create new event loop if no running loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop


 abstract_client.py clients/abstract_client.py clients/trigno_client.py managers/abstract_manager.py managers/trigno_manager.py qtm_client.py trigno_client.py trigno_manager.py trigno_utils.py utils/trigno_utils.py