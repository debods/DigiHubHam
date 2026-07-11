#!/usr/bin/env python3

"""
audiodetect.py
Best-effort ALSA capture device auto-detection, shared by direwolfconf.py
and dhardopd. Not a standalone DigiHub command in its own right, but can
be run directly to print the detected device (or nothing, exit 1, if no
confident single candidate was found).

Version 0.1

Steve de Bode - W0FFS - July 2026

Input:  none
Output: "plughw:N,0" on stdout, or nothing

Exit codes:
 0 = a single confident candidate was found and printed
 1 = no confident candidate (caller should fall back to the system default)
"""

from __future__ import annotations

import re
import subprocess
import sys

# ALSA card identifiers that are virtually never a radio interface, used to
# steer best-effort ADEVICE auto-detection away from a system's built-in
# audio. This is a heuristic, not a guarantee.
BUILTIN_AUDIO_HINTS = (
 "hdmi", "bcm2835", "vc4", "pch", "generic", "headphone",
 "builtin", "internal", "pulse", "default",
)


def detect_adevice() -> str | None:
 """Best-effort ALSA capture card auto-detection via `arecord -l`.
 Returns a "plughw:N,0" string, or None if no confident single
 candidate was found (caller should omit the device option and let
 the consuming program use its own system default)."""
 try:
  out = subprocess.run(
   ["arecord", "-l"], capture_output=True, text=True, timeout=5
  ).stdout
 except (OSError, subprocess.SubprocessError):
  return None

 candidates = []
 for m in re.finditer(r"^card (\d+): (\S+) \[(.*?)\]", out, re.MULTILINE):
  idx, cardid, desc = m.group(1), m.group(2), m.group(3)
  haystack = f"{cardid} {desc}".lower()
  if any(hint in haystack for hint in BUILTIN_AUDIO_HINTS):
   continue
  candidates.append(idx)

 if len(candidates) == 1:
  return f"plughw:{candidates[0]},0"
 return None


def main() -> int:
 device = detect_adevice()
 if device:
  print(device)
  return 0
 return 1


if __name__ == "__main__":
 raise SystemExit(main())
