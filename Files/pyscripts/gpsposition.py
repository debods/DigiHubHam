#!/usr/bin/env python3

"""
gpsposition.py
Get curent position from GPS

Version 1.0a

Steve de Bode - KQ4ZCI - December 2025

Output: Latitude,Longitude
"""

try:
 import os
 import serial
 import pynmea2
except ModuleNotFoundError:
 venv_dir = os.getenv("DigiHubvenv")
 print("\nPython virtual environmnet required to execute:")
 print(f"\nsource {venv_dir}/bin/activate\n")
 exit(1)

PORT = os.getenv("DigiHubvenv")

def main():
 ser = serial.Serial(PORT, 9600, timeout=1)

 while True:
  line = ser.readline().decode('ascii', errors='ignore').strip()
  if not line:
   continue

  if line.startswith("$GNRMC") or line.startswith("$GPRMC"):
   try:
    msg = pynmea2.parse(line)
   except:
    continue

  if msg.status != "A":
   continue

  lat = msg.latitude
  lon = msg.longitude

  print(f"{lat:.6f},{lon:.6f}")
  break

if __name__ == "__main__":
 main()