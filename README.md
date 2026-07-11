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
| dhdirewolf  | Runs Direwolf for DigiHub's TNC/digipeater/tracker modes    | bash        |
| dhedit      | DigiHub configuration editor                                | bash        |
| dhgpsmonitor| Background service that updates .dhinfo when GPS position moves | bash/python |
| dhmode      | Switch DigiHub's active digital mode                        | bash        |
| dhremove    | DigiHub uninstaller                                         | bash        |
| dhrig       | Turn DigiHub's CAT control (rigctld) on or off               | bash        |
| dhrigctld   | Runs hamlib's rigctld for DigiHub CAT control                | bash        |
| dhupdate    | Sync installed DigiHub scripts against the GitHub repository | bash        |
| dhweb       | DigiHub web configuration interface                         | python (Flask) |
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
All scripts are tested and working in WSL.  However, in order to leverage a USB-attached GPS device, usbipd needs to be installed and configured.

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

The remaining modes DigiHub is designed to eventually support (`webchat`, `node`, `winlinkrms`, `wsjtx`, `js8call`, `sstv`, `fldigi`) aren't wired up to a service yet; selecting one records the choice in `.dhinfo` without starting anything, as later phases of DigiHub's development add them.

For the Direwolf-backed modes, `dhmode` regenerates `/etc/digihub/direwolf.conf` from `.dhinfo`'s callsign, coordinates, `radiointerface`, and `rigdevice` fields before (re)starting the `dhdirewolf` service. Audio device selection is best-effort (it looks for a single plausible non-built-in USB audio device); PTT method follows `radiointerface` — CM108-style USB adapters (including AIOC and most inexpensive USB radio interfaces) use Dire Wolf's automatic GPIO detection, DigiRig Mobile uses serial RTS on `rigdevice`, and Raspberry Pi audio HATs use a GPIO pin number you supply in `rigdevice`. If auto-detection can't confidently pick an audio device, or the PTT method can't be determined, a warning is logged and you can fix `/etc/digihub/direwolf.conf` by hand (it'll be regenerated the next time you switch modes) or correct the underlying `.dhinfo` field with `dhedit`/`dhweb`.

You can also switch modes from `dhweb`'s Mode page. That requires `dhweb` (which runs as an unprivileged, unattended systemd service) to invoke `dhmode` as root without a password prompt; `install.sh` sets this up with a narrowly scoped sudoers rule (`/etc/sudoers.d/digihub-dhmode`) that permits *only* `/usr/local/bin/dhmode`, and `dhmode` itself still validates the mode name against a fixed list before doing anything privileged.

CAT Control (rigctld)
-------------------------
Separately from digital modes, `dhrig` turns network CAT control on or off — hamlib's `rigctld`, giving other applications (WSJT-X, FLDigi, Winlink clients, etc.) frequency/mode/PTT control of the radio over the network instead of each needing its own serial connection. It's independent of `dhmode`: it can run alongside whichever digital mode is active (or none), as long as they're not fighting over the same physical port.

```bash
dhrig on
```

CAT control needs `rignumber` (a [hamlib rig model number](https://hamlib.sourceforge.net/html/rigctld.1.html), found with `rigctl -l`) and `rigdevice` set first, via `dhedit` or `dhweb`'s Configuration page — `dhrig on` will tell you if they're missing. It's off by default, same as the Direwolf-backed modes, and only starts (installing its systemd unit on first use) once you turn it on. `dhrig status` reports whether it's currently running, and `dhweb`'s Rig Control page offers the same on/off toggle over the same sudoers rule used for mode switching.

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
