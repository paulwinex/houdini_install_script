from __future__ import print_function
import sys, re, os, shutil, argparse
import getpass

try:
    import requests
except ImportError:
    print('This script require requests module.\n Install: pip install requests')
    sys.exit()
try:
    from bs4 import BeautifulSoup
except ImportError:
    print('This scrip require BeautifulSoup package (https://www.crummy.com/software/BeautifulSoup/bs4/doc/#).' 
          '\nInstall: pip install beautifulsoup4')
    sys.exit()

# VARIABLES ################################
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--install_dir", type=str, help="Installation dir")
parser.add_argument("-u", "--username", type=str, help="SideFx account username")
parser.add_argument("-p", "--password", type=str, help="SideFx account password")
parser.add_argument("-s", "--server", type=str, help="Install License server (y/yes, n/no, a/auto, default auto)")
parser.add_argument("-pr", "--production", help="Filter only production builds", action='store_true')


_args, other_args = parser.parse_known_args()
username = _args.username
password = _args.password
if not username or not password:
    print('Please set username and password')
    print('Example: -u username -p password')
    sys.exit()

install_dir = _args.install_dir
if not install_dir:
    print('ERROR: Please set installation folder in argument -i. For example: -i "%s"' % (
        '/opt/houdini' if os.name == 'postx' else 'c:\\cg\\houdini'))
    sys.exit()
install_dir = install_dir.replace('\\', '/').rstrip('/')
tmp_folder = os.path.expanduser('~/temp_houdini')

# license server
lic_server = False
if os.name == 'nt':
    if not os.path.exists('C:/Windows/System32/sesinetd.exe'):
        lic_server = True
elif os.name == 'posix':
    if not os.path.exists('/usr/lib/sesi/sesinetd'):
        lic_server = True

if _args.server:
    if _args.server in ['y', 'yes']:
        lic_server = True
    elif _args.server in ['n', 'no']:
        lic_server = False


############################################################# START #############


def create_output_dir(install_dir, build):
    """
    Change this to define installation folder
    """
    if os.name == 'nt':
        return os.path.join(install_dir, build).replace('/', '\\')
    else:
        return '/'.join([install_dir.rstrip('/'), build])


def windows_is_admin():
    import ctypes
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin


# define OS
if os.name == 'nt':
    if not windows_is_admin():
        print('Run this script as administrator')
        sys.exit()
# urls
BASE_URL = 'https://www.sidefx.com/'
LOGIN_URL = BASE_URL+'login/'
BUILDS_URL = BASE_URL+'download/daily-builds/get/'
# current os
OS = dict(win32='win', linux='linux', darwin='mac')[sys.platform]
client = requests.session()
# sets cookie
client.get(LOGIN_URL)
csrftoken = client.cookies['csrftoken']
# create login data
login_data = dict(username=username, password=password, csrfmiddlewaretoken=csrftoken, next='/')
# login
print('Login on %s ...' % LOGIN_URL)
client.post(LOGIN_URL, data=login_data, headers=dict(Referer=BASE_URL))


def get_builds():
    # request all builds
    content = client.get(BUILDS_URL)
    data = content.json()
    from collections import defaultdict
    builds = defaultdict(dict)
    for build in data['daily_builds_releases']:
        if build['product'] == 'houdini':
            build_name = "{}.{}".format(build['version'], build['build'])
            builds[build_name]['build'] = build_name
            builds[build_name]['is_production'] = build['release'] == 'gold'
            builds[build_name]['urls'] = builds[build_name].get('urls', defaultdict(list))
            builds[build_name]['urls'][build['os']].append(dict(filename=build['display_name'],
                                                                url=BASE_URL + build['download_url'] + 'get/'))
    builds = [{'urls': dict(v['urls']), 'build': k, 'is_production': v['is_production']} for k, v in builds.items()]
    return builds

# create client

# Retrieve the CSRF token first

builds = get_builds()
builds = [x for x in builds if OS in x['urls']]
if _args.production:
    builds = [x for x in builds if x['is_production']]
from pprint import pprint
pprint(builds)
build = sorted(builds, key=lambda x: x['build'], reverse=True)[0]
print('Latest build is:', build['build'])

