#!/usr/bin/env python3

"""
hamgrid.py
Convert latitude and longitude into Maidenhead Grid

Version 1.0c

Steve de Bode - KQ4ZCI - December 2025

Input: latitude longitude
Output: Maidenhead Grid Square

Exit codes:
  0 = valid + printed grid
  1 = invalid coordinates
  2 = invalid arguments
"""

import argparse
import sys
import validcoords


class SilentArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        # Silent argparse error (no usage text)
        sys.exit(2)


def grid_conversion(latitude: float, longitude: float) -> str:
    field_lon = int((longitude + 180) / 20)
    field_lat = int((latitude + 90) / 10)
    grid = chr(ord("A") + field_lon) + chr(ord("A") + field_lat)

    square_lon = int(((longitude + 180) % 20) / 2)
    square_lat = int(((latitude + 90) % 10) / 1)
    grid += str(square_lon) + str(square_lat)

    subsquare_lon = int((((longitude + 180) % 20) % 2) / (2 / 24))
    subsquare_lat = int((((latitude + 90) % 10) % 1) / (1 / 24))
    grid += chr(ord("A") + subsquare_lon) + chr(ord("A") + subsquare_lat)

    return grid


def main() -> int:
    parser = SilentArgumentParser(add_help=False)
    parser.add_argument("latitude", type=float)
    parser.add_argument("longitude", type=float)
    args = parser.parse_args()

    try:
        validcoords.validate(args.latitude, args.longitude)
    except ValueError:
        return 1

    maidenhead = grid_conversion(args.latitude, args.longitude)
    maidenhead = maidenhead[:-2] + maidenhead[-2:].lower()
    print(maidenhead)
    return 0


if __name__ == "__main__":
    sys.exit(main())