# Houdini Auto Install Script

### What is it

Auto install Houdini python script from command line.
For Windows and Linux

### What it do

- This script install only Houdini. Servers and HoudiniEngines will be skipped.
- Script install last build from page http://www.sidefx.com/download/daily-builds/

### How to

Use command line:

Set **USERNAME** and **PASSWORD** of SideFx Site Account

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
