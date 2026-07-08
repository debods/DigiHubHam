#!/usr/bin/env python3

"""
position.py
Get GPS position from GPS device

Version 1.1

Steve de Bode - W0FFS - December 2025

Input:  None, uses DigiHubGPSport environment variable
Output: GPS Position - Latitude,Longitude

Exit codes:
 0 = position printed
 1 = no fix / no usable position
 2 = no GPS port configured
 3 = serial open/read error
"""

try:
 import argparse
 import os
 import sys
 import time
 import serial
 import pynmea2
except ModuleNotFoundError:
 print("\nPython virtual environment required to execute.\n", file=sys.stderr)
 sys.exit(3)


def main() -> int:
 parser = argparse.ArgumentParser()
 parser.add_argument("--timeout", type=float, default=15.0)
 parser.add_argument("--baud", type=int, default=9600)
 parser.add_argument("--debug", action="store_true")
 args = parser.parse_args()

 port = os.getenv("DigiHubGPSport", "").strip()

 if not port or port == "nogps" or port == "notfound":
  return 2

 start = time.time()

 try:
  with serial.Serial(port, args.baud, timeout=1) as ser:
   while time.time() - start < args.timeout:
    raw = ser.readline()

    if not raw:
     continue

    line = raw.decode("ascii", errors="ignore").strip()

    if args.debug:
     print(line, file=sys.stderr, flush=True)

    if not line.startswith(("$GNRMC", "$GPRMC")):
     continue

    try:
     msg = pynmea2.parse(line)
    except pynmea2.ParseError:
     continue

    if getattr(msg, "status", "") != "A":
     continue

    lat = float(msg.latitude)
    lon = float(msg.longitude)

    print(f"{lat:.7f},{lon:.7f}")
    return 0

  return 1

 except (serial.SerialException, OSError):
  return 3


if __name__ == "__main__":
 raise SystemExit(main())
