import qtm
import asyncio
import xml.etree.ElementTree as ET
from typing import Optional, Any, List

class ConnectionError(Exception):
    """Custom exception for connection-related errors."""
    pass

class QTMClient:
    def __init__(self, ip: str, port: int = 22223, version: str = "1.22"):
        self._ip = ip
        self._port = port
        self._version = version
        self._connection = None
        self._connection_lock = asyncio.Lock()

    @property
    def connection(self):
        return self._connection

    def connect(self):
        """Synchronous wrapper for asynchronous connect method."""

        async def _async_connect() -> bool:
            """Asynchronous connection method."""
            try:
                self._connection = await qtm.connect(self._ip,
                                                     port=self._port,
                                                     version=self._version)
                                                     
                return self._connection is not None

            except asyncio.TimeoutError:
                raise ConnectionError(f"QTM connection timeout")
            except Exception as e:
                raise ConnectionError(f"QTM failed to connect: {e}")
            
        asyncio.run(_async_connect())

    def disconnect(self) -> bool:
        if self._connection is None:
            return True

        try:
            if hasattr(self._connection, 'disconnect'):
                self._connection.disconnect()
            self._connection = None
            return True

        except Exception as e:
            print(f"QTM disconnection error: {e}")
            return False

    def get_parameters(self,
                       parameters: Optional[List[str]] = None) -> ET.ElementTree:
        """Synchronous wrapper for asynchronous get_parameters method."""
        return self._loop.run_until_complete(self._async_get_parameters(parameters))

    async def _async_get_parameters(self,
                                    parameters: Optional[List[str]] = None) -> ET.ElementTree:
        """Asynchronous method to retrieve QTM settings parameters."""
        if not self._connection:
            raise ConnectionError("No active QTM connection")

        try:
            if parameters is None:
                parameters = ['all']

            xml_settings = await self._connection.get_parameters(parameters)
            return ET.fromstring(xml_settings)

        except Exception as e:
            raise ConnectionError(f"Error retrieving QTM parameters: {e}")
        
   
