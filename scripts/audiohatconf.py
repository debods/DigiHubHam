#!/usr/bin/env python3

"""
audiohatconf.py
Apply the Raspberry Pi device-tree overlay matching $HOME/.dhinfo's
radiointerface field, for DigiHub's I2S audio HAT interfaces (fepi, aiz,
drapizero)

Version 0.1

Steve de Bode - W0FFS - July 2026

Input:  none - reads $HOME/.dhinfo's radiointerface field
Output: writes /boot/firmware/config.txt (or /boot/config.txt)

Confirmed against DigiPi's own home/pi/localize.sh (github.com/craigerl/
digipi): aiz and drapizero both use dtoverlay=audioinjector-wm8731-audio;
fepi is the baseline dtoverlay=fe-pi-audio; digipihat needs no dtoverlay
change at all. Every other radiointerface value (cm108, aioc, usbradio,
digirig, usbaudio) is a USB/external device, not an I2S HAT, so none of
them need one either.

Exit codes:
 0 = no overlay change was needed for the current radiointerface (this
     includes non-HAT interfaces like usbaudio/cm108/digirig -- not an
     error, just nothing to do)
 1 = .dhinfo missing/unreadable, or no config.txt found (not a
     Raspberry Pi, or an unrecognized boot layout)
 2 = config.txt could not be written
"""

from __future__ import annotations

import os
import pwd
import re
import sys

DHINFO_FIELDS = [
 "callsign", "class", "expiry", "grid", "lat", "lon", "licstat",
 "forename", "initial", "surname", "suffix",
 "street", "town", "state", "zip", "country",
 "aprspass", "axnodepass", "mapboxtoken",
 "winlinkpass", "defaultmode", "radiointerface",
 "rigdevice", "rigbaud", "rignumber",
]

CONFIG_TXT_CANDIDATES = ["/boot/firmware/config.txt", "/boot/config.txt"]

# Every overlay DigiHub knows how to manage; when one is activated, any
# other listed here is commented out, since they all claim the same I2S
# audio interface and can't coexist.
MANAGED_OVERLAYS = ["fe-pi-audio", "audioinjector-wm8731-audio"]

RADIOINTERFACE_OVERLAY = {
 "fepi": "fe-pi-audio",
 "aiz": "audioinjector-wm8731-audio",
 "drapizero": "audioinjector-wm8731-audio",
}


def user_home() -> str:
 """Resolve the invoking (pre-sudo) user's home directory, since
 audiohatconf.py needs root to write /boot/firmware/config.txt but
 .dhinfo lives under the DigiHub user's own home, not root's."""
 sudo_user = os.environ.get("SUDO_USER")
 if sudo_user and sudo_user != "root":
  try:
   return pwd.getpwnam(sudo_user).pw_dir
  except KeyError:
   pass
 return os.path.expanduser("~")


def load_dhinfo(path: str) -> dict[str, str]:
 with open(path, "r") as f:
  line = f.readline().rstrip("\n")
 fields = line.split(",")
 fields += [""] * (len(DHINFO_FIELDS) - len(fields))
 return dict(zip(DHINFO_FIELDS, fields[:len(DHINFO_FIELDS)]))


def find_config_txt() -> str | None:
 for path in CONFIG_TXT_CANDIDATES:
  if os.path.isfile(path):
   return path
 return None


def patch_config_txt(text: str, target_overlay: str) -> tuple[str, bool]:
 """Ensure target_overlay is active and every other managed overlay is
 commented out. Returns (new_text, changed)."""
 lines = text.split("\n")
 changed = False
 target_active = False

 overlay_re = re.compile(r'^(\s*)(#\s*)?dtoverlay=([A-Za-z0-9_-]+)\s*$')

 for i, line in enumerate(lines):
  m = overlay_re.match(line)
  if not m:
   continue
  indent, hashmark, overlay = m.groups()
  if overlay not in MANAGED_OVERLAYS:
   continue

  if overlay == target_overlay:
   target_active = True
   if hashmark:
    lines[i] = f"{indent}dtoverlay={overlay}"
    changed = True
  elif not hashmark:
   lines[i] = f"{indent}#dtoverlay={overlay}"
   changed = True

 new_text = "\n".join(lines)

 if not target_active:
  sep = "" if new_text.endswith("\n") else "\n"
  new_text = f"{new_text}{sep}dtoverlay={target_overlay}\n"
  changed = True

 return new_text, changed


def main() -> int:
 home = user_home()

 try:
  info = load_dhinfo(os.path.join(home, ".dhinfo"))
 except OSError:
  sys.stderr.write(".dhinfo not found; run install.sh first.\n")
  return 1

 radiointerface = info["radiointerface"].strip().lower()
 target_overlay = RADIOINTERFACE_OVERLAY.get(radiointerface)

 if target_overlay is None:
  sys.stdout.write(
   f'radiointerface "{radiointerface or "(unset)"}" needs no audio HAT '
   "device-tree overlay; nothing to do.\n"
  )
  return 0

 config_path = find_config_txt()
 if config_path is None:
  sys.stderr.write(
   "No /boot/firmware/config.txt or /boot/config.txt found -- this "
   "isn't a Raspberry Pi (or uses an unrecognized boot layout), so "
   "audio HAT device-tree overlays don't apply here.\n"
  )
  return 1

 try:
  with open(config_path, "r") as f:
   text = f.read()
 except OSError as e:
  sys.stderr.write(f"Could not read {config_path}: {e}\n")
  return 2

 new_text, changed = patch_config_txt(text, target_overlay)

 if not changed:
  sys.stdout.write(
   f"dtoverlay={target_overlay} is already active in {config_path}; "
   "nothing to do.\n"
  )
  return 0

 try:
  with open(config_path, "w") as f:
   f.write(new_text)
 except OSError as e:
  sys.stderr.write(f"Could not write {config_path}: {e}\n")
  return 2

 sys.stdout.write(
  f"Set dtoverlay={target_overlay} in {config_path}. "
  "Reboot for this to take effect.\n"
 )
 return 0


if __name__ == "__main__":
 raise SystemExit(main())
