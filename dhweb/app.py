#!/usr/bin/env python3
"""
dhweb app.py
DigiHub web configuration interface (Flask, served by waitress).

Not run directly by hand; started via the scripts/dhweb wrapper.

Input:  [host] [port]  (both optional, default 0.0.0.0:8080)
Output: none - runs the DigiHub web UI until stopped
"""

import os
import re
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
# Same constraint as DHMODE_BIN above: must match install.sh's sudoers rule.
DHPAT_BIN = os.environ.get("DIGIHUB_DHPAT_BIN", "/usr/local/bin/dhpat")
PAT_PORT = 8015
# Same constraint as DHMODE_BIN above: must match install.sh's sudoers rule.
DHARDOP_BIN = os.environ.get("DIGIHUB_DHARDOP_BIN", "/usr/local/bin/dhardop")
ARDOP_WEBGUI_PORT = 8514
# Same constraint as DHMODE_BIN above: must match install.sh's sudoers rule.
DHWEBCHAT_BIN = os.environ.get("DIGIHUB_DHWEBCHAT_BIN", "/usr/local/bin/dhwebchat")
WEBCHAT_PORT = 8888
# Same constraint as DHMODE_BIN above: must match install.sh's sudoers rule.
DHCONSOLE_BIN = os.environ.get("DIGIHUB_DHCONSOLE_BIN", "/usr/local/bin/dhconsole")
CONSOLE_PORT = 7681
# dhupdate --check is read-only and needs no sudo; dhupdate --yes writes
# files under /usr/local and restarts services, so it needs the same
# NOPASSWD sudoers rule as DHMODE_BIN above -- must match install.sh's.
DHUPDATE_BIN = os.environ.get("DIGIHUB_DHUPDATE_BIN", "/usr/local/bin/dhupdate")
# man-db is an install.sh package dependency, so man(1) is always
# available; no mandoc/groff-html dependency needed just to show pages
# in the browser.
MAN_DIR = os.environ.get("DIGIHUB_MAN_DIR", "/usr/local/share/man/man1")
# Same constraint as DHMODE_BIN above: must match install.sh's sudoers
# rule. Unlike the toggles above, dhpower reboots/shuts down the whole
# host -- the Power page requires an explicit confirmation click before
# either action fires.
DHPOWER_BIN = os.environ.get("DIGIHUB_DHPOWER_BIN", "/usr/local/bin/dhpower")
# .dhinfo is owned by the operator account, the same one dhweb.service
# already runs as -- unlike DHMODE_BIN etc. above, no sudoers rule is
# needed here at all.
DHRESET_BIN = os.environ.get("DIGIHUB_DHRESET_BIN", "/usr/local/bin/dhreset")

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
    "standby", "tnc", "tnc300b", "tracker", "digipeater",
    "node", "winlinkrms", "wsjtx", "js8call", "qsstv",
]

# Modes backed by a VNC + noVNC remote desktop (see dh.lib's
# run_vnc_session()); the Mode page links out to noVNC for these.
VNC_MODES = {"wsjtx", "js8call", "qsstv"}
NOVNC_PORT = 6080

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


