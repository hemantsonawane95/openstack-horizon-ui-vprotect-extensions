import requests
import json
import datetime
from django.utils.translation import ugettext_lazy as _
import datetime
from openstack_dashboard import api
from horizon.utils import functions as horizon_utils
import pytz
import yaml

CONFIG = yaml.load(open('openstack_dashboard/dashboards/vprotect/config.yaml', 'r'))
VPROTECT_API_URL = CONFIG['REST_API_URL']
USER = CONFIG['USER']
PASSWORD = CONFIG['PASSWORD']

def login():
    payload = {
        "login": CONFIG['USER'],
        "password": CONFIG['PASSWORD']
    }
    headers = {'content-type': 'application/json'}
    session = requests.Session()
    session.post(VPROTECT_API_URL + '/session/login', data=json.dumps(payload), headers=headers)
    return session

def fetch_vms(request):
    vprotect_vms = login().get(VPROTECT_API_URL + '/virtual-machines?hypervisor-manager-type=OPENSTACK').json()
    instances, has_more = api.nova.server_list(request)
    return __pick_tenant_vms(vprotect_vms, instances)

def __pick_tenant_vms(vprotect_vms, nova_vms):
    return [vm for vm in vprotect_vms if vm['uuid'] in [nova_vm.id for nova_vm in nova_vms]]

def fetch_vprotect_vm(guid):
    return login().get(VPROTECT_API_URL + "/virtual-machines/" + guid)

def fetch_backups_for_vm(guid):
    response = login().get(VPROTECT_API_URL + "/backups?protected-entity=" + guid + "&status=SUCCESS")
    json = response.json() #TODO handle 401 somewhere
    backups = []
    for backup in json:
        backups.append((backup['guid'], '%(backupTime)s (%(guid)s)'
                                    % {"backupTime": datetime.fromtimestamp(backup['backupTime'] / 1000).strftime('%Y-%m-%d %H:%M:%S'), "guid": backup['guid']}))
    if not backups:
        backups.insert(0, ("", _("No backups available")))

    return backups

def fetch_backup_destinations_guid(instance_id):

    payload = [{"name": "", "guid" : instance_id}]
    headers = {'content-type': 'application/json'}

    response = login().post(VPROTECT_API_URL + "/backup-destinations/usable-for-vms", data=json.dumps(payload), headers=headers)

    return __sanitize_backup_destinations(response)

def fetch_backup_destinations():
    headers = {'content-type': 'application/json'}
    response = login().get(VPROTECT_API_URL + "/backup-destinations", headers=headers)
    return __sanitize_backup_destinations(response)

def __sanitize_backup_destinations(response):
    r = response.json()  # TODO handle 401 somewhere
    backup_destinations = []
    for destination in r:
        backup_destinations.append((destination['guid'], '%(name)s (%(guid)s)'
                                    % {"name": destination['name'], "guid": destination['guid']}))
    if not backup_destinations:
        backup_destinations.insert(0, ("", _("No backup destinations available")))
    return backup_destinations

def fetch_schedules(request):
    return login().get(VPROTECT_API_URL + "/schedules?type=VM_BACKUP&tenant-id=" + request.user.tenant_id).json()

def fetch_schedule(guid):
    return login().get(VPROTECT_API_URL + "/schedules/" + guid).json()

def create_rule(name, schedule_guids, backup_destination_guids, policy_guid):
    payload = {"name": name, "schedules" : schedule_guids, "backupDestinations": backup_destination_guids, "policy": policy_guid}
    headers = {'content-type': 'application/json'}
    return login().post(VPROTECT_API_URL + "/rules/vm-backup", data=json.dumps(payload), headers=headers)

