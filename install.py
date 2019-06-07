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

CONFIG_PATH = 'dashboards/vprotect/config.yaml'

if len(sys.argv) == 2:
    update_variable(sys.argv[1], 'REST_API_URL')

if len(sys.argv) == 3:
    update_variable(sys.argv[2], 'USER')

if len(sys.argv) == 4:
    update_variable(sys.argv[3], 'PASSWORD')

shutil.copyfile('dashboards/vprotect', '/usr/share/openstack-dashboard/openstack_dashboard/dashboards/')
shutil.copyfile('_50_vprotect.py', '/usr/share/openstack-dashboard/openstack_dashboard/enabled/')

