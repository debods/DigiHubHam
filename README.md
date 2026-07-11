DigiHub - Digital Hub for ham radio 
===================================

by

W0FFS@PLOTLOST.COM
------------------

Overview
--------
DigiHub is not an application or environment; it is a curated collection of ham radio utilities and applications geared toward Digital ham radio Operations.

It was conceived as an alternative to the popular DigiPi, which is an excellent implementation and is a highly recommended option for those setting out on the digital ham path.

DigiHub builds on the DigiPi concept and is designed to be installed on an existing Debian system rather than being a complete Operating System image. Also, it is re-configurable.

The installation script has been built and tested on Debian trixie 64-bit, which includes WSL (see below) and Raspberry Pi OS running on a Pi Zero 2W, 3, 4, or 5.

The primary design goal of DigiHub is flexibility and configurability:

Digihub
|:---------------------------------------------------------------------------------------------------|
Validates (US) callsigns.
Has an editable configuration, from the terminal or a web browser.
Automatically calculates the Maidenhead grid square from the Latitude and Longitude when using a GPS device.
Automatically generates the correct APRS password.
Automatically generates a random alphanumeric AX node password.
Automatically configures and populates a local FCC amateur callsign database (hamdb).
Can be installed for an individual or club callsign.
Can be installed on an existing Debian trixie x64 Operating System.
It is entirely free.

Command Line Utilities
---------------------
A number of the methods used to install, run, and maintain DigiHub are included as command-line utilities:

| Command     | Purpose                                                     | Written in  |
|:------------|:------------------------------------------------------------|:------------|
| aprspass    | Generate an APRS password                                   | bash/python |
| axnodepass  | Generate a random alphanumeric AX Node password             | bash        |
| dhardop     | Turn DigiHub's ARDOP TNC (ardopcf) on or off                 | bash        |
| dhaudiohat  | Activate the Raspberry Pi device-tree overlay for DigiHub's audio HAT | bash/python |
| dhardopd    | Runs ardopcf for DigiHub's ARDOP TNC                         | bash        |
| dhdirewolf  | Runs Direwolf for DigiHub's TNC/digipeater/tracker/node modes | bash        |
| dhedit      | DigiHub configuration editor                                | bash        |
| dhgpsmonitor| Background service that updates .dhinfo when GPS position moves | bash/python |
| dhjs8calld  | Runs JS8Call on a VNC + noVNC remote desktop for DigiHub's js8call mode | bash        |
| dhmode      | Switch DigiHub's active digital mode                        | bash        |
| dhnoded     | Runs kissattach + ax25d + uronode for DigiHub's AX.25 node/BBS mode | bash        |
| dhqsstvd    | Runs qSSTV on a VNC + noVNC remote desktop for DigiHub's qsstv mode | bash        |
| dhremove    | DigiHub uninstaller                                         | bash        |
| dhpat       | Turn DigiHub's Winlink client (Pat) on or off                | bash        |
| dhpatd      | Runs Pat's web interface for DigiHub's Winlink client        | bash        |
| dhrig       | Turn DigiHub's CAT control (rigctld) on or off               | bash        |
| dhrigctld   | Runs hamlib's rigctld for DigiHub CAT control                | bash        |
| dhupdate    | Sync installed DigiHub scripts against the GitHub repository | bash        |
| dhweb       | DigiHub web configuration interface                         | python (Flask) |
| dhwebchat   | Turn DigiHub's APRS WebChat (aprsd) on or off                | bash        |
| dhwebchatd  | Runs aprsd's webchat command for DigiHub's APRS WebChat      | bash        |
| dhwsjtxd    | Runs WSJT-X on a VNC + noVNC remote desktop for DigiHub's wsjtx mode | bash        |
| hamdb       | FCC Amateur Radio license database                          | bash        |
| maidenhead  | Calculate a Maidenhead ham grid from latitude and longitude | bash/python |
| position    | Get current GPS position from GPS device                    | bash/python |
| qrz         | Check a US callsign using hamdb, hamdb.org & mapbox API     | bash        |
| sysinfo     | System information                                          | bash        |
| whohami     | Show user information held for current configuration        | bash        |

