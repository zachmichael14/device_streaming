from abc import ABC, abstractmethod
import asyncio
import multiprocessing
from queue import Queue

class DeviceManager(ABC):
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

    @abstractmethod
    def get_device_name(self):
        """Return the device name."""
        pass


"""
Implements a TCP Client to the Trigno SDK Server

To use the SDK 

Connect to the Trigno SDK Server via TCP/IP
• Configure the Trigno system hardware (see Section 5)
• Start data acquisition using one of two methods:
    o Send the command “START” over the Command port
    o Arm the system and send a start trigger to the Trigno Base Station (see the Trigno Wireless EMG System User Guide)
• Process the data streams that are being sent over the data ports (see Section 6

All data values are IEEE floats (4 bytes). For synchronization purposes, always process
bytes in segments determined by multiples of the following factor
    (No. of data channels on port) * (4 bytes/sample)

6.2 Packet Structure

Each command is terminated with <CR><LF>. The end of a command packet is terminated by
two consecutive <CR><LF> pairs, and the server will process app commands received
to this point when two <CR><LF> are received

"""

from timeit import default_timer
import numpy
from typing import Dict, Tuple, List
from pathlib import Path
from queue import Queue
from dataclasses import asdict
import threading
import json
import struct
import socket

from .datastructure import DSChannel, EMGSensor, EMGSensorMeta
__all__ = ("TrignoClient",)



COMMAND_PORT = 50040  # receives control commands, sends replies to commands
EMG_DATA_PORT = 50043  # sends EMG and primary non-EMG data
AUX_DATA_PORT = 50044  # sends auxiliary data

# IP_ADDR = "10.229.96.239"
IP_ADDR = "192.168.254.1" #QTM computer
# IP_ADDR = "10.229.96.210" #STim (Noah) computer

def _print(*args, **kwargs):
    print("[TrignoClient]", *args, **kwargs)


def recv(sock: socket.socket, maxlen=1024) -> bytes:
    "For receiving from the COMMAND_PORT"
    return sock.recv(maxlen).strip()

def recv_sz(sock: socket.socket, sz: int) -> bytes:
    "For receiving from the EMG_DATA_PORT"
    buf = b""
    while len(buf) < sz:
        buf += sock.recv(sz - len(buf))
    return buf

