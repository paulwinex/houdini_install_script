# Houdini Auto Install Script

### What is it

Automatically download and install last Houdini build.

### What does it do

- Login in SideFx site using USERNAME and PASSWORD
- Looking for the last Houdini production build on page http://www.sidefx.com/download/daily-builds/
- Download the last build if not downloaded or file is broken
- Extract archive (Linux)
- Start silent installation Houdini only (no Engine or any Servers)

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

### Requires

- Windows or Linux
- python 2.7
- Modules requests and BeautifulSoup