def pat_toggle(action):
    """Run dhpat via the NOPASSWD sudoers rule install.sh sets up.
    Returns (ok, output)."""
    try:
        result = subprocess.run(
            ["sudo", "-n", DHPAT_BIN, action],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as e:
        return False, str(e)
    output = (result.stdout + result.stderr).strip()
    return result.returncode == 0, output


def ardop_toggle(action):
    """Run dhardop via the NOPASSWD sudoers rule install.sh sets up.
    Returns (ok, output)."""
    try:
        result = subprocess.run(
            ["sudo", "-n", DHARDOP_BIN, action],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as e:
        return False, str(e)
    output = (result.stdout + result.stderr).strip()
    return result.returncode == 0, output


def webchat_toggle(action):
    """Run dhwebchat via the NOPASSWD sudoers rule install.sh sets up.
    Returns (ok, output)."""
    try:
        result = subprocess.run(
            ["sudo", "-n", DHWEBCHAT_BIN, action],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as e:
        return False, str(e)
    output = (result.stdout + result.stderr).strip()
    return result.returncode == 0, output


def console_toggle(action):
    """Run dhconsole via the NOPASSWD sudoers rule install.sh sets up.
    Returns (ok, output)."""
    try:
        result = subprocess.run(
            ["sudo", "-n", DHCONSOLE_BIN, action],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as e:
        return False, str(e)
    output = (result.stdout + result.stderr).strip()
    return result.returncode == 0, output


def check_update():
    """Run dhupdate --check (read-only, no sudo needed -- see man
    dhupdate). Returns (code, output): 0 = up to date, 3 = changes
    available, anything else = a prerequisite failed (git/network/
    manifest)."""
    try:
        result = subprocess.run(
            [DHUPDATE_BIN, "--check"],
            capture_output=True, text=True, timeout=60,
        )
    except (OSError, subprocess.SubprocessError) as e:
        return 1, str(e)
    return result.returncode, (result.stdout + result.stderr).strip()


def apply_update():
    """Run dhupdate --yes via the NOPASSWD sudoers rule install.sh sets
    up. Returns (ok, output). Generous timeout: a real update clones the
    repo, installs files, restarts services, and -- if dhupdate updated
    itself -- re-runs the whole cycle once more before returning."""
    try:
        result = subprocess.run(
            ["sudo", "-n", DHUPDATE_BIN, "--yes"],
            capture_output=True, text=True, timeout=180,
        )
    except (OSError, subprocess.SubprocessError) as e:
        return False, str(e)
    output = (result.stdout + result.stderr).strip()
    return result.returncode == 0, output


_OVERSTRIKE = re.compile(r".\x08")


def list_man_pages():
    """Return sorted installed DigiHub man page names (without the .1
    suffix); also doubles as the whitelist render_man_page() checks
    against before shelling out to man(1)."""
    try:
        names = [f[:-2] for f in os.listdir(MAN_DIR) if f.endswith(".1")]
    except OSError:
        return []
    return sorted(names)


def render_man_page(name):
    """Render an installed man page as plain text via man(1) (already an
    install.sh dependency), with the backspace-overstrike sequences
    groff's ASCII/UTF-8 output uses for bold/underline stripped out.
    Returns None if name isn't a real installed page (path-traversal /
    argument-injection guard -- man(1) never sees anything but a name
    already confirmed to exist) or rendering otherwise fails."""
    if name not in list_man_pages():
        return None
    try:
        result = subprocess.run(
            ["man", name],
            capture_output=True, text=True, timeout=10,
            env={**os.environ, "MANWIDTH": "80"},
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0 or not result.stdout:
        return None
    return _OVERSTRIKE.sub("", result.stdout)


def power_action(action):
    """Run dhpower via the NOPASSWD sudoers rule install.sh sets up.
    Returns (ok, output). systemctl reboot/poweroff return almost
    immediately (they queue the shutdown, they don't wait for it), so
    the subprocess call normally completes and this response reaches
    the browser before the host actually goes down -- a timeout here
    is treated as an expected side effect of that race, not a failure."""
    try:
        result = subprocess.run(
            ["sudo", "-n", DHPOWER_BIN, action],
            capture_output=True, text=True, timeout=10,
        )
    except subprocess.TimeoutExpired:
        return True, "Command issued; the host is going down now."
    except (OSError, subprocess.SubprocessError) as e:
        return False, str(e)
    output = (result.stdout + result.stderr).strip()
    return result.returncode == 0, output


def reset_config():
    """Run dhreset --yes. Returns (ok, output). No sudo -- .dhinfo is
    owned by the same operator account dhweb.service already runs as."""
    try:
        result = subprocess.run(
            [DHRESET_BIN, "--yes"],
            capture_output=True, text=True, timeout=10,
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

    novnc_url = None
    if current in VNC_MODES:
        mode_host = request.host.split(":")[0]
        novnc_url = f"http://{mode_host}:{NOVNC_PORT}/vnc.html?host={mode_host}&port={NOVNC_PORT}"

    return render_template(
        "mode.html",
        current=current,
        default_modes=DEFAULT_MODES,
        services=services,
        statuses=statuses,
        log_tail=log_tail,
        log_service=services[0] if services else None,
        novnc_url=novnc_url,
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


@app.route("/pat", methods=["GET", "POST"])
def pat():
    # Pat has its own web UI; dhweb shows status and a toggle, and links
    # out to it rather than reimplementing it.
    message = None
    ok = None

    if request.method == "POST":
        action = request.form.get("action", "")
        if action not in ("on", "off"):
            message, ok = f'Unknown action "{action}".', False
        else:
            ok, output = pat_toggle(action)
            message = output or (
                f"Winlink client turned {action}." if ok else "Request failed."
            )
        message = " ".join(message.split())[:300]
        return redirect(url_for("pat", msg=message, ok="1" if ok else "0"))

    values = dhinfo.load_dhinfo()
    status = service_status("dhpat.service")
    pat_host = request.host.split(":")[0]

    msg = request.args.get("msg")
    msg_ok = request.args.get("ok") == "1"

    return render_template(
        "pat.html",
        mycall=values.get("callsign", ""),
        locator=values.get("grid", ""),
        has_password=bool(values.get("winlinkpass", "").strip()),
        status=status,
        pat_url=f"http://{pat_host}:{PAT_PORT}",
        message=msg,
        message_ok=msg_ok,
    )


@app.route("/ardop", methods=["GET", "POST"])
def ardop():
    # ardopcf has its own web GUI for level adjustment; dhweb shows
    # status and a toggle, and links out to it rather than reimplementing.
    message = None
    ok = None

    if request.method == "POST":
        action = request.form.get("action", "")
        if action not in ("on", "off"):
            message, ok = f'Unknown action "{action}".', False
        else:
            ok, output = ardop_toggle(action)
            message = output or (
                f"ARDOP TNC turned {action}." if ok else "Request failed."
            )
        message = " ".join(message.split())[:300]
        return redirect(url_for("ardop", msg=message, ok="1" if ok else "0"))

    values = dhinfo.load_dhinfo()
    status = service_status("dhardop.service")
    ardop_host = request.host.split(":")[0]
    ptt_via_rigctld = bool(
        values.get("rignumber", "").strip() and values.get("rigdevice", "").strip()
    )

    msg = request.args.get("msg")
    msg_ok = request.args.get("ok") == "1"

    return render_template(
        "ardop.html",
        status=status,
        ptt_via_rigctld=ptt_via_rigctld,
        ardop_webgui_url=f"http://{ardop_host}:{ARDOP_WEBGUI_PORT}",
        message=msg,
        message_ok=msg_ok,
    )


@app.route("/webchat", methods=["GET", "POST"])
def webchat():
    # aprsd-webchat-extension has its own web UI; dhweb shows status and
    # a toggle, and links out to it rather than reimplementing it. Unlike
    # rig/pat/ardop, it isn't tied to a .dhinfo config subset of its own
    # -- webchatconf.py just reads callsign/lat/lon, already shown on the
    # Configuration page.
    message = None
    ok = None

    if request.method == "POST":
        action = request.form.get("action", "")
        if action not in ("on", "off"):
            message, ok = f'Unknown action "{action}".', False
        else:
            ok, output = webchat_toggle(action)
            message = output or (
                f"APRS WebChat turned {action}." if ok else "Request failed."
            )
        message = " ".join(message.split())[:300]
        return redirect(url_for("webchat", msg=message, ok="1" if ok else "0"))

    status = service_status("dhwebchat.service")
    webchat_host = request.host.split(":")[0]
    direwolf_active = service_status("dhdirewolf.service") == "active"

    msg = request.args.get("msg")
    msg_ok = request.args.get("ok") == "1"

    return render_template(
        "webchat.html",
        status=status,
        direwolf_active=direwolf_active,
        webchat_url=f"http://{webchat_host}:{WEBCHAT_PORT}",
        message=msg,
        message_ok=msg_ok,
    )


@app.route("/console", methods=["GET", "POST"])
def console():
    # ttyd has its own browser-based terminal, authenticated by login(1)
    # against the operator's real system password; dhweb shows status
    # and a toggle and links out to it rather than reimplementing a
    # terminal -- and never sees or handles that password itself.
    message = None
    ok = None

    if request.method == "POST":
        action = request.form.get("action", "")
        if action not in ("on", "off"):
            message, ok = f'Unknown action "{action}".', False
        else:
            ok, output = console_toggle(action)
            message = output or (
                f"Web console turned {action}." if ok else "Request failed."
            )
        message = " ".join(message.split())[:300]
        return redirect(url_for("console", msg=message, ok="1" if ok else "0"))

    status = service_status("dhconsole.service")
    console_host = request.host.split(":")[0]

    msg = request.args.get("msg")
    msg_ok = request.args.get("ok") == "1"

    return render_template(
        "console.html",
        status=status,
        console_url=f"http://{console_host}:{CONSOLE_PORT}",
        message=msg,
        message_ok=msg_ok,
    )


@app.route("/update", methods=["GET", "POST"])
def update():
    # dhupdate's own output can be a multi-line file list (Added/
    # Changed/Removed, restart messages), unlike the short one-line
    # results everything else on this page redirects with in the URL --
    # so the apply result is rendered inline instead of round-tripped
    # through a query string, and the page just re-checks fresh after a
    # POST rather than redirecting.
    apply_ok = None
    apply_output = None

    if request.method == "POST":
        apply_ok, apply_output = apply_update()

    code, check_output = check_update()

    return render_template(
        "update.html",
        up_to_date=code == 0,
        check_failed=code not in (0, 3),
        check_output=check_output,
        apply_ok=apply_ok,
        apply_output=apply_output,
    )


GUI_APPS = [
    ("wsjtx", "WSJT-X", "wsjtx"),
    ("js8call", "JS8Call", "js8call"),
    ("qsstv", "qSSTV", "qsstv"),
]


def package_installed(pkg):
    try:
        result = subprocess.run(
            ["dpkg", "-s", pkg],
            capture_output=True, text=True, timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return result.returncode == 0


@app.route("/guiapps")
def guiapps():
    # WSJT-X, JS8Call, and qSSTV are GUI-only applications with no
    # headless mode and no remote-control protocol DigiHub uses (unlike
    # FLDigi's XML-RPC) -- dhweb only reports whether each is installed;
    # you run them yourself from the local console (a monitor and
    # keyboard, or your own remote desktop session), same as FLDigi.
    apps = [
        {"pkg": pkg, "label": label, "binary": binary, "installed": package_installed(pkg)}
        for pkg, label, binary in GUI_APPS
    ]
    return render_template("guiapps.html", apps=apps)


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


@app.route("/docs")
def docs():
    pages = list_man_pages()
    name = request.args.get("page", "")
    text = render_man_page(name) if name else None
    return render_template("docs.html", pages=pages, name=name, text=text)


@app.route("/power", methods=["GET", "POST"])
def power():
    # Reboot/shutdown fire on the same request that renders the result
    # (no redirect) -- once dhpower runs, this host may not be around
    # long enough for a second round-trip to reliably land. Reset
    # doesn't have that problem, but stays on the same no-redirect
    # pattern for consistency with its neighbors on this page.
    message = None
    ok = None

    if request.method == "POST":
        action = request.form.get("action", "")
        if action not in ("reboot", "shutdown", "reset"):
            message, ok = f'Unknown action "{action}".', False
        elif action == "reset":
            ok, output = reset_config()
            message = output or ("Configuration reset." if ok else "Reset failed.")
        else:
            ok, output = power_action(action)
            if ok:
                message = (
                    "Rebooting now -- this page will be unreachable for a minute or two."
                    if action == "reboot" else
                    "Shutting down now -- power the device back on manually to reach it again."
                )
            else:
                message = output or "Request failed."

    return render_template("power.html", message=message, message_ok=ok)


def main():
    from waitress import serve

    host = sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    serve(app, host=host, port=port)


if __name__ == "__main__":
    main()
