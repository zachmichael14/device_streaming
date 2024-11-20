from io import StringIO
from pathlib import Path
import pkg_resources




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

def load_full_emg_meta(fpath: Path):
    """This seems to be a stub as it doesn't return anything."""
    with open(fpath, "r") as fp:
        tmp: Dict = json.load(fp)
