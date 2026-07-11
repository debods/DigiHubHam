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
import fldigi_client

BIN_DIR = os.environ.get("DIGIHUB_BIN_DIR", "/usr/local/bin")
# The default here must exactly match the path named in install.sh's
# NOPASSWD sudoers rule (/usr/local/bin/dhmode) or mode switching will
# silently fail with sudo blocking on a password prompt that can never be
# answered. Only override DIGIHUB_DHMODE_BIN for testing.
DHMODE_BIN = os.environ.get("DIGIHUB_DHMODE_BIN", "/usr/local/bin/dhmode")
# Same constraint as DHMODE_BIN above: must match install.sh's sudoers rule.
DHRIG_BIN = os.environ.get("DIGIHUB_DHRIG_BIN", "/usr/local/bin/dhrig")

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


def mode_services(mode):
    """Ask dhmode which systemd service(s) a mode maps to (read-only,
    no sudo needed). Returns a list, empty if the mode has no service
    wired up yet."""
    try:
        result = subprocess.run(
            [DHMODE_BIN, "--services", mode],
            capture_output=True, text=True, timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if result.returncode != 0:
        return []
    return [s for s in result.stdout.split() if s]


def service_status(service):
    try:
        result = subprocess.run(
            ["systemctl", "is-active", service],
            capture_output=True, text=True, timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    return result.stdout.strip() or "unknown"


def service_log_tail(service, lines=50):
    try:
        result = subprocess.run(
            ["journalctl", "-u", service, "-n", str(lines), "--no-pager"],
            capture_output=True, text=True, timeout=5,
        )
    except (OSError, subprocess.SubprocessError) as e:
        return f"(could not read logs: {e})"
    return result.stdout or "(no log output)"


def switch_mode(mode):
    """Run dhmode via the NOPASSWD sudoers rule install.sh sets up.
    Returns (ok, output)."""
    try:
        result = subprocess.run(
            ["sudo", "-n", DHMODE_BIN, mode],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as e:
        return False, str(e)
    output = (result.stdout + result.stderr).strip()
    return result.returncode == 0, output


def rig_toggle(action):
    """Run dhrig via the NOPASSWD sudoers rule install.sh sets up.
    Returns (ok, output)."""
    try:
        result = subprocess.run(
            ["sudo", "-n", DHRIG_BIN, action],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as e:
        return False, str(e)
    output = (result.stdout + result.stderr).strip()
    return result.returncode == 0, output


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


@app.route("/mode", methods=["GET", "POST"])
def mode():
    message = None
    ok = None

    if request.method == "POST":
        requested = request.form.get("mode", "")
        if requested not in DEFAULT_MODES:
            message, ok = f'Unknown mode "{requested}".', False
        else:
            ok, output = switch_mode(requested)
            message = output or (
                f'Switched to "{requested}".' if ok else "Mode switch failed."
            )
        message = " ".join(message.split())[:300]
        return redirect(url_for("mode", msg=message, ok="1" if ok else "0"))

    values = dhinfo.load_dhinfo()
    current = values.get("defaultmode") or "standby"
    services = mode_services(current)
    statuses = {s: service_status(s) for s in services}
    log_tail = service_log_tail(services[0]) if services else None

    msg = request.args.get("msg")
    msg_ok = request.args.get("ok") == "1"

    return render_template(
        "mode.html",
        current=current,
        default_modes=DEFAULT_MODES,
        services=services,
        statuses=statuses,
        log_tail=log_tail,
        log_service=services[0] if services else None,
        message=msg,
        message_ok=msg_ok,
    )


@app.route("/rig", methods=["GET", "POST"])
def rig():
    message = None
    ok = None

    if request.method == "POST":
        action = request.form.get("action", "")
        if action not in ("on", "off"):
            message, ok = f'Unknown action "{action}".', False
        else:
            ok, output = rig_toggle(action)
            message = output or (
                f"CAT control turned {action}." if ok else "Request failed."
            )
        message = " ".join(message.split())[:300]
        return redirect(url_for("rig", msg=message, ok="1" if ok else "0"))

    values = dhinfo.load_dhinfo()
    status = service_status("dhrigctld.service")

    msg = request.args.get("msg")
    msg_ok = request.args.get("ok") == "1"

    return render_template(
        "rig.html",
        rignumber=values.get("rignumber", ""),
        rigdevice=values.get("rigdevice", ""),
        rigbaud=values.get("rigbaud", ""),
        status=status,
        message=msg,
        message_ok=msg_ok,
    )


@app.route("/fldigi", methods=["GET", "POST"])
def fldigi():
    # FLDigi is a GUI app with no headless mode; dhweb never starts or
    # stops it, only talks to an already-running local instance over its
    # own XML-RPC interface.
    message = None
    ok = None

    if request.method == "POST":
        action = request.form.get("action", "")
        if action == "set_modem":
            modem = request.form.get("modem", "")
            ok = fldigi_client.set_modem(modem)
            message = f'Modem set to "{modem}".' if ok else "Could not set modem."
        elif action == "set_frequency":
            freq = request.form.get("frequency", "")
            ok = fldigi_client.set_frequency(freq)
            message = f"Frequency set to {freq} Hz." if ok else "Could not set frequency."
        elif action in ("tx", "rx", "abort"):
            ok = getattr(fldigi_client, action)()
            message = f"Sent {action}." if ok else f"Could not send {action}."
        else:
            message, ok = f'Unknown action "{action}".', False
        message = " ".join(message.split())[:300]
        return redirect(url_for("fldigi", msg=message, ok="1" if ok else "0"))

    status = fldigi_client.get_status()
    modems = fldigi_client.list_modems() if status else []

    msg = request.args.get("msg")
    msg_ok = request.args.get("ok") == "1"

    return render_template(
        "fldigi.html",
        status=status,
        modems=modems,
        message=msg,
        message_ok=msg_ok,
    )


def main():
    from waitress import serve

    host = sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    serve(app, host=host, port=port)


if __name__ == "__main__":
    main()