def create_policy(name, auto_remove_non_present, vm_guids, fail_remaining_backup_tasks_export_threshold, fail_remaining_backup_tasks_store_threshold):
    payload = {"name" : name,
                "autoRemoveNonPresent" : auto_remove_non_present,
                "autoAssignSettings" : { "mode" : "DISABLED"},
                "vms": vm_guids,
                "failRemainingBackupTasksExportThreshold": fail_remaining_backup_tasks_export_threshold,
                "failRemainingBackupTasksStoreThreshold": fail_remaining_backup_tasks_store_threshold}
    headers = {'content-type': 'application/json'}
    return login().post(VPROTECT_API_URL + "/policies/vm-backup", data=json.dumps(payload), headers=headers)

def fetch_policies():
    response = login().get(VPROTECT_API_URL + "/policies/vm-backup")
    try:
        return [(policy['guid'], policy['name']) for policy in response.json()]
    except JSONDecodeError:
        return []

def fetch_policies_not_sanitized(): #TODO
    return login().get(VPROTECT_API_URL + "/policies/vm-backup").json()

def fetch_policies_by_rules(schedule_rules):
    rules = list(map(lambda sch: sch['guid'], schedule_rules))
    policies = fetch_policies_not_sanitized()
    return list(filter(lambda policy: any(x in rules_in_policy(policy) for x in rules), policies))


def rules_in_policy(policy):
    return list(map(lambda x: x['guid'], policy['rules']))

def create_schedule(data):
    headers = {'content-type': 'application/json'}
    post = login().post(VPROTECT_API_URL + "/schedules", data=data, headers=headers)
    return post

def update_schedule(data, schedule_id):
    headers = {'content-type': 'application/json;charset=UTF-8'}
    post = login().put(VPROTECT_API_URL + "/schedules/" + schedule_id, data=data, headers=headers)
    return post

def fetch_rules_for_policy(policy_guid):
    response = login().get(VPROTECT_API_URL + "/rules/vm-backup?rule=" + policy_guid)
    rules = []
    for rule in response.json():
        rules.append((rule['guid'], '%(name)s (%(guid)s)' % {"name": rule['name'], "guid": rule['guid']}))
    return rules

def fetch_tasks(request):
    return login().get(VPROTECT_API_URL + "/tasks?tenant-id=" + request.user.tenant_id)

def convert_date_to_long(data):
    time_of_the_day = datetime.strptime(data.isoformat(), '%H:%M:%S')
    return time_of_the_day.replace(year=time_of_the_day.year + 70).timestamp() * 1000

def fetch_rules_for_policies(policy_guids):
    rules = []
    for policy in policy_guids:
        rules_for_policy = list(map(lambda rule: rule[0], fetch_rules_for_policy(policy)))
        rules += rules_for_policy
    return rules

def sanitize_vms(virtual_machines):
    vms = []
    for vm in virtual_machines:
        vms.append((vm['guid'], '%(name)s (%(guid)s)'
                        % {"name": vm['name'], "guid": vm['guid']}))
    if not vms:
        vms.insert(0, ("", _("No virtual machines available")))
    return vms

def create_export_task(payload):
    headers = {'content-type': 'application/json'}
    return login().post(VPROTECT_API_URL + "/tasks/export", data=json.dumps(payload), headers=headers)

def determine_vm_id(data):
    try:
        return login().get(VPROTECT_API_URL + "/virtual-machines?uuid=" + data.get('vm_guid')).json()[0]['guid']
    except IndexError:
        return login().get(VPROTECT_API_URL + "/virtual-machines/" + data.get('vm_guid')).json()['guid']


def create_restore_and_import_task(payload):
    headers = {'content-type': 'application/json'}
    return login().post(VPROTECT_API_URL + "/tasks/restore-and-import", data=json.dumps(payload), headers=headers)

def fetch_hypervisor_manager(backup):
    return login().get(VPROTECT_API_URL + "/hypervisor-managers/?backup-to-be-restored=" + backup).json()

def convert_long_to_date(request, timestamp):
    timezone = horizon_utils.get_timezone(request)
    truncated_to_days_with_timezone = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=pytz.timezone(timezone))
    return truncated_to_days_with_timezone + datetime.timedelta(microseconds=1000 * timestamp)