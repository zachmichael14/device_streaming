from enum import Enum
import socket
import struct

from src.clients.abstract_client import AbstractDeviceClient

class NotConnectedException(Exception):
    pass


class InvalidCommandException(Exception):
    pass


class CommandResponses(Enum):
    OK = "OK"
    INVALID = "INVALID COMMAND"
    CANT_COMPLETE = "CANNOT COMPLETE"


class TrignoClient(AbstractDeviceClient):
    COMMAND_PORT = 50040  # receives control commands, sends replies to commands
    EMG_DATA_PORT = 50043  # sends EMG and primary non-EMG data
    
    # AUX_DATA_PORT = 50044  # sends auxiliary data (not typically used)

    BASE_STATION_CONFIG_COMMANDS = [
        "ENDIAN LITTLE",
        "BACKWARDS COMPATIBILITY OFF",
        "UPSAMPLE ON",
    ]

    def __init__(self, host_ip: str):
        self.is_connected = False
        self.host_ip = host_ip

        self.command_socket = socket.socket(socket.AF_INET,
                                            socket.SOCK_STREAM)
        self.emg_data_socket = socket.socket(socket.AF_INET,
                                             socket.SOCK_STREAM)

    def connect(self):
        if self.is_connected:
            return
        
        self._connect_socket(self.command_socket, self.COMMAND_PORT)

        # Connecting the command socket causes a response from the base station
        # This response must be received before continuing.
        self._receive_command_response()

        self._connect_socket(self.emg_data_socket, self.EMG_DATA_PORT)

        self.is_connected = True
        print("Trigno connection successful.")
        self.configure()

    def disconnect(self):
        self.stop_streaming()
        if self.is_connected:
            self._send_command("QUIT")
            self.is_connected = False
        self.command_socket.close()
        self.emg_data_socket.close()

    def start_streaming(self):
        if not self.is_connected:
            self.connect()
        self._send_command("START")

    def stop_streaming(self):
        self._send_command("STOP")

    def _connect_socket(self, socket: socket.socket, port: str):
        try:
            socket.settimeout(3)
            socket.connect((self.host_ip, port))

        except TimeoutError as e:
            if port == self.COMMAND_PORT:
                print(f"Command socket failed to connect to Base Station: {e}")
            else:
                print(f"EMG socket failed to connect to Base Station: {e}")
        finally:
            # TODO: cleanup steps
            pass

    def _receive_command_response(self,
                                  max_packet_length: int = 1024,
                                  is_raw: bool = False):
        response = self.command_socket.recv(max_packet_length)
        if is_raw:
            return response
        return response.strip().decode() 
    
    def receive_emg_frame(self, frame_size: int = 16 * 4) -> tuple[float, ...]:
        """
        For receiving from the EMG_DATA_PORT.
        Data is a 4 byte float across 16 devices, so frame size is 4 * 16.
        """
        data_buffer = b""
        
        while len(data_buffer) < frame_size:
            data_buffer += self.emg_data_socket.recv(frame_size - len(data_buffer))
        return struct.unpack("<ffffffffffffffff", data_buffer)
    
    def _send_command(self, command: str) -> bytes:
        """
        Send command to the Trigno base station.
        The base station expects command packets to end with two pairs of 
        <CR> and <LF>, so those are appended to the end of the packet.
        """
        packet_end = b"\r\n\r\n"
        self.command_socket.send(command.encode() + packet_end)

        response = self._receive_command_response()

        if response == CommandResponses.INVALID:
            raise InvalidCommandException(f"<{command}> is not a valid Trigno command. Base station response: {response}")
        elif response == CommandResponses.CANT_COMPLETE:
            raise InvalidCommandException(f"<{command}> command can't be completed at this time. Base station response: {response}")
        
        return response
    
    def configure(self):
        responses = {}
        for command in self.BASE_STATION_CONFIG_COMMANDS:
            responses[command] = self._send_command(command)
        print("Base station config successful")
        self._verify_base_station_config(responses)
        
    def _verify_base_station_config(self, responses: dict[str, str]):
        """
        """
        for command, response in responses.items():
            if response != "OK":
                raise InvalidCommandException(f"<{command}> is not a valid Trigno Command. Base station response: {response}")

    def get_sensors(self):
        if not self.is_connected:
            raise NotConnectedException("Cannot find paired sensors - Base station not connected to server")
        
        paired_sensors = self._get_paired_sensors()
        print(f"Paired: {paired_sensors}")

        print(f"Active: {self._get_active_sensors()}")

    def _get_paired_sensors(self):
        return [i for i in range(1, 17) if self._send_command(f"SENSOR {i} PAIRED?") == "YES"]
    
    def _get_active_sensors(self):
        return [i for i in range(1, 17) if self._send_command(f"SENSOR {i} ACTIVE?") == "YES"]