**Note:** * hamdb is installed using MariaDB rather than MySQL. Starting with MariaDB 10.5, the mysqlimport command was replaced with mariadb-import; the version in this repository has been modified to reflect that change, but is otherwise identical.*

Every command above has a full man page (usage, arguments, files, exit codes) installed with DigiHub, e.g. `man qrz`. Sources live under [`man/`](man/) in this repository and are kept in sync by `dhupdate` the same way scripts are.

Prerequisites
-------------
DigiHub installation requires that the user installing it has sudo privileges.

GPS Devices
-----------
DigiHub will detect and use correctly installed and working GPS devices (port and baud rate) in the following order:

Stable Names
	/dev/serial/by-id/*

USB devices
	/dev/ttyACM*
	/dev/ttyUSB*

Native UARTs
	/dev/ttyAMA*
	/dev/ttyS0-3

For a Raspberry Pi installation, this usually requires enabling the SPI and Serial Port interfaces via raspi-config. The manufacturer's instructions for the GPS device should be followed to ensure it is working prior to DigiHub installation.

DigiHub installs minicom and a Python script gpstest.py, to assist with troubleshooting after installation.

A recommended GPS device is a Waveshare LC29H Multi-GNSS HAT (available [here](https://www.waveshare.com/lc29h-gps-hat.htm)). It works with any PC hardware via USB and with Raspberry Pi via the GPIO header.

Custom Installation
-------------------

hamdb.org is reliable for the United States (US), Canada (CA), and Australia (AU), but for the Czech Republic (CZ) and Germany (DE), the database is updated daily; for the rest of the world, it is updated monthly. For other countries, there is no reliable resource.

For non-US/AU/CA/CZ and custom installations, entering 'nodb' as the callsign when installing DigiHub (e.g., ./install.sh nodb) will allow manual entry of the unvalidated callsign and other required/optional details.

Installation
-------------

Issue the following commands:

If necessary, install git:
```bash
sudo apt update && sudo apt install git
```
Change directory to the install folder, make the installer executable, and run it:

```bash
git clone https://github.com/debods/DigiHubHam.git
```
```bash
cd DigiHubHam
```
```bash
chmod +x install.sh
```
```bash
./install.sh 
```
DigiHub can also be installed using: ./install.sh followed by the callsign you wish to use. 

If the DigiHub installation fails, the system will revert to its original state, meaning all installed packages and scripts will be removed, and any environmental changes will be undone.  The only exception is that OS upgrades will not be reverted.

All software installed by DigiHub is open-source licensed and freely available.

Windows Subsystem for Linux (WSL)
---------------------------------
All scripts are tested and working in WSL.  However, in order to leverage a USB-attached GPS device, usbipd needs to be installed and configured. One exception: `node` mode (the AX.25 packet node/BBS, see below) needs a kernel built with `CONFIG_AX25`, which WSL2's default kernel doesn't have — it fails with a clear error on WSL2 rather than silently not working. Everything else in DigiHub is unaffected.

Post installation
-----------------
All of DigiHub's scripts are located in /usr/local/bin.

Many of the bash scripts are simply wrappers for the associated Python scripts.  The Python scripts can be run independently after activating the installed Virtual Environment (venv) using the following command:

```bash
source "$DigiHubvenv/bin/activate"
```

To exit the Python Virtual Environment, run:

```bash
deactivate
```

Editing Your Configuration
---------------------------
`dhedit` opens an interactive editor over `$HOME/.dhinfo`:

```bash
dhedit
```

- Edit any field directly (callsign, license, name, address, the Mapbox token, the AX Node password, the Winlink password, the default mode, or the radio interface / rig control fields), or regenerate the AX Node password fresh. The APRS password is derived from the callsign (APRS-IS passcode algorithm) and isn't independently editable — it's regenerated automatically whenever the callsign changes.
- Changing the callsign, or choosing "Refresh from hamdb.org", offers to pull license/name/address details straight from hamdb.org.
- Changing latitude or longitude automatically revalidates and recalculates the Maidenhead grid.
- Add or remove a GPS device: adding re-runs the same auto-detection `install.sh` uses (with a manual entry fallback), updates `.profile`, and installs/enables the `dhgpsmonitor` service; removing resets `.profile` and fully tears the service down.

Nothing is written to `.dhinfo` until you choose "Save and exit"; GPS device changes take effect immediately since they touch `.profile` and systemd, not `.dhinfo`.

Web Configuration Interface
-----------------------------
`dhweb` serves the same configuration, as a web page, for anyone who'd rather use a phone, tablet, or browser than a terminal. It's installed and enabled automatically by `install.sh` as a systemd service, so it's already running after installation:

```
http://<digihub-host>:8080/config
```

It validates and saves fields the same way `dhedit` does (reusing the same installed validator/computation scripts), and backs up `.dhinfo` to `.dhinfo.last` before every save. Its Mode page (`/mode`) shows the active digital mode, the status of the service(s) behind it, a recent log tail, and lets you switch modes — see "Digital Modes" below.

**`dhweb` has no authentication and is meant only for a trusted local network** — the same Wi-Fi or hotspot the DigiHub device itself is on. Do not expose it to the open internet (e.g. via port forwarding). If you don't want it running at all, disable it with:

```bash
sudo systemctl disable --now dhweb
```

Digital Modes (Direwolf / AX.25)
-----------------------------------
DigiHub can only run one digital mode at a time, since most of them share the same sound card or serial port. `dhmode` switches between them: it stops whatever's currently active and starts the one you pick.

```bash
dhmode digipeater
```

Currently implemented, all backed by [Direwolf](https://github.com/wb2osz/direwolf):

| Mode         | What it does                                                    |
|:-------------|:------------------------------------------------------------------|
| standby      | Nothing running (the default)                                     |
| tnc          | Plain KISS/AGW TNC (1200 baud) for other apps to use               |
| tnc300b      | Same, at 300 baud, for HF SSB packet                               |
| tracker      | TNC plus an APRS position beacon using the coordinates in `.dhinfo`|
| digipeater   | TNC plus beaconing plus wide-area APRS digipeating                 |
| node         | AX.25 packet node/BBS ([uronode](#ax25-nodebbs-uronode)) on top of a KISS TNC |

Also implemented, backed by a [TigerVNC](https://tigervnc.org/) + [noVNC](https://novnc.com/) remote desktop instead of Direwolf — **opt-in at install time**, not installed by default (see [VNC Remote Desktop](#vnc-remote-desktop-wsjt-x-js8call-qsstv) below):

| Mode    | What it does                                          |
|:--------|:-------------------------------------------------------|
| wsjtx   | Runs [WSJT-X](https://wsjt.sourceforge.io/) (FT8/FT4/weak-signal modes) on a browser-accessible VNC desktop |
| js8call | Runs [JS8Call](http://js8call.com/) (JS8 keyboard-to-keyboard messaging) the same way |
| qsstv   | Runs [qSSTV](http://users.telenet.be/on4qz/) (slow-scan TV) the same way |

`winlinkrms` (a future Winlink RMS Gateway mode) is DigiHub's one remaining unimplemented mode; selecting it records the choice in `.dhinfo` without starting anything, for a later phase of DigiHub's development to add.

APRS WebChat and FLDigi are *not* among `dhmode`'s modes, even though DigiPi treats them as its own boot-mode options — see [APRS WebChat](#aprs-webchat-aprsd) and [FLDigi](#fldigi) below for why.

For the Direwolf-backed modes, `dhmode` regenerates `/etc/digihub/direwolf.conf` from `.dhinfo`'s callsign, coordinates, `radiointerface`, and `rigdevice` fields before (re)starting the `dhdirewolf` service. Audio device selection is best-effort (it looks for a single plausible non-built-in USB audio device); PTT method follows `radiointerface` — CM108-style USB adapters (including AIOC and most inexpensive USB radio interfaces) use Dire Wolf's automatic GPIO detection, DigiRig Mobile uses serial RTS on `rigdevice`, and Raspberry Pi audio HATs use a GPIO pin number you supply in `rigdevice`. If auto-detection can't confidently pick an audio device, or the PTT method can't be determined, a warning is logged and you can fix `/etc/digihub/direwolf.conf` by hand (it'll be regenerated the next time you switch modes) or correct the underlying `.dhinfo` field with `dhedit`/`dhweb`.

You can also switch modes from `dhweb`'s Mode page. That requires `dhweb` (which runs as an unprivileged, unattended systemd service) to invoke `dhmode` as root without a password prompt; `install.sh` sets this up with a narrowly scoped sudoers rule (`/etc/sudoers.d/digihub-dhmode`) that permits *only* `/usr/local/bin/dhmode`, and `dhmode` itself still validates the mode name against a fixed list before doing anything privileged.

AX.25 Node/BBS (uronode)
----------------------------
`node` mode is DigiHub's packet radio node/BBS: [uronode](https://sourceforge.net/projects/uronode/), listening on top of a real kernel AX.25 network interface, so anyone connecting over the air with a TNC (or another AX.25 station) gets a node prompt they can use to look around, send/read mail, or connect onward to other stations.

```bash
dhmode node
```

Unlike the other Direwolf-backed modes, `node` needs more than Direwolf itself: `dhmode` starts both `dhdirewolf.service` (Direwolf, launched with `-p` so it exposes a local KISS pseudo-terminal at `/tmp/kisstnc` instead of just a network TNC port) and `dhnode.service` (`dhnoded`, a new wrapper that runs `kissattach` to bridge that pty into the kernel AX.25 stack, tunes it with `kissparms`, and then runs `ax25d`, which spawns a `uronode` session for each incoming connection). The AX.25 port/node configuration (`/etc/ax25/axports`, `/etc/ax25/ax25d.conf`, `/etc/ax25/uronode.perms`, and the `HostName`/`NodeId`/`FlexID` lines of `/etc/ax25/uronode.conf`) is generated from `.dhinfo`'s `callsign` and `axnodepass` fields by `nodeconf.py` — everything else in `uronode.conf` and the rest of the package's shipped files (help text, MOTD, etc.) is left exactly as `uronode` installed it. `axnodepass` (see the `axnodepass` command above) becomes the password required to log in to the node at all; if it's not set, the node allows anyone in.

This is the one part of DigiHub that needs real kernel support, not just a userspace daemon: creating an AX.25 network interface requires a kernel built with `CONFIG_AX25`, which not every platform has — most notably, **WSL2's default kernel does not**. `dhnoded` checks for it (`modprobe ax25`, then `/proc/net/ax25`) before doing anything else and fails with a clear message if it's missing, rather than let `kissattach` silently do nothing. If you're on WSL2 and need this mode, you'll need a custom WSL2 kernel built with AX.25 support; everything else in DigiHub works fine without it.

Also unlike every other DigiHub service, `dhnode.service` runs as `root` rather than the installing user — creating a kernel network interface needs it, and `ax25d`'s own per-connection user-switching (its config's `uid` column) is designed around a root-started daemon, the same way it's run in every traditional AX.25 node setup.

CAT Control (rigctld)
-------------------------
Separately from digital modes, `dhrig` turns network CAT control on or off — hamlib's `rigctld`, giving other applications (WSJT-X, FLDigi, Winlink clients, etc.) frequency/mode/PTT control of the radio over the network instead of each needing its own serial connection. It's independent of `dhmode`: it can run alongside whichever digital mode is active (or none), as long as they're not fighting over the same physical port.

```bash
dhrig on
```

CAT control needs `rignumber` (a [hamlib rig model number](https://hamlib.sourceforge.net/html/rigctld.1.html), found with `rigctl -l`) and `rigdevice` set first, via `dhedit` or `dhweb`'s Configuration page — `dhrig on` will tell you if they're missing. It's off by default, same as the Direwolf-backed modes, and only starts (installing its systemd unit on first use) once you turn it on. `dhrig status` reports whether it's currently running, and `dhweb`'s Rig Control page offers the same on/off toggle over the same sudoers rule used for mode switching.

Winlink (Pat)
----------------
[Pat](https://github.com/la5nta/pat) is DigiHub's Winlink client. It isn't packaged for Debian, so `install.sh` fetches the right `.deb` for your architecture (amd64/arm64/armhf/i386) straight from Pat's own GitHub releases and verifies it against the sha256 checksum GitHub reports for that file before installing — best-effort, like hamdb: if that fails (no network, GitHub unreachable), installation continues with a warning, and you can install Pat manually later.

Unlike FLDigi, Pat has no GUI dependency and runs perfectly well headless, so — like Direwolf and rigctld — DigiHub manages it as a systemd service, off by default:

```bash
dhpat on
```

`dhpat on` regenerates `$HOME/.config/pat/config.json`'s `mycall`, `secure_login_password`, and `locator` fields from `.dhinfo` (a Winlink password is recommended but not required — Pat still runs without one, just without secure CMS login), sets a default `http_addr` of `0.0.0.0:8015` the first time the file is created (deliberately not Pat's own `:8080` default, which would collide with `dhweb`), and otherwise leaves the file alone — anything you add by hand later (`connect_aliases` for AX.25/ARDOP/telnet, `hamlib_rigs`, a `schedule`, etc.) survives every future `dhpat on`. `dhpat status` reports whether it's running, and `dhweb`'s Winlink page offers the same on/off toggle plus a link to Pat's own web interface at `http://<digihub-host>:8015` — DigiHub doesn't reimplement Pat's UI, just links to it.

ARDOP
--------
[ardopcf](https://github.com/pflarue/ardop) — the actively-maintained fork Pat's own documentation recommends over the original `piardopc` — is DigiHub's ARDOP TNC, most commonly used for Winlink-over-ARDOP with Pat. It has no Debian package, so `install.sh` downloads the prebuilt binary matching your architecture (amd64/arm64/armhf) straight from GitHub releases — best-effort, like Pat/hamdb. Unlike Pat, upstream doesn't publish checksums for these binaries, so this step relies on GitHub's own HTTPS distribution rather than a separate integrity check.

Also unlike Pat, `ardopcf` has no GUI dependency and *can* run headless, but upstream itself notes it "is not currently well suited" to running unattended from boot — so DigiHub follows the same pattern as Direwolf and rigctld: off by default, toggled on when you actually need it:

```bash
dhardop on
```

`dhardop on` also regenerates Pat's `config.json` (the same generator `dhpat` uses), setting `ardop.addr` to `localhost:8515` so Pat can find it. If `rignumber`/`rigdevice` are set, it goes further and wires Pat to control ARDOP's PTT through `dhrigctld` (`hamlib_rigs`/`ptt_ctrl`/`rig` in Pat's config) instead of giving `ardopcf` its own serial port options — this is `ardopcf`'s own upstream-recommended approach, since it avoids two programs fighting over the same port. If those fields aren't set, nothing is wired up automatically; you're on your own for PTT (VOX, or editing `dhardop.service`'s `ExecStart` to add `ardopcf`'s own `-p`/`-c` flags).

The audio device is auto-detected the same best-effort way as Direwolf's (shared logic, `audiodetect.py`) — but unlike Direwolf, `ardopcf` doesn't fall back gracefully if none is found confidently; it tries an ALSA alias literally named `ARDOP` and crashes if that alias doesn't exist. So `dhardop`/`dhardopd` refuse to start at all in that case, with a clear message, rather than crash-looping. `dhardop status` reports whether it's running, and `dhweb`'s ARDOP page offers the same on/off toggle, shows whether PTT is wired via rigctld, and links to `ardopcf`'s own web GUI at `http://<digihub-host>:8514` for adjusting audio levels — again, DigiHub links to it rather than reimplementing it.

APRS WebChat (aprsd)
------------------------
[aprsd](https://github.com/craigerl/aprsd) plus the [aprsd-webchat-extension](https://github.com/hemna/aprsd-webchat-extension) give DigiHub browser-based APRS text messaging — DigiPi's own "APRS WebChat" feature, built on the same underlying project. `install.sh` pip-installs both into the shared DigiHub venv alongside Flask/waitress.

Unlike CAT control, Winlink, and ARDOP above, WebChat doesn't need exclusive access to any radio hardware: it's just another TCP client of Direwolf's KISS-over-TCP interface (`localhost:8001`, Direwolf's default), which every Direwolf-backed mode (`tnc`/`tnc300b`/`tracker`/`digipeater`/`node`) already exposes. That's why it's an independent toggle (`dhwebchat`) like `dhrig`/`dhpat`/`dhardop`, rather than one of `dhmode`'s mutually-exclusive modes — even though DigiPi itself treats WebChat as one of its boot-mode options. It can run alongside whichever Direwolf-backed mode (or none) is active; without one, WebChat's browser UI still works for composing/reading, but nothing moves over RF until you pick a mode with `dhmode`.

```bash
dhwebchat on
```

`dhwebchat on` regenerates `$HOME/.config/aprsd/aprsd.conf` from `.dhinfo`'s callsign/latitude/longitude via `webchatconf.py`, configured for RF-only operation (`aprs_network` disabled — no APRS-IS/internet connection needed) with `kiss_tcp` pointed at Direwolf's port. `dhwebchat status` reports whether it's running, and `dhweb`'s WebChat page offers the same on/off toggle, shows whether a Direwolf-backed mode is currently active, and links to aprsd-webchat-extension's own browser UI at `http://<digihub-host>:8888` — DigiHub links to it rather than reimplementing it.

FLDigi
--------
FLDigi is installed, but — unlike Direwolf and rigctld — DigiHub doesn't manage it as a background service, because it's a GUI application with no headless mode. You start it yourself, locally on the machine (a monitor and keyboard, or your own remote desktop session):

```bash
fldigi
```

Once it's running (its XML-RPC control interface is on by default, at `127.0.0.1:7362`), `dhweb`'s FLDigi page can see it: current version, TX/RX status, modem, and frequency, plus controls to change the modem, set the frequency, and trigger TX/RX/abort. If FLDigi isn't running, the page just says so — DigiHub never starts, stops, or otherwise manages the process itself. Full waterfall tuning still means sitting at the actual screen; this page is remote *control*, not a remote *view*. Unlike WSJT-X/JS8Call/qSSTV below, FLDigi doesn't need exclusive audio-device access the way they do, and its XML-RPC interface is more capable than a VNC view would be for it specifically — so it stays this way rather than getting VNC-streamed too.

VNC Remote Desktop (WSJT-X, JS8Call, qSSTV)
------------------------------------------------
[WSJT-X](https://wsjt.sourceforge.io/), [JS8Call](http://js8call.com/), and [qSSTV](http://users.telenet.be/on4qz/) round out DigiHub's digital modes — FT8/FT4/other weak-signal modes, JS8's keyboard-to-keyboard messaging, and slow-scan TV. Unlike FLDigi, they need *exclusive* access to the same sound card Direwolf/ardopcf use — so, matching DigiPi's own `wsjtx.service`/`js8call.service`/`sstv.service` (confirmed via [DigiPi's source](https://github.com/craigerl/digipi)), they're real `dhmode` modes, each backed by a [TigerVNC](https://tigervnc.org/) desktop bridged into the browser with [noVNC](https://novnc.com/).

This is the heaviest, most niche-interest slice of DigiHub — three sizeable Qt apps plus a full VNC/noVNC/window-manager stack — so unlike everything else covered above, it's **not installed by default**. `install.sh` asks about it explicitly (right after the Mapbox prompt) and skips it unless you say yes; run `install.sh` again later if you decide you want it after all, or decline it later if you don't. Nothing about not installing it requires an existing desktop environment either way: TigerVNC's `Xtigervnc` is a self-contained virtual X server (it doesn't attach to or need any pre-existing X session), and the window manager it uses ([Fluxbox](http://fluxbox.org/)) is a standalone lightweight WM, not tied to GNOME/KDE — this is the same headless-VNC pattern DigiPi itself relies on running on Raspberry Pi OS Lite.

```bash
dhmode wsjtx
```

Selecting one of these modes stops whatever else is running (same as any other `dhmode` switch) and starts a VNC desktop (`:1`, port 5901) running Fluxbox, with [noVNC](https://novnc.com/)'s bundled `novnc_proxy` bridging it to a browser-usable URL on port 6080 — `dhweb`'s Mode page links to it directly. The VNC password comes from `.dhinfo`'s `vncpass` field (auto-generated at install time regardless of whether you opted into VNC, editable via `dhedit`/`dhweb` like `axnodepass`); if you opted in, `install.sh` writes it into `~/.config/tigervnc/passwd` via `vncpasswd -f`, and you'll be asked for it when you open the remote desktop link.

If you selected one of these modes without opting into VNC support at install time, `dhwsjtxd`/`dhjs8calld`/`dhqsstvd` fail with a clear message (`systemctl status`/`journalctl -u dhwsjtx`) telling you which packages to install rather than silently doing nothing.

If you only need FT8 occasionally, running WSJT-X locally on the console (same as the FLDigi pattern) works too and needs none of this; the VNC modes exist for headless/remote setups where that isn't practical.

`dhweb`'s GUI Apps page just reports whether each is installed (`dpkg -s`, no root needed) — it doesn't start, stop, or otherwise talk to any of them.

Raspberry Pi Audio HATs
--------------------------
Setting `radiointerface` to `fepi`, `aiz`, or `drapizero` (Fe-Pi Audio, Audio Injector Zero, or a DRAWS-style N7NIX board) already picks the right PTT method for Direwolf — see [Digital Modes](#digital-modes-direwolf--ax25) above. But those boards also need a Raspberry Pi kernel device-tree overlay to make their audio hardware work at all, which `dhaudiohat` handles separately:

```bash
sudo dhaudiohat
```

`dhaudiohat` reads `radiointerface` from `.dhinfo` and patches the matching `dtoverlay=` line into `/boot/firmware/config.txt` (or `/boot/config.txt`) — confirmed against [DigiPi's own boot script](https://github.com/craigerl/digipi/blob/master/home/pi/localize.sh): `aiz` and `drapizero` both use `dtoverlay=audioinjector-wm8731-audio`, `fepi` is the baseline `dtoverlay=fe-pi-audio`, and `digipihat` needs no overlay change at all. Every other `radiointerface` value (USB/external devices) is a no-op too. A reboot is required afterward for the change to take effect — `dhedit` and `dhweb`'s Configuration page both remind you to run it when you set one of the three HAT values. This only applies on a genuine Raspberry Pi; on any other Debian system (which is most of what DigiHub targets) it fails with a clear message rather than silently doing nothing.

Everything else DigiPi's own hardware add-ons cover — GPIO status LEDs, physical pushbuttons, and TFT displays — is tied to the exact wiring of one specific commercial product (the elekitsorparts digiPi HAT) and isn't something DigiHub can verify without that physical board, so it's deliberately left out of scope rather than guessed at.

Updating DigiHub
-----------------
`dhupdate` syncs installed scripts against the latest GitHub repository: new scripts are added, changed scripts are replaced, and scripts no longer present upstream are removed. It shows what will change and asks for confirmation first.

```bash
dhupdate
```

Use `dhupdate --yes` to apply updates without prompting (e.g. from a script or cron job). If `dhgpsmonitor`'s or `dhweb`'s script/application files change and the corresponding service is running, it's restarted automatically.

Every `dhupdate` run — including the daily automated one — also checks that `$HOME/.dhinfo` exists. If it's missing, it's restored automatically from `$HOME/.dhinfo.last`, a rolling backup that `install.sh`, `dhedit`, and `dhweb` all keep up to date before every save. If no backup exists either, `dhupdate` leaves a note that the next `sysinfo` login banner surfaces as "Configuration Missing," since there's nothing to recreate `.dhinfo` from automatically in that case — you'd need to run `install.sh` or `dhedit` yourself.

Installation also enables a systemd timer, `dhupdatecheck`, that runs `dhupdate --check` once a day (around 04:00, with up to 30 minutes of random delay). It never applies script updates — it only checks whether the repository has changed and, if so, leaves a note that the next `sysinfo` login banner will surface as "Update Available: Run 'dhupdate' to review and apply the latest DigiHub changes." The note clears itself automatically once an update is applied (or the pending changes go away upstream). Check its status or logs with:

```bash
systemctl status dhupdatecheck.timer
journalctl -u dhupdatecheck.service
```

HamDB (FCC Callsign Database)
------------------------------
During installation, DigiHub creates a local MariaDB user for `hamdb` and runs `hamdb full` to download and import the complete FCC amateur callsign database. This step is best-effort: if MariaDB isn't reachable or the download fails, installation continues with a warning, and the database can be populated later by running:

```bash
hamdb full
```

The generated MySQL credentials are stored in `$HOME/.hamdb.cnf` (mode 700) and are used automatically by `hamdb` and `qrz` on every run; they are never prompted for or typed by hand.

Installation also enables a systemd timer, `dhhamdbupdate`, that runs `hamdb update` once a day (around 03:00, with up to 30 minutes of random delay to avoid every DigiHub install hitting the FCC at once). Most days this pulls a small daily delta; `hamdb` automatically does a full re-import on the day after Sunday. Check its status or logs with:

```bash
systemctl status dhhamdbupdate.timer
journalctl -u dhhamdbupdate.service
```

Address Geocoding (Optional)
------------------------------
`qrz` can fall back to [Mapbox](https://www.mapbox.com) to fill in a callsign's coordinates when hamdb/hamdb.org don't provide any. This is entirely optional — everything else in DigiHub works fully without it.

Installation asks whether you'd like to enter a Mapbox API token; declining leaves it blank and `qrz` simply skips the geocoding fallback, with no errors and no other effect. A token can be added, changed, or removed at any time afterward with `dhedit`.

GPS Monitor Service
--------------------
When a GPS device is detected during installation, DigiHub installs and enables a systemd service, `dhgpsmonitor`, that periodically checks the GPS position and updates the latitude, longitude, and Maidenhead grid stored in `$HOME/.dhinfo` when the device has moved beyond a configurable distance.

Its configuration lives in `/etc/digihub/gpsmonitor.env`:

| Variable                | Purpose                                             | Default |
|:-------------------------|:-----------------------------------------------------|:--------|
| DigiHubGPSpoll           | Seconds between GPS position checks                  | 30      |
| DigiHubGPSthreshold      | Minimum movement, in meters, before .dhinfo is updated | 20      |

After editing this file, apply the change with:

```bash
sudo systemctl restart dhgpsmonitor
```

Check status or logs with:

```bash
systemctl status dhgpsmonitor
journalctl -u dhgpsmonitor -f
```


Credits                                                   
-------

|           | Link                                          | Purpose               |
|:----------|:----------------------------------------------|:----------------------|
| hamdb.org | https://hamdb.org                             | API Calls (FCC)       |
| mapbox    | https://www.mapbox.com                        | Geolocation           |
| Direwolf  | https://github.com/wb2osz/direwolf            | Direwolf              |
| scripts   | https://github.com/dslotter/ham_radio_scripts | FLdigi Installation   |
| HamPi     | https://github.com/dslotter/HamPi             | Content               |
| hamdb     | https://github.com/k3ng/hamdb                 | Hamdb (MariaDB)       |
| DigiPi    | https://digipi.org                            | Concept & content     |
| usbipd    | https://github.com/dorssel/usbipd-win         | USB Passthrough (WSL) |
| Flask     | https://flask.palletsprojects.com             | Web Interface (dhweb) |
| waitress  | https://github.com/Pylons/waitress            | Web Interface (dhweb) |
| Hamlib    | https://github.com/Hamlib/Hamlib              | CAT Control (rigctld) |
| Pat       | https://github.com/la5nta/pat                 | Winlink Client        |
| ardopcf   | https://github.com/pflarue/ardop              | ARDOP TNC             |
| uronode   | https://sourceforge.net/projects/uronode/     | AX.25 Node/BBS        |
| aprsd     | https://github.com/craigerl/aprsd             | APRS WebChat          |
| aprsd-webchat-extension | https://github.com/hemna/aprsd-webchat-extension | APRS WebChat |
| WSJT-X    | https://wsjt.sourceforge.io/                  | Weak-signal modes     |
| JS8Call   | http://js8call.com/                           | JS8 messaging         |
| qSSTV     | http://users.telenet.be/on4qz/                | Slow-scan TV          |
| TigerVNC  | https://tigervnc.org/                         | Remote Desktop        |
| noVNC     | https://novnc.com/                            | Remote Desktop (browser bridge) |
| Fluxbox   | http://fluxbox.org/                           | Remote Desktop (window manager) |
| FLDigi    | http://www.w1hkj.com/                         | Digital Modes (XML-RPC control) |
