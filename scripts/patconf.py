#!/usr/bin/env python3

"""
patconf.py
Generate $HOME/.config/pat/config.json from $HOME/.dhinfo

Version 0.1

Steve de Bode - W0FFS - July 2026

Input:  none
Output: writes $HOME/.config/pat/config.json

Exit codes:
 0 = config written successfully
 1 = .dhinfo missing, unreadable, or callsign empty
"""

from __future__ import annotations

import json
import os
import sys

DHINFO_FIELDS = [
 "callsign", "class", "expiry", "grid", "lat", "lon", "licstat",
 "forename", "initial", "surname", "suffix",
 "street", "town", "state", "zip", "country",
 "aprspass", "axnodepass", "mapboxtoken",
 "winlinkpass", "defaultmode", "radiointerface",
 "rigdevice", "rigbaud", "rignumber",
]

# Explicit, never left blank: Pat falls back to ":8080" when http_addr is
# unset, which would collide with dhweb's own default port.
HTTP_ADDR = "0.0.0.0:8015"


def load_dhinfo(path: str) -> dict[str, str]:
 with open(path, "r") as f:
  line = f.readline().rstrip("\n")
 fields = line.split(",")
 fields += [""] * (len(DHINFO_FIELDS) - len(fields))
 return dict(zip(DHINFO_FIELDS, fields[:len(DHINFO_FIELDS)]))


def build_config(info: dict[str, str], existing: dict) -> dict:
 """Merge .dhinfo identity fields into an existing config.json rather
 than overwriting it outright -- unlike direwolf.conf, this file is the
 user's actual Pat configuration and may carry hand-added connect_aliases,
 hamlib_rigs, or schedule entries from later DigiHub phases or manual
 tweaking. mycall/secure_login_password/locator always track .dhinfo;
 http_addr/listen are only seeded on first creation, never overwritten,
 so a deliberate change survives future runs. Everything else is left
 untouched."""
 config = dict(existing)
 config["mycall"] = info["callsign"].strip().upper()
 config["secure_login_password"] = info["winlinkpass"].strip()
 config["locator"] = info["grid"].strip()
 config.setdefault("http_addr", HTTP_ADDR)
 config.setdefault("listen", ["http"])
 return config


def main() -> int:
 dhinfo_path = os.path.join(os.path.expanduser("~"), ".dhinfo")

 try:
  info = load_dhinfo(dhinfo_path)
 except OSError:
  sys.stderr.write(".dhinfo not found; run install.sh first.\n")
  return 1

 if not info["callsign"].strip():
  sys.stderr.write(".dhinfo has no callsign set.\n")
  return 1

 config_dir = os.path.join(os.path.expanduser("~"), ".config", "pat")
 config_path = os.path.join(config_dir, "config.json")

 existing = {}
 if os.path.isfile(config_path):
  try:
   with open(config_path, "r") as f:
    existing = json.load(f)
  except (OSError, ValueError):
   existing = {}

 config = build_config(info, existing)

 try:
  os.makedirs(config_dir, exist_ok=True)
  with open(config_path, "w") as f:
   json.dump(config, f, indent=2)
   f.write("\n")
 except OSError as e:
  sys.stderr.write(f"Could not write {config_path}: {e}\n")
  return 1

 if not config["secure_login_password"]:
  sys.stderr.write(
   "Warning: winlinkpass is not set in .dhinfo; secure CMS login will "
   "not work until you set it with dhedit or dhweb.\n"
  )

 return 0


if __name__ == "__main__":
 raise SystemExit(main())
