
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs
from openstack_dashboard.dashboards.vprotect.backup import tables

from dashboards.vprotect import utils


def filter_tenant_vms(vprotect_vms, nova_vms):
    return [vm for vm in vprotect_vms if vm['uuid'] in [nova_vm.id for nova_vm in nova_vms]]

class InstanceTab(tabs.TableTab):
    name = _("Instances Tab")
    slug = "instances_tab"
    table_classes = (tables.InstancesTable,)
    attrs = (tables.BackupAction,)
    template_name = ("horizon/common/_detail_table.html")
    preload = True

    def get_instances_data(self):
        try:
            return utils.fetch_vms(self.request)
        except Exception:
            error_message = _('Unable to get instances')
            exceptions.handle(self.request, error_message)

            return []

class BackupTabs(tabs.TabGroup):
    slug = "backup_tabs"
    tabs = (InstanceTab,)
    sticky = True
