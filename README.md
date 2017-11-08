# Houdini Silent Install Script

### What is it

Automatically (silent) downloads and installs latest Houdini build.
Good solution for studio pipeline!

### What does it do

- Logs in SideFx site using USERNAME and PASSWORD
- Looking for the latest Houdini production build at http://www.sidefx.com/download/daily-builds/
- Downloads the latest build if it is not yet downloaded or file is corrupted
- Extracts archive (Linux)
- Starts silent installation of Houdini only

### How to

Start script with python in command line. Set **USERNAME** and **PASSWORD** of SideFx Site Account.

_(linux)_
```bash
python ./houdini_install.py -u myusername -p mypassword -i /opt/houdini
```

_(windows start as admin!)_
```cmd
python c:\scripts\houdini_install.py -u myusername -p mypassword -i c:\software\houdini
```

Script will install houdini to folder _installation_dir/build/_

If last Houdini build is 16.5.123 HFS will be _/opt/houdini/16.5.123_ or _c:\software\houdini\16.5.123_

## Flags

- `-i --install_dir` - Installation dir. Required.
- `-u --username` - SideFX site username 
- `-p --password` - SideFX site password 
- `-s --server` - Install Houdini License Server. `y/yes`, `n/no`, `a/auto`. Default `auto` (experimental)

### Requires

- Windows or Linux
- python 2.7
- Python Modules `requests` and `BeautifulSoup`

To install modules call command
```bash
pip install beautifulsoup4 requests
```

### Tested on

- Windows 10 x64
- Ubuntu 16.04