# check your last version here
if not os.path.exists(install_dir):
    os.makedirs(install_dir)

if build in os.listdir(install_dir):
    print('Build {} already installed'.format(build))
    sys.exit()

# if your version is lower go to download
print('Start download...')
# download url
url = build['urls'][OS][0]['url']
filename = build['urls'][OS][0]['filename']
print('  DOWNLOAD URL:', url)

# create local file path
if not os.path.exists(tmp_folder):
    os.makedirs(tmp_folder)
local_filename = os.path.join(tmp_folder, filename).replace('\\', '/')
print('  Local File:', local_filename)

# get content
resp = client.get(url, stream=True)
total_length = int(resp.headers.get('content-length'))
need_to_download = True
if os.path.exists(local_filename):
    # compare file size
    if not os.path.getsize(local_filename) == total_length:
        os.remove(local_filename)
    else:
        # skip downloading if file already exists
        print('Skip download')
        need_to_download = False

if need_to_download:
    # download file
    print('Total size %sMb' % int(total_length / 1024.0 / 1024.0))
    block_size = 1024*4
    dl = 0
    with open(local_filename, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=block_size):
            if chunk:
                f.write(chunk)
                f.flush()
                dl += len(chunk)
                done = int(50 * dl / total_length)
                sys.stdout.write("\r[%s%s] %sMb of %sMb" % ('=' * done,
                                                            ' ' * (50-done),
                                                            int(dl/1024.0/1024.0),
                                                            int(total_length/1024.0/1024.0)
                                                            )
                                 )
                sys.stdout.flush()
    print()
    print('Download complete')

# start silent installation
print('Start install Houdini')
if os.name == 'posix':
    # unzip
    print('Unpack "%s" to "%s"' % (local_filename, tmp_folder))
    cmd = 'sudo tar xf {} -C {}'.format(local_filename, tmp_folder)
    os.system(cmd)
    # os.remove(local_filename)
    install_file = os.path.join(tmp_folder, os.path.splitext(os.path.splitext(os.path.basename(local_filename))[0])[0], 'houdini.install')
    print('Install File', install_file)
    # ./houdini.install --auto-install --accept-EULA --make-dir /opt/houdini/16.0.705
    out_dir = create_output_dir(install_dir, build)
    flags = '--auto-install --accept-EULA --make-dir'
    if lic_server:
        pass
    cmd = 'sudo ./houdini.install {flags} {dir}'.format(
        flags=flags,
        dir=out_dir
    )
    print('Create output folder', out_dir)
    if not os.path.exists(out_dir):
        print('Create folder:', out_dir)
        os.makedirs(out_dir)
    print('Start install...')
    # print 'CMD:\n'+cmd
    print('GoTo', os.path.dirname(install_file))
    os.chdir(os.path.dirname(install_file))
    os.system(cmd)
    # sudo chown -R paul: /opt/houdini/16.0.705
    # sudo chmod 777 -R
    # whoami
    # setup permission
    os.system('chown -R %s: %s' % (getpass.getuser(), out_dir))
    os.system('chmod 777 -R ' + out_dir)
    # delete downloaded file
    # shutil.rmtree(tmp_folder)
else:
    out_dir = create_output_dir(install_dir, build)
    print('Create output folder', out_dir)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    cmd = '"{houdini_install}" /S /AcceptEula=yes /LicenseServer={lic_server} /DesktopIcon=No ' \
          '/FileAssociations=Yes /HoudiniServer=No /EngineUnity=No ' \
          '/EngineMaya=No /EngineUnreal=No /HQueueServer=No ' \
          '/HQueueClient=No /IndustryFileAssociations=Yes /InstallDir="{install_dir}" ' \
          '/ForceLicenseServer={lic_server} /MainApp=Yes /Registry=Yes'.format(
            lic_server='Yes' if lic_server else 'No',
            houdini_install=local_filename,
            install_dir=out_dir
            )
    print('CMD:\n' + cmd)
    print('Start install...')
    os.system(cmd)
    print('If installation not happen, repeat process.')
