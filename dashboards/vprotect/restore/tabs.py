
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs

from openstack_dashboard.dashboards.vprotect.restore import tables

from dashboards.vprotect import utils


class InstanceTab(tabs.TableTab):
    name = _("Instances Tab")
    slug = "instances_tab"
    table_classes = (tables.InstancesTable,)
    attrs = (tables.RestoreAction,)
    template_name = ("horizon/common/_detail_table.html")
    preload = True

    def get_instances_data(self):
        try:
            return list(filter(lambda vm: vm['lastSuccessfulBackupSize'] > 0, utils.fetch_vms(self.request)))
        except Exception:
            error_message = _('Unable to get virtual machines')
            exceptions.handle(self.request, error_message)

            return []

class RestoreTabs(tabs.TabGroup):
    slug = "restore_tabs"
    tabs = (InstanceTab,)
    sticky = True