# Toroid

Simple GUI for Linux Tor proxy

<img width="622" height="609" alt="image" src="https://github.com/user-attachments/assets/06a60f6b-2429-42dc-8db9-059de5abad98" />

***It's not meant to be perfect and/or the fastest - it's just meant to work***

Make sure you have Tor installed, for example:
```
sudo apt install tor obfs4proxy
```
or
```
sudo zypper install tor obfs4
```
## Packaging into an executable
Install dependencies:
```
pip install PySide6 pyinstaller
```
Make a binary:
```
python -m PyInstaller --onefile --windowed --add-data "toroid.conf:." main.py
```
## Using bridges:
Open your toroid.conf

Add these lines at the end of file:
```
ClientTransportPlugin obfs4 exec /path/to/obfs4
Bridge somebrigdehere
Bridge andhere
Bridge evenhere
Bridge andthere
UseBridges 1 
```
For example:
```
## Tor proxy configuration/torrc file
SocksPort 9050
DataDirectory /tmp/tor_temp_data
Log notice stdout
ClientTransportPlugin obfs4 exec /usr/bin/obfs4proxy
Bridge obfs4 195.20.227.157:443 B952...
Bridge obfs4 178.62.227.91:8081 E500...
Bridge obfs4 57.128.57.245:3099 D655...
Bridge obfs4 46.226.107.235:57180 93BD...
UseBridges 1 
```
