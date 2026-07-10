#!/usr/bin/env python3
"""
dhweb app.py
DigiHub web configuration interface (Flask, served by waitress).

Not run directly by hand; started via the scripts/dhweb wrapper.

Input:  [host] [port]  (both optional, default 0.0.0.0:8080)
Output: none - runs the DigiHub web UI until stopped
"""

import os
import subprocess
import sys

from flask import Flask, redirect, render_template, request, url_for

import dhinfo

BIN_DIR = os.environ.get("DIGIHUB_BIN_DIR", "/usr/local/bin")

CLASS_LABELS = {
    "T": "Technician",
    "G": "General",
    "E": "Extra",
    "N": "Novice",
    "A": "Advanced",
    "": "Unknown",
}

LICSTAT_LABELS = {
    "A": "Active",
    "E": "Expired",
    "P": "Pending",
    "": "Unknown",
}

DEFAULT_MODES = [
    "standby", "tnc", "tnc300b", "tracker", "digipeater", "webchat",
    "node", "winlinkrms", "wsjtx", "js8call", "sstv", "fldigi",
]

RADIO_INTERFACES = [
    "", "aioc", "usbradio", "cm108", "fepi", "digirig",
    "drapizero", "digipihat", "aiz", "usbaudio",
]

app = Flask(__name__)


def run_worker(name, *args):
    """Run an installed DigiHub Python worker; return (returncode, stdout)."""
    cmd = [sys.executable, os.path.join(BIN_DIR, name), *args]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout.strip()


def is_valid_callsign(callsign):
    code, _ = run_worker("validcall.py", callsign)
    return code == 0


def valid_coords_and_grid(lat, lon):
    """Return (ok, grid). grid is unchanged/empty on failure."""
    code, _ = run_worker("validcoords.py", lat, lon)
    if code != 0:
        return False, ""
    code, grid = run_worker("maidenhead.py", lat, lon)
    if code != 0 or not grid:
        return False, ""
    return True, grid


def regenerate_aprspass(callsign):
    code, out = run_worker("aprspass.py", callsign)
    return out if code == 0 else ""


@app.route("/")
def index():
    return redirect(url_for("config"))


@app.route("/config", methods=["GET", "POST"])
def config():
    errors = []
    values = dhinfo.load_dhinfo()

    if request.method == "POST":
        for name in dhinfo.FIELD_NAMES:
            if name in ("aprspass", "grid"):
                continue
            values[name] = request.form.get(name, "").strip()

        values["callsign"] = values["callsign"].strip().upper()

        if not values["callsign"]:
            errors.append("Callsign is required.")
        elif not is_valid_callsign(values["callsign"]):
            errors.append(
                f"\"{values['callsign']}\" is not a valid US callsign format."
            )

        lat, lon = values.get("lat", ""), values.get("lon", "")
        if lat or lon:
            ok, grid = valid_coords_and_grid(lat, lon)
            if not ok:
                errors.append("Latitude/longitude are invalid; grid left unchanged.")
            else:
                values["grid"] = grid

        if not errors:
            values["aprspass"] = regenerate_aprspass(values["callsign"])
            dhinfo.save_dhinfo(values)
            return redirect(url_for("config", saved=1))

    return render_template(
        "config.html",
        values=values,
        errors=errors,
        saved=request.args.get("saved") == "1",
        class_labels=CLASS_LABELS,
        licstat_labels=LICSTAT_LABELS,
        default_modes=DEFAULT_MODES,
        radio_interfaces=RADIO_INTERFACES,
    )


def main():
    from waitress import serve

    host = sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    serve(app, host=host, port=port)


if __name__ == "__main__":
    main()
