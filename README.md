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
Has an editable configuration.
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
| dhedit      | DigiHub configuration editor                                | bash        |
| dhgpsmonitor| Background service that updates .dhinfo when GPS position moves | bash/python |
| dhremove    | DigiHub uninstaller                                         | bash        |
| dhupdate    | Sync installed DigiHub scripts against the GitHub repository | bash        |
| hamdb       | FCC Amateur Radio license database                          | bash        |
| maidenhead  | Calculate a Maidenhead ham grid from latitude and longitude | bash/python |
| position    | Get current GPS position from GPS device                    | bash/python |
| qrz         | Check a US callsign using hamdb, hamdb.org & mapbox API     | bash        |
| sysinfo     | System information                                          | bash        |
| whohami     | Show user information held for current configuration        | bash        |

**Note:** * hamdb is installed using MariaDB rather than MySQL. Starting with MariaDB 10.5, the mysqlimport command was replaced with mariadb-import; the version in this repository has been modified to reflect that change, but is otherwise identical.*

Every command above has a detailed reference page (usage, arguments, files, exit codes) under [`help/`](help/) in this repository, e.g. [`help/qrz.txt`](help/qrz.txt).

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

- Edit any field directly (callsign, license, name, address, the Mapbox token, or the AX Node password), or regenerate the AX Node password fresh. The APRS password is derived from the callsign (APRS-IS passcode algorithm) and isn't independently editable — it's regenerated automatically whenever the callsign changes.
- Changing the callsign, or choosing "Refresh from hamdb.org", offers to pull license/name/address details straight from hamdb.org.
- Changing latitude or longitude automatically revalidates and recalculates the Maidenhead grid.
- Add or remove a GPS device: adding re-runs the same auto-detection `install.sh` uses (with a manual entry fallback), updates `.profile`, and installs/enables the `dhgpsmonitor` service; removing resets `.profile` and fully tears the service down.

Nothing is written to `.dhinfo` until you choose "Save and exit"; GPS device changes take effect immediately since they touch `.profile` and systemd, not `.dhinfo`.

Updating DigiHub
-----------------
`dhupdate` syncs installed scripts against the latest GitHub repository: new scripts are added, changed scripts are replaced, and scripts no longer present upstream are removed. It shows what will change and asks for confirmation first.

```bash
dhupdate
```

Use `dhupdate --yes` to apply updates without prompting (e.g. from a script or cron job). If `dhgpsmonitor`'s script changes and the service is running, it's restarted automatically.

Installation also enables a systemd timer, `dhupdatecheck`, that runs `dhupdate --check` once a day (around 04:00, with up to 30 minutes of random delay). It never applies anything — it only checks whether the repository has changed and, if so, leaves a note that the next `sysinfo` login banner will surface as "Update Available: Run 'dhupdate' to review and apply the latest DigiHub changes." The note clears itself automatically once an update is applied (or the pending changes go away upstream). Check its status or logs with:

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
