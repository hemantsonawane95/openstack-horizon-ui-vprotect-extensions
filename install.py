#!/usr/bin/env bash

import shutil
import sys
import yaml

def update_variable(state, variable):
    with open(CONFIG_PATH) as f:
        doc = yaml.safe_load(f)

    doc[variable] = state

    with open(CONFIG_PATH, 'w') as f:
        yaml.safe_dump(doc, f, default_flow_style=False)

def passed_argument_or_default():
    if len(sys.argv) == 2:
        return sys.argv
    else:
        return "http://localhost:8080/api"

CONFIG_PATH = 'dashboards/vprotect/config.yaml'
URL=passed_argument_or_default()

update_variable(URL, 'REST_API_URL')

shutil.copyfile('dashboards/vprotect', '/usr/share/openstack-dashboard/openstack_dashboard/dashboards/')
shutil.copyfile('_50_vprotect.py', '/usr/share/openstack-dashboard/openstack_dashboard/enabled/')

