#!/usr/bin/env python3

"""
gpstest.py
Test for installed and working GPS device

Version 0.4

Steve de Bode - W0FFS - July 2026

Input:  None
Output: GPS port,GPS status,GPS baud

Exit codes:
 0 = working
 1 = nofix
 2 = nodata
 3 = nogps
"""

from __future__ import annotations

try:
 import argparse
 import glob
 import os
 import re
 import stat
 import sys
 import time
 from dataclasses import dataclass
 from typing import Optional, Tuple
 import serial
 from serial.tools import list_ports
except ModuleNotFoundError:
 print("\nPython virtual environment required to execute.\n")
 sys.exit(0)


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


def parse_fix(sentence: str) -> Optional[bool]:
 s = sentence.strip()

 if not s.startswith("$"):
  return None

 core = s[1:]

 if "*" in core:
  core = core.split("*", 1)[0]

 parts = core.split(",")

 if not parts or len(parts[0]) < 5:
  return None

 msg_type = parts[0][-3:]

 if msg_type == "RMC" and len(parts) > 2:
  status_field = parts[2].strip().upper()

  if status_field == "A":
   return True

  if status_field == "V":
   return False

  return None

 if msg_type == "GGA" and len(parts) > 6:
  quality = parts[6].strip()

  if quality.isdigit():
   return int(quality) > 0

  return None

 if msg_type == "GLL" and len(parts) > 6:
  status_field = parts[6].strip().upper()

  if status_field == "A":
   return True

  if status_field == "V":
   return False

  return None

 return None


def is_char_device(path: str) -> bool:
 try:
  st = os.stat(path)
  return stat.S_ISCHR(st.st_mode)
 except OSError:
  return False


def linux_ports(include_ttys: bool = False, ttys_max: int = 4) -> list[str]:
 ports: list[str] = []

 # Prefer persistent Linux serial symlinks first.
 # These are stable across reboots and USB enumeration changes.
 ports.extend(glob.glob("/dev/serial/by-id/*"))

 try:
  ports.extend([p.device for p in list_ports.comports() if p.device])
 except Exception:
  pass

 ports.extend(glob.glob("/dev/ttyACM*"))
 ports.extend(glob.glob("/dev/ttyUSB*"))

 # Do not blindly scan /dev/ttyS*.
 # Many Linux systems expose ttyS0 through ttyS31 even when nothing is attached.
 if include_ttys:
  for i in range(ttys_max):
   ports.append(f"/dev/ttyS{i}")

 seen_realpaths = set()
 out: list[str] = []

 for dev in ports:
  try:
   real = os.path.realpath(dev)
  except OSError:
   continue

  if real in seen_realpaths:
   continue

  seen_realpaths.add(real)

  if os.path.exists(dev) and is_char_device(dev):
   out.append(dev)

 return out


@dataclass
class Result:
 port: str = ""
 status: str = "nogps"
 baud: int = 0


def sniff(port: str, baud: int, listen: float, debug: bool = False) -> Tuple[Result, bool, bool]:
 start = time.monotonic()
 nmea_ok = False
 opened_ok = False

 try:
  with serial.Serial(
   port=port,
   baudrate=baud,
   timeout=0.25,
   write_timeout=0,
   rtscts=False,
   dsrdtr=False,
   xonxoff=False,
  ) as ser:
   opened_ok = True
   time.sleep(0.05)

   try:
    ser.reset_input_buffer()
   except serial.SerialException:
    pass

   while time.monotonic() - start < listen:
    line = ser.readline()

    if not line:
     continue

    s = line.decode(errors="ignore").strip()

    if debug:
     print(f"{port}@{baud}: {s}", file=sys.stderr, flush=True)

    if not s.startswith("$") or "*" not in s:
     continue

    if not nmea_checksum_ok(s):
     continue

    nmea_ok = True
    fix = parse_fix(s)

    if fix is True:
     return Result(port, "working", baud), True, opened_ok

   if nmea_ok:
    return Result(port, "nofix", baud), True, opened_ok

   return Result("", "nodata", 0), False, opened_ok

 except (serial.SerialException, OSError) as e:
  if debug:
   print(f"{port}@{baud}: serial error: {e}", file=sys.stderr, flush=True)
  return Result("", "nogps", 0), False, False


def emit(r: Result) -> None:
 if r.status == "nogps":
  print("nogps,nogps,0")
 elif r.status == "nodata":
  print("nodata,nodata,0")
 else:
  print(f"{r.port},{r.status},{r.baud}")


def main() -> int:
 if not sys.platform.startswith("linux"):
  emit(Result("", "nogps", 0))
  return 3

 ap = argparse.ArgumentParser()
 ap.add_argument("--listen", type=float, default=2.0)
 ap.add_argument("--bauds", default="115200,9600,4800,38400,19200,57600")
 ap.add_argument("--include-ttys", action="store_true")
 ap.add_argument("--ttys-max", type=int, default=4)
 ap.add_argument("--debug", action="store_true")

 args = ap.parse_args()

 try:
  bauds = [int(x.strip()) for x in args.bauds.split(",") if x.strip()]
 except ValueError:
  emit(Result("", "nogps", 0))
  return 3

 ports = linux_ports(include_ttys=args.include_ttys, ttys_max=args.ttys_max)

 opened_any = False

 if args.debug:
  print(f"Ports to scan: {', '.join(ports) if ports else 'none'}", file=sys.stderr, flush=True)
  print(f"Bauds to scan: {', '.join(str(b) for b in bauds)}", file=sys.stderr, flush=True)

 for port in ports:
  for baud in bauds:
   if args.debug:
    print(f"Trying {port}@{baud}", file=sys.stderr, flush=True)

   r, nmea_ok, opened_ok = sniff(port, baud, args.listen, args.debug)
   opened_any |= opened_ok

   if r.status in ("working", "nofix"):
    emit(r)
    return 0 if r.status == "working" else 1

   if nmea_ok:
    break

 if opened_any:
  emit(Result("", "nodata", 0))
  return 2

 emit(Result("", "nogps", 0))
 return 3


if __name__ == "__main__":
 raise SystemExit(main())