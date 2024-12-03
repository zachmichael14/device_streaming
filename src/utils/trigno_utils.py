from dataclasses import asdict, dataclass
from io import StringIO
import json
from pathlib import Path
import pkg_resources
import time
from typing import Dict, List


__all__ = ("EMGSensorMeta", "EMGSensor", "DSChannel")


@dataclass
class DSChannel:
    "A channel on a given sensor"
    gain: float  # gain
    samples: int  # native samples per frame
    rate: float  # native sample rate in Hz
    units: str  # unit of the data


@dataclass
class EMGSensor:
    """Delsys EMG Sensor properties queried from the Base Station"""

    type: str
    serial: str
    mode: int
    firmware: str
    emg_channels: int
    aux_channels: int

    start_idx: int
    channel_count: int
    channels: List[DSChannel]


@dataclass
class EMGSensorMeta:
    """Metadata associated with a EMG sensor
    Most importantly sensor placement
    """

    muscle_name: str = ""
    side: str = ""


def load_avanti_modes():
    """Load Avanti modes file. Must use Unix line endings."""
    raw = pkg_resources.resource_string(__name__, "avanti_modes.tsv").decode()
    buf = StringIO(raw.strip())
    keys = buf.readline().strip().split("\t")[1:]
    modes = {}
    for _line in buf.readlines():
        line = _line.strip().split("\t")
        modes[int(line[0])] = {k: v for k, v in zip(keys, line[1:])}
    return modes

def load_meta(self, fpath: Path | str):
        """Load JSON metadata from fpath"""
        with open(fpath, "r") as fp:
            tmp: Dict = json.load(fp)

        for k, v in tmp.items():
            self.sensor_meta[k] = EMGSensorMeta(**v)

def save_meta(self, fpath: Path | str, slim=False):
    """Save metadata as JSON to fpath"""
    tmp = {k: asdict(v) for k, v in self.sensor_meta.items()}

    with open(fpath, "w") as fp:
        json.dump(tmp, fp, indent=2)

def get_current_time(self):
    timestamp = time.time()
    milliseconds = int(timestamp * 1000) % 1000
    formatted_timestamp = time.strftime("%H:%M:%S",
                                        time.localtime(timestamp)) + f".{milliseconds:03}"
    return formatted_timestamp