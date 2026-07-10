#!/usr/bin/env python3

"""
gpsupdate.py
Update the stored GPS position in .dhinfo when it has moved beyond a threshold

Version 0.1

Steve de Bode - W0FFS - July 2026

Input:  None, uses DigiHubGPSport, DigiHubGPSbaud, DigiHubGPSthreshold
        environment variables. Reads and rewrites $HOME/.dhinfo
        (field 4 = grid, field 5 = latitude, field 6 = longitude).
Output: None

Exit codes:
 0 = no update needed (GPS not configured, or movement below threshold)
 1 = .dhinfo updated
 2 = .dhinfo missing or malformed
 3 = no GPS fix obtained (device unreachable or no satellite lock)
"""

from __future__ import annotations

try:
 import math
 import os
 import subprocess
 import sys
except ModuleNotFoundError:
 print("\nPython virtual environment required to execute.\n", file=sys.stderr)
 sys.exit(2)


LAT_FIELD = 4
LON_FIELD = 5
GRID_FIELD = 3
FIELD_COUNT = 18

EARTH_RADIUS_M = 6371000.0


def env_float(name: str, default: float) -> float:
 value = os.getenv(name, "").strip()

 if not value:
  return default

 try:
  return float(value)
 except ValueError:
  return default


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
 p1, p2 = math.radians(lat1), math.radians(lat2)
 dphi = math.radians(lat2 - lat1)
 dlambda = math.radians(lon2 - lon1)
 a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
 return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def get_position(script_dir: str, baud: int, timeout: float) -> tuple[float, float] | None:
 try:
  result = subprocess.run(
   [sys.executable, os.path.join(script_dir, "position.py"), "--baud", str(baud), "--timeout", str(timeout)],
   capture_output=True,
   text=True,
   timeout=timeout + 5.0,
  )
 except (OSError, subprocess.TimeoutExpired):
  return None

 if result.returncode != 0:
  return None

 try:
  lat_s, lon_s = result.stdout.strip().split(",")
  return float(lat_s), float(lon_s)
 except ValueError:
  return None


def get_grid(script_dir: str, lat: float, lon: float) -> str | None:
 try:
  result = subprocess.run(
   [sys.executable, os.path.join(script_dir, "maidenhead.py"), str(lat), str(lon)],
   capture_output=True,
   text=True,
   timeout=5.0,
  )
 except OSError:
  return None

 if result.returncode != 0:
  return None

 grid = result.stdout.strip()
 return grid or None


def main() -> int:
 home = os.getenv("HOME", "").strip()

 if not home:
  return 2

 dhinfo_path = os.path.join(home, ".dhinfo")

 port = os.getenv("DigiHubGPSport", "").strip()
 baud = os.getenv("DigiHubGPSbaud", "").strip()

 if not port or port in ("nogps", "nodata", "notfound") or not baud.isdigit():
  return 0

 try:
  with open(dhinfo_path, "r", encoding="utf-8") as f:
   fields = f.readline().rstrip("\n").split(",")
 except OSError:
  return 2

 if len(fields) != FIELD_COUNT:
  return 2

 script_dir = os.path.dirname(os.path.abspath(__file__))
 pos = get_position(script_dir, int(baud), timeout=5.0)

 if pos is None:
  return 3

 lat, lon = pos

 moved = None
 try:
  old_lat = float(fields[LAT_FIELD])
  old_lon = float(fields[LON_FIELD])
  moved = haversine_m(old_lat, old_lon, lat, lon)
 except ValueError:
  moved = None

 threshold_m = env_float("DigiHubGPSthreshold", 20.0)

 if moved is not None and moved < threshold_m:
  return 0

 grid = get_grid(script_dir, lat, lon)

 fields[LAT_FIELD] = f"{lat:.7f}"
 fields[LON_FIELD] = f"{lon:.7f}"

 if grid:
  fields[GRID_FIELD] = grid

 tmp_path = f"{dhinfo_path}.tmp"

 with open(tmp_path, "w", encoding="utf-8") as f:
  f.write(",".join(fields) + "\n")

 os.replace(tmp_path, dhinfo_path)
 return 1


if __name__ == "__main__":
 raise SystemExit(main())
