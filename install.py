
#!/usr/bin/env bash

import os
import shutil
import sys
import yaml
import requests, zipfile, io
from distutils.dir_util import copy_tree
from importlib.metadata import version as ver
from pick import pick

def update_variable(state, variable):
    with open(CONFIG_PATH) as f:
        doc = yaml.safe_load(f)

    doc[variable] = state

    with open(CONFIG_PATH, 'w') as f:
        yaml.safe_dump(doc, f, default_flow_style=False)

def getReleaseLabel(release):
    return release['name']

CONFIG_PATH = 'dashboards/vprotect/config.yaml'
RELEASES_API = 'https://api.github.com/repos/Storware/ovirt-engine-ui-vprotect-extensions/releases'
VERSION_DATA = None

if len(sys.argv) >= 2:
    update_variable(sys.argv[1], 'REST_API_URL')

if len(sys.argv) >= 3:
    update_variable(sys.argv[2], 'USER')

if len(sys.argv) >= 4:
    update_variable(sys.argv[3], 'PASSWORD')

# If the version of package is provided
if len(sys.argv) >= 5:
    requestApi = RELEASES_API + (sys.argv[4] == 'latest' and "/latest" or "/tags/" + sys.argv[4])

    r = requests.get(requestApi)
    if r.json().get('message'):
        print(r.json()['message'])
    else:
        VERSION_DATA = r.json()
else:
    versions = requests.get(RELEASES_API)
    versionsNames = map(getReleaseLabel, versions.json())
    
    if ver('pick').startswith('1.3'):
        option, index = pick(list(versionsNames), "Select a version", indicator='=>', multiselect=False)[0]
    else:
        option, index = pick(list(versionsNames), "Select a version", indicator='=>', multiselect=False)
    
    if option:
        VERSION_DATA = versions.json()[index]


if VERSION_DATA.get('assets'):
    openstackUrl = VERSION_DATA['assets'][0]['browser_download_url']
    package = requests.get(openstackUrl)

    z = zipfile.ZipFile(io.BytesIO(package.content))
    z.extractall("dashboards/vprotect/static/vprotect")
    z.extractall("/usr/share/openstack-dashboard/static/vprotect")

    path = '/usr/share/openstack-dashboard/openstack_dashboard/enabled'
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)

    copy_tree('dashboards/vprotect/', '/usr/share/openstack-dashboard/openstack_dashboard/dashboards/vprotect/')
    shutil.copyfile('enabled/_50_vprotect.py', '/usr/share/openstack-dashboard/openstack_dashboard/enabled/_50_vprotect.py')

