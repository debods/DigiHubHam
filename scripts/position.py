#!/usr/bin/env python3

"""
gpsposition.py
get GPS position from GPS device

Version 1.0a

Steve de Bode - W0FFS - December 2025

Input:  None (GPS Device)
Output: GPS Position - Latitude,Longitude
"""

try:
 import os
 import sys
 import serial
 import pynmea2
except ModuleNotFoundError:
 print("\nPython virtual environment required to execute,\n")
 print("Please run the wrapper script gpsposition instead.\n")
 sys.exit(0)

PORT = os.getenv("DigiHubGPSport")

if PORT == "nogps":
 print("\nNo GPS device is configured for DigiHub, please run editconfig if this is incorrect.\n")
 sys.exit(0)

def main():
 ser = serial.Serial(PORT, 9600, timeout=1)

 while True:
  line = ser.readline().decode("ascii", errors="ignore").strip()
  if not line:
   continue

  msg = None

  if line.startswith("$GNRMC") or line.startswith("$GPRMC"):
   try:
    msg = pynmea2.parse(line)
   except pynmea2.ParseError:
    continue
  else:
   continue

  if msg.status != "A":
   continue

  lat = msg.latitude
  lon = msg.longitude

  print(f"{lat:.7f},{lon:.7f}")
  break

if __name__ == "__main__":
 main()
