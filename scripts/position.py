#!/usr/bin/env python3

"""
position.py
Get GPS position from GPS device

Version 0.3

Steve de Bode - W0FFS - July 2026

Input:  None, uses DigiHubGPSport and DigiHubGPSbaud environment variables
Output: GPS Position - Latitude,Longitude

Exit codes:
 0 = position printed
 1 = no fix / no usable position
 2 = no GPS port or baud configured
 3 = serial open/read error
"""

from __future__ import annotations

try:
 import argparse
 import os
 import re
 import sys
 import time
 import serial
except ModuleNotFoundError:
 print("\nPython virtual environment required to execute.\n", file=sys.stderr)
 sys.exit(3)


NMEA_RE = re.compile(r"^\$(?P<body>[^*]+)\*(?P<ck>[0-9A-Fa-f]{2})\s*$")


def nmea_checksum_ok(sentence: str) -> bool:
 m = NMEA_RE.match(sentence.strip())
 if not m:
  return False

 body = m.group("body")
 given = int(m.group("ck"), 16)

 calc = 0
 for ch in body:
  calc ^= ord(ch)

 return calc == given


def nmea_coord_to_decimal(value: str, hemi: str) -> float | None:
 if not value or not hemi:
  return None

 try:
  raw = float(value)
 except ValueError:
  return None

 degrees = int(raw // 100)
 minutes = raw - degrees * 100
 decimal = degrees + minutes / 60.0

 if hemi.upper() in ("S", "W"):
  decimal = -decimal

 return decimal


def parse_position(sentence: str) -> tuple[float, float] | None:
 s = sentence.strip()

 if not s.startswith("$"):
  return None

 if "*" in s and not nmea_checksum_ok(s):
  return None

 core = s[1:].split("*", 1)[0]
 parts = core.split(",")

 if not parts or len(parts[0]) < 5:
  return None

 msg_type = parts[0][-3:]

 # RMC:
 # $GNRMC,time,status,lat,N/S,lon,E/W,...
 if msg_type == "RMC" and len(parts) >= 7:
  if parts[2].strip().upper() != "A":
   return None

  lat = nmea_coord_to_decimal(parts[3], parts[4])
  lon = nmea_coord_to_decimal(parts[5], parts[6])

  if lat is not None and lon is not None:
   return lat, lon

 # GGA:
 # $GNGGA,time,lat,N/S,lon,E/W,quality,...
 if msg_type == "GGA" and len(parts) >= 7:
  quality = parts[6].strip()

  if not quality.isdigit() or int(quality) <= 0:
   return None

  lat = nmea_coord_to_decimal(parts[2], parts[3])
  lon = nmea_coord_to_decimal(parts[4], parts[5])

  if lat is not None and lon is not None:
   return lat, lon

 # GLL:
 # $GNGLL,lat,N/S,lon,E/W,time,status,...
 if msg_type == "GLL" and len(parts) >= 7:
  if parts[6].strip().upper() != "A":
   return None

  lat = nmea_coord_to_decimal(parts[1], parts[2])
  lon = nmea_coord_to_decimal(parts[3], parts[4])

  if lat is not None and lon is not None:
   return lat, lon

 return None


def env_int(name: str, default: int = 0) -> int:
 value = os.getenv(name, "").strip()

 if not value:
  return default

 try:
  return int(value)
 except ValueError:
  return default


def main() -> int:
 default_baud = env_int("DigiHubGPSbaud", 0)

 parser = argparse.ArgumentParser()
 parser.add_argument("--timeout", type=float, default=5.0)
 parser.add_argument("--baud", type=int, default=default_baud)
 parser.add_argument("--debug", action="store_true")
 args = parser.parse_args()

 port = os.getenv("DigiHubGPSport", "").strip()

 if not port or port in ("nogps", "notfound"):
  return 2

 if args.baud <= 0:
  return 2

 deadline = time.monotonic() + args.timeout

 try:
  with serial.Serial(
   port=port,
   baudrate=args.baud,
   timeout=0.25,
   write_timeout=0,
   rtscts=False,
   dsrdtr=False,
   xonxoff=False,
  ) as ser:
   try:
    ser.reset_input_buffer()
   except serial.SerialException:
    pass

   while time.monotonic() < deadline:
    raw = ser.readline()

    if not raw:
     continue

    line = raw.decode("ascii", errors="ignore").strip()

    if args.debug:
     print(line, file=sys.stderr, flush=True)

    pos = parse_position(line)

    if pos is None:
     continue

    lat, lon = pos
    print(f"{lat:.7f},{lon:.7f}")
    return 0

  return 1

 except (serial.SerialException, OSError) as e:
  if args.debug:
   print(f"Serial error: {e}", file=sys.stderr, flush=True)
  return 3


if __name__ == "__main__":
 raise SystemExit(main())