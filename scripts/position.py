#!/usr/bin/env python3

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


def checksum_ok(sentence: str) -> bool:
 m = NMEA_RE.match(sentence.strip())
 if not m:
  return False

 calc = 0
 for ch in m.group("body"):
  calc ^= ord(ch)

 return calc == int(m.group("ck"), 16)


def nmea_to_decimal(value: str, hemi: str) -> float | None:
 if not value or not hemi:
  return None

 try:
  raw = float(value)
 except ValueError:
  return None

 deg = int(raw // 100)
 minutes = raw - deg * 100
 dec = deg + minutes / 60.0

 if hemi.upper() in ("S", "W"):
  dec = -dec

 return dec


def parse_position(line: str) -> tuple[float, float] | None:
 line = line.strip()

 if not line.startswith("$"):
  return None

 if "*" in line and not checksum_ok(line):
  return None

 body = line[1:].split("*", 1)[0]
 parts = body.split(",")

 if not parts:
  return None

 msg = parts[0][-3:]

 # $GNRMC,time,A,lat,N,lon,W,...
 if msg == "RMC" and len(parts) >= 7:
  if parts[2].upper() != "A":
   return None

  lat = nmea_to_decimal(parts[3], parts[4])
  lon = nmea_to_decimal(parts[5], parts[6])

  if lat is not None and lon is not None:
   return lat, lon

 # $GNGGA,time,lat,N,lon,W,quality,...
 if msg == "GGA" and len(parts) >= 7:
  if not parts[6].isdigit() or int(parts[6]) <= 0:
   return None

  lat = nmea_to_decimal(parts[2], parts[3])
  lon = nmea_to_decimal(parts[4], parts[5])

  if lat is not None and lon is not None:
   return lat, lon

 # $GNGLL,lat,N,lon,W,time,A,...
 if msg == "GLL" and len(parts) >= 7:
  if parts[6].upper() != "A":
   return None

  lat = nmea_to_decimal(parts[1], parts[2])
  lon = nmea_to_decimal(parts[3], parts[4])

  if lat is not None and lon is not None:
   return lat, lon

 return None


def main() -> int:
 parser = argparse.ArgumentParser()
 parser.add_argument("--timeout", type=float, default=5.0)
 parser.add_argument("--baud", type=int, default=9600)
 parser.add_argument("--debug", action="store_true")
 args = parser.parse_args()

 port = os.getenv("DigiHubGPSport", "").strip()

 if not port or port in ("nogps", "notfound"):
  return 2

 deadline = time.monotonic() + args.timeout

 try:
  ser = serial.Serial(
   port=port,
   baudrate=args.baud,
   timeout=0.25,
   write_timeout=0,
   rtscts=False,
   dsrdtr=False,
   xonxoff=False,
  )
 except (serial.SerialException, OSError) as e:
  if args.debug:
   print(f"Serial open error: {e}", file=sys.stderr, flush=True)
  return 3

 try:
  with ser:
   ser.reset_input_buffer()

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
   print(f"Serial read error: {e}", file=sys.stderr, flush=True)
  return 3


if __name__ == "__main__":
 raise SystemExit(main())
