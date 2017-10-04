import sys, re, os, shutil, argparse
import ctypes
try:
    import requests
except ImportError:
    print 'This script require requests module.\n Install: pip install requests'
    sys.exit()
try:
    from bs4 import BeautifulSoup
except ImportError:
    print 'This scrip require BeautifulSoup package (https://www.crummy.com/software/BeautifulSoup/bs4/doc/#).' \
          '\nInstall: pip install beautifulsoup4'
    sys.exit()

# VARIABLES ################################
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--install_dir", type=str, help="Instalation dir")
parser.add_argument("-u", "--username", type=str, help="SideFx account username")
parser.add_argument("-p", "--password", type=str, help="SideFx account password")

_args, other_args = parser.parse_known_args()
username = _args.username
password = _args.password
if not username or not password:
    print 'Please set username and password'
    print 'Example: -u username -p password'
    sys.exit()

install_dir = _args.install_dir
if not install_dir:
    print 'ERROR: Please set installation folder in argument -i. For example: -i "%s"' % ('/opt/houdini' if os.name == 'postx' else 'c:\\cgsoft\\houdini')
    sys.exit()
install_dir = install_dir.replace('\\', '/').rstrip('/')
tmp_folder = os.path.expanduser('~/temp_houdini')


############################################################# START #############


def create_output_dir(istall_dir, build):
    """
    Change this to define installation folder
    """
    if os.name == 'nt':
        return os.path.join(install_dir, build).replace('/', '\\')
    else:
        return '/'.join([install_dir.rstrip('/'), build])


def windows_is_admin():
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin


# define OS
if os.name == 'nt':
    category = 'win'
    if not windows_is_admin():
        print 'Run this script as administrator'
        sys.exit()
elif os.name == 'posix':
    category = 'linux'
else:
    raise Exception('This OS not supported')

# create client
client = requests.session()
# Retrieve the CSRF token first
URL = 'https://www.sidefx.com/login/'
print 'Login on %s ...' % URL
client.get(URL)  # sets cookie
csrftoken = client.cookies['csrftoken']
# create login data
login_data = dict(username=username, password=password, csrfmiddlewaretoken=csrftoken, next='/')
# login
r = client.post(URL, data=login_data, headers=dict(Referer=URL))

# goto daily builds page
print 'Get last build version...'
page = client.get('http://www.sidefx.com/download/daily-builds/')

# parse page
s = BeautifulSoup(page.content, 'html.parser')

# get all versions
# lin = s.findAll('div', {'class': lambda x: x and 'category-' + categorys['linux'] in x.split()})

# get last version
a = s.find('div', {'class': lambda x: x and 'category-'+category in x.split()}).find('a')

# get build
build = re.match(r".*?(\d+\.\d+\.\d+).*", str(a.text)).group(1)
print 'Last build is ', build

# check your last version here
if not os.path.exists(install_dir):
    os.makedirs(install_dir)

if build in os.listdir(install_dir):
    print 'Build {} already installed'.format(build)
    sys.exit()

# if your version is lower go to download
print 'Start download...'
# download url
url = 'http://www.sidefx.com' + a.get('href').split('=')[-1] + 'get/'
print '  DOWNLOAD URL:', url

# create local file path
if not os.path.exists(tmp_folder):
    os.makedirs(tmp_folder)
local_filename = os.path.join(tmp_folder, a.text).replace('\\', '/')
print '  Local File:', local_filename

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
        print 'Skip download'
        need_to_download = False

if need_to_download:
    # download file
    print 'Total size %sMb' % int(total_length/1024.0/1024.0)
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
    print
    print 'Download complete'

# start silent installation
print 'Start install Houdini'
if os.name == 'posix':
    # unzip
    print 'Unpack "%s" to "%s"' % (local_filename, tmp_folder)
    cmd = 'tar xf {} -C {}'.format(local_filename, tmp_folder)
    os.system(cmd)
    # os.remove(local_filename)
    install_file = os.path.join(tmp_folder, os.path.splitext(os.path.splitext(os.path.basename(local_filename))[0])[0], 'houdini.install')
    print 'Install File', install_file
    # ./houdini.install --auto-install --accept-EULA --make-dir /opt/houdini/16.0.705
    out_dir = create_output_dir(install_dir, build)
    cmd = './houdini.install {} {}'.format(
        '--auto-install --accept-EULA --make-dir',
        out_dir
    )
    print 'Create output folder', out_dir
    if not os.path.exists(out_dir):
        print 'Create folder:', out_dir
        os.makedirs(out_dir)
    print 'Start install...'
    # print 'CMD:\n'+cmd
    print 'GoTo', os.path.dirname(install_file)
    os.chdir(os.path.dirname(install_file))
    os.system(cmd)
    # sudo chown -R paul: /opt/houdini/16.0.705
    # sudo chmod 777 -R
    os.system('chown -R paul: ' + out_dir)
    os.system('chmod 777 -R ' + out_dir)
    # delete downloaded file
    # shutil.rmtree(tmp_folder)
else:
    out_dir = create_output_dir(install_dir, build)
    print 'Create output folder', out_dir
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    cmd = '"{houdini_install}" /S /AcceptEula=yes /LicenseServer=No /DesktopIcon=No ' \
          '/FileAssociations=Yes /HoudiniServer=No /EngineUnity=No ' \
          '/EngineMaya=No /EngineUnreal=No /HQueueServer=No ' \
          '/HQueueClient=No /IndustryFileAssociations=Yes /InstallDir="{install_dir}" ' \
          '/LicenseServer=No /ForceLicenseServer=No /MainApp=Yes /Registry=Yes'.format(
        houdini_install=local_filename,
        install_dir=out_dir
        )
    print 'CMD:\n' + cmd
    print 'Start install...'
    os.system(cmd)
    print 'If installation not happen, repeat process.'
