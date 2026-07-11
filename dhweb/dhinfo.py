"""
dhinfo.py
Shared $HOME/.dhinfo read/write helpers for DigiHub Python tooling.

Not a standalone command; imported by dhweb's app.py.
"""

import os
import shutil

FIELD_NAMES = [
    "callsign", "class", "expiry", "grid", "lat", "lon", "licstat",
    "forename", "initial", "surname", "suffix",
    "street", "town", "state", "zip", "country",
    "aprspass", "axnodepass", "mapboxtoken",
    "winlinkpass", "defaultmode", "radiointerface",
    "rigdevice", "rigbaud", "rignumber",
    "vncpass",
]

FIELD_COUNT = len(FIELD_NAMES)


def dhinfo_path():
    return os.path.join(os.path.expanduser("~"), ".dhinfo")


def load_dhinfo(path=None):
    path = path or dhinfo_path()
    with open(path, "r") as f:
        line = f.readline().rstrip("\n")
    fields = line.split(",")
    if len(fields) < FIELD_COUNT:
        fields += [""] * (FIELD_COUNT - len(fields))
    return dict(zip(FIELD_NAMES, fields[:FIELD_COUNT]))


def save_dhinfo(values, path=None):
    path = path or dhinfo_path()

    if os.path.exists(path):
        try:
            shutil.copyfile(path, path + ".last")
        except OSError:
            pass

    line = ",".join(values.get(name, "") for name in FIELD_NAMES)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        f.write(line + "\n")
    os.replace(tmp, path)
