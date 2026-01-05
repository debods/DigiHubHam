DigiHub - Digital Hub for ham radio 
===================================

W0FFS
-----

Overview
--------
DigiHub is not an application or environment; it is a curated collection of ham radio utilities and applications geared toward Digital ham radio Operations.

It was conceived as an alternative to the popular DigiPi, which is an excellent implementation and is a highly recommended option for those setting out on the digital ham path.

DigiHub builds on the DigiPi concept and is designed to be installed on an existing Debian system rather than being a complete Operating System image. Also, it is re-configurable.

The installation script has been built and tested on Debian trixie 64-bit, which includes Raspberry Pi OS running on a Pi Zero 2W, 3, 4, or 5.

The primary design goal of DigiHub is flexibility and configurability:

Digihub
|:---------------------------------------------------------------------------------------------------|
Validates (US) callsigns.
Has an editable configuration.
Automatically calculates the Maidenhead grid square from the Latitude and Longitude when using a GPS device.
Automatically generates the correct APRS password.
Automatically generates a random alphanumeric AX node password.
Can be installed for an individual or club callsign.
Can be installed on an existing Debian Linux trixie x64 Operating System.
It is entirely free.

Command Line Utilities
---------------------
A number of the methods used to install, run, and maintain DigiHub are included as command line utilities:

| Command     | Purpose                                                     | Written in  |
|:------------|:------------------------------------------------------------|:------------|
| aprspass    | Generate an APRS password                                   | bash/python |
| axnodepass  | Generate a random alphanumeric AX Node password             | bash        |
| qrz         | Check a US callsign using the hamdb API                     | bash        |
| dhconfig    | DigiHub configuration editor/uninstaller                    | bash        |
| position    | Get current GPS position from GPS device                    | bash/python |
| maidenhead  | Calculate a Maidenhead ham grid from latitude and longitude | bash/python |
| sysinfo     | System information                                          | bash        |
| whohami     | Show user information held for current configuration        | bash        |

GPS Devices
-----------
DigiHub will detect and use correctly installed and working GPS devices.

A recommended GPS device is a Waveshare L76X Multi-GNSS HAT (available [here](https://www.waveshare.com/l76x-gps-hat.htm)). It works with any PC hardware via USB and with Raspberry Pi via the GPIO header.

Custom Installation
-------------------
DigiHub leverages the hamdb.org API for automatic callsign validation and user data.

It is reliable for the United States (US), Canada (CA), and Australia (AU) because the database is updated daily for the Czech Republic (CZ) and Germany (DE); the database is updated monthly. For other countries, there is no reliable resource.

For non-US/AU/CA/CZ and custom installations, entering 'nodb' as the callsign when installing DigiHub, e.g., ./install.sh nodb, will allow manual entry of the unvalidated callsign and other required/optional details.

Installation
-------------
Ensure the Operating System you are installing on has an active Internet connection, and that, if you intend to use a GPS, it is connected and working.

**Note:** * As part of the installation process, there is an option to update the OS (recommended). If DigiHub is removed, any packages added by the installer will be removed.*

Issue the following commands:

If necessary, install git:
```bash
sudo apt install git
```
Change directory to the install folder, make the installer executable, and run it:

```bash
git clone https://github.com/debods/DigiHubHam.git
cd DigiHubHam
chmod +x install.sh
./install.sh <callsign>
```
All software installed by DigiHub is open-source licensed and freely available.

Credits                                                   
-------

| Source    | Link                                          | Purpose             |
|:----------|:----------------------------------------------|:--------------------|
| hamdb.org | https://hamdb.org                             | API Calls           |
| Direwolf  | https://github.com/wb2osz/direwolf            | Direwolf            |
| scripts   | https://github.com/dslotter/ham_radio_scripts | FLdigi Installation |
| DigiPi    | https://digipi.org                            | Concept & content   |






