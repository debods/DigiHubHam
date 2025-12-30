#!/usr/bin/env python3
"""
validcoords.py
Validate Latitude/Longitude ranges

Version 1.0b

Steve de Bode - KQ4ZCI - December 2025

Input:      Latitude Longitude
Exit codes: 0 = valid
            1 = invalid coordinates
            2 = invalid arguments
"""

import argparse
import sys


class SilentArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        # argparse-style error, but silent
        sys.exit(2)


def validate(latitude: float, longitude: float) -> None:
    """
    Validate latitude/longitude.

    Raises:
        ValueError: if latitude or longitude is out of range
    """
    if not (-90.0 <= latitude <= 90.0):
        raise ValueError("Latitude must be between -90 and 90.")
    if not (-180.0 <= longitude <= 180.0):
        raise ValueError("Longitude must be between -180 and 180.")


def main() -> None:
    parser = SilentArgumentParser(add_help=False)
    parser.add_argument("latitude", type=float)
    parser.add_argument("longitude", type=float)

    args = parser.parse_args()

    try:
        validate(args.latitude, args.longitude)
    except ValueError:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()