#!/usr/bin/env python3

"""
geocode.py
Geocode a street address into latitude/longitude using the Mapbox
Geocoding API

Version 0.1

Steve de Bode - W0FFS - July 2026

Input:  address (single argument)
        Uses the MAPBOX_TOKEN environment variable
Output: Latitude,Longitude

Exit codes:
 0 = geocoded successfully
 1 = no result found, or the API request failed
 2 = invalid arguments or missing MAPBOX_TOKEN
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def geocode(address: str, token: str) -> tuple[float, float] | None:
 url = (
  "https://api.mapbox.com/geocoding/v5/mapbox.places/"
  + urllib.parse.quote(address)
  + ".json?limit=1&access_token="
  + urllib.parse.quote(token)
 )

 try:
  with urllib.request.urlopen(url, timeout=10) as resp:
   data = json.load(resp)
 except (urllib.error.URLError, TimeoutError, ValueError, OSError):
  return None

 features = data.get("features") or []
 if not features:
  return None

 center = features[0].get("center")
 if not isinstance(center, list) or len(center) != 2:
  return None

 lon, lat = center

 try:
  return float(lat), float(lon)
 except (TypeError, ValueError):
  return None


def main() -> int:
 if len(sys.argv) != 2 or not sys.argv[1].strip():
  return 2

 token = os.getenv("MAPBOX_TOKEN", "").strip()
 if not token:
  return 2

 result = geocode(sys.argv[1], token)
 if result is None:
  return 1

 lat, lon = result
 print(f"{lat:.7f},{lon:.7f}")
 return 0


if __name__ == "__main__":
 raise SystemExit(main())