class TrignoClient:
    """
    DelsysClient interfaces with the Delsys SDK server via its TCP sockets.
    Handles device management and data streaming
    """

    # ZS: My understanding is that specifying __slots__ prevents internal
    # __dict__ from being instantiated, which both saves memory and prevents
    # dynamic allocation of attributes. I'm not sure why else this would be
    # used since it isn't explicitly referenced anywhere
    __slots__ = (
        "connected",
        "host_ip",
        "command_sock",
        "emg_data_sock",
        "sensors",
        "sensor_idx",
        "sensor_idx_0",
        "n_sensors",
        "sensor_meta",
        "start_time",
        "_done_streaming",
        "_worker_thread",
        "backwards_compatibility",
        "upsampling",
        "frame_interval",
        "max_samples_emg",
        "emg_sample_rate",
        "max_samples_aux",
        "aux_sample_rate",
        "endianness",
        "base_firmware",
        "base_serial",
    )


    def __init__(self, host_ip: str = IP_ADDR):
        self.connected = False
        self.host_ip = host_ip
        self._init_state()

    def _init_state(self):
        self.command_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.emg_data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.sensors: List[EMGSensor | None] = [None] * 17  # use 1 indexing
        self.sensor_idx: List[int] = []
        self.n_sensors = 0

        self.sensor_meta: Dict[str, EMGSensorMeta] = {}  # Mapping[serial, meta]

        self.start_time = 0.0
        self._done_streaming = threading.Event()
        self._worker_thread: threading.Thread | None = None

    def __call__(self, cmd: str):
        return self.send_cmd(cmd)

    # This was throwing an error and idk what it do
    # def __repr__(self):
    #     return "<{_class} @{_id:x} {_attrs}>".format(
    #         _class=self.__class__.__name__,
    #         _id=id(self) & 0xFFFFFF,
    #         _attrs=" ".join(
    #             "{}={!r}".format(k, getattr(self, k)) for k in sorted(self.__slots__)
    #         ),
    #     )

    def __getitem__(self, idx: int):
        return self.sensors[idx]

    def __len__(self) -> int:
        return len(self.sensors)

    def disconnect(self):
        self.stop_stream()
        self.command_sock.close()
        self.emg_data_sock.close()
        self._init_state()
        self.connected = False
        _print("Disconnected")

    def connect(self) -> str:
        """Called once during init to setup base station.

        Set little endian
        Sets backwards compatibility off (resample lower Fs channels to the highest Fs used)

        Returns error string if failed to connect.
        """
        if not self.connected:
            try:
                self.command_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.emg_data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.command_sock.settimeout(1)
                self.command_sock.connect((self.host_ip, COMMAND_PORT))
                self.command_sock.settimeout(5)
                buf = recv(self.command_sock)
                _print(buf.decode())
                self.emg_data_sock.connect((self.host_ip, EMG_DATA_PORT))
                self.connected = True
            except TimeoutError as e:
                err_str = "Failed to connect to Base Station: " + str(e)
                _print(err_str)
                return err_str

        self.connected = True
        cmd = lambda _cmd: self.send_cmd(_cmd).decode()

        # # Change settings
        assert cmd("ENDIAN LITTLE") == "OK"  # Use little endian
        assert cmd("BACKWARDS COMPATIBILITY ON") == "OK" #Reference page 12 of Trigno SDK User's Guide. With Upsampling on and BC on, we should be getting a 2k sampling rate!"""
        assert cmd("UPSAMPLE ON") == "OK"

        ### Queries
        self.backwards_compatibility = cmd("BACKWARDS COMPATIBILITY?")
        print(f'Backwards Compatibility: {self.backwards_compatibility}')

        self.upsampling = cmd("UPSAMPLING?")
        print(f'Upsampling: {self.upsampling}')

        # Trigno System frame interval, which is the length in time between frames
        self.frame_interval = float(cmd("FRAME INTERVAL?"))
        # expected maximum samples per frame for EMG channels. Divide by the frame interval to get expected EMG sample rate
        self.max_samples_emg = float(cmd("MAX SAMPLES EMG?"))
        self.emg_sample_rate = self.max_samples_emg / self.frame_interval

        # expected maximum samples per frame for AUX channels. Divide by the frame interval to get the expected AUX samples rate
        self.max_samples_aux = float(cmd("MAX SAMPLES AUX?"))
        self.aux_sample_rate = self.max_samples_aux / self.frame_interval

        self.endianness = cmd("ENDIANNESS?")
        # firmware version of the connected base station
        self.base_firmware = cmd("BASE FIRMWARE?")
        # firmware version of the connected base station
        self.base_serial = cmd("BASE SERIAL?")

        self.query_devices()
        self.sensor_idx_0 = numpy.array(self.sensor_idx)-1
        return ""

    def query_device(self, i: int):
        """
        Checks for devices connected to the base and updates `self.sensors`
        Also updates some settings
            - Force mode 40 (EMG only at 2146 Hz)
        """
        assert self.connected

        cmd = lambda _cmd: self.send_cmd(_cmd).decode()

        ## Only look at PAIRED and ACTIVE sensors
        if cmd(f"SENSOR {i} PAIRED?") == "NO":
            return

        if cmd(f"SENSOR {i} ACTIVE?") == "NO":
            return

        _type = cmd(f"SENSOR {i} TYPE?")
        print(_type)
        if _type == '25':  #TRIGGER
            # Force mode 41: SIG raw (2222Hz)
            res = cmd(f"SENSOR {i} SETMODE 41")
            _print(res,{'MODE Description': 'SIG raw (2222Hz)','Data Output':'1 Channel'}) 
            _mode = int(cmd(f"SENSOR {i} MODE?"))
        else:
            # Force mode 40: EMG (2148Hz)
            res = cmd(f"SENSOR {i} SETMODE 40")
            _mode = int(cmd(f"SENSOR {i} MODE?"))

        _serial = cmd(f"SENSOR {i} SERIAL?")
        firmware = cmd(f"SENSOR {i} FIRMWARE?")
        emg_channels = int(cmd(f"SENSOR {i} EMGCHANNELCOUNT?"))
        aux_channels = int(cmd(f"SENSOR {i} AUXCHANNELCOUNT?"))
        start_idx = int(cmd(f"SENSOR {i} STARTINDEX?"))

        channel_count = int(cmd(f"SENSOR {i} CHANNELCOUNT?"))
        channels = []
        for j in range(1, channel_count + 1):
            channels.append(
                DSChannel(
                    gain=float(cmd(f"SENSOR {i} CHANNEL {j} GAIN?")),
                    samples=int(cmd(f"SENSOR {i} CHANNEL {j} SAMPLES?")),
                    rate=float(cmd(f"SENSOR {i} CHANNEL {j} RATE?")),
                    units=cmd(f"SENSOR {i} CHANNEL {j} UNITS?"),
                )
            )

        return EMGSensor(
            serial=_serial,
            type=_type,
            mode=_mode,
            firmware=firmware,
            emg_channels=emg_channels,
            aux_channels=aux_channels,
            start_idx=start_idx,
            channel_count=channel_count,
            channels=channels,
        )

    def query_devices(self):
        """Query the Base Station for all 16 devices"""
        assert self.connected

        for i in range(1, 17):
            self.sensors[i] = self.query_device(i)

        self.sensor_idx = [i for i, s in enumerate(self.sensors) if s]
        self.n_sensors = sum([1 for s in self.sensors if s])

    def send_cmd(self, cmd: str) -> bytes:
        self.command_sock.send(cmd.encode() + b"\r\n\r\n")
        return recv(self.command_sock)

    def send_cmds(self, cmds: List[str]) -> List[bytes]:
        for cmd in cmds:
            self.command_sock.send(cmd.encode() + b"\r\n")
        self.command_sock.send(b"\r\n")
        return [recv(self.command_sock) for _ in cmds]

    def start_stream(self):
        assert self.connected
        self.send_cmd("START")
        self.start_time = default_timer()
        self._done_streaming.clear()

    def stop_stream(self):
        self._done_streaming.set()
        self._worker_thread and self._worker_thread.join()
        if self.connected:
            self.send_cmd("STOP")

    def recv_emg(self) -> Tuple[float, ...]:
        """
        Receive one EMG frame
        """
        buf = recv_sz(self.emg_data_sock, 4 * 16)  # 16 devices, 4 byte float
        return struct.unpack("<ffffffffffffffff", buf)

    def handle_stream(self, queue: Queue[Tuple[float]], savedir: Path, devices: numpy.ndarray):
        """
        If `queue` is passed, append data into the queue.
        If `savedir` is passed, write to `savedir/sensor_EMG.csv`.
            Also persist metadata in `savedir` before and after stream
        """
        assert self.connected
        self.start_stream()
        self.save_meta(savedir / "meta.json")
        self._worker_thread = threading.Thread(
            target=self.stream_worker, args=(queue, devices,savedir)
        )
        self._worker_thread.start()

    def stream_worker(self, queue: Queue[Tuple[float]], devices: numpy.ndarray,savedir: Path = None):
        """
        Stream worker calls `recv_emg` continuously until `self.streaming = False`
        """
        if not savedir:
            while not self._done_streaming.is_set():
                emg = self.recv_emg()
                emg_to_write = numpy.array(emg)[self.sensor_idx_0]
                queue.put(emg_to_write)
        else:
            with open(Path(savedir) / "temp_emg.csv", "w") as fp:
                fp.write(",".join([str(v) for v in devices]) + "\n")
                while not self._done_streaming.is_set():
                    try:
                        emg = self.recv_emg()
                    except struct.error as e:
                        _print("Failed to parse packet", e)
                        continue
                    emg_to_write = numpy.array(emg)[self.sensor_idx_0]
                    queue.put(emg_to_write)
                    fp.write(",".join([str(v) for v in emg_to_write]) + "\n")

            self.save_meta(savedir / "meta.json")

    def close(self):
        self.stop_stream()
        if self.connected:
            self.send_cmd("QUIT")
            self.connected = False
        self.command_sock.close()
        self.emg_data_sock.close()
        self.sensor_idx = []
        self.sensors = []

    def save_meta(self, fpath: Path | str):
        """Save metadata as JSON to fpath"""
        tmp = {k: asdict(v) for k, v in self.sensor_meta.items()}

        with open(fpath, "w") as fp:
            json.dump(tmp, fp, indent=2)

    def load_meta(self, fpath: Path | str):
        """Load JSON metadata from fpath"""
        with open(fpath, "r") as fp:
            tmp: Dict = json.load(fp)

        for k, v in tmp.items():
            self.sensor_meta[k] = EMGSensorMeta(**v)

    def __del__(self):
        self.close()


