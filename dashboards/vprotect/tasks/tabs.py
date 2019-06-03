from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs

from openstack_dashboard.dashboards.vprotect.tasks import tables
from dashboards.vprotect import utils


class TaskTab(tabs.TableTab):
    name = _("Task Tab")
    slug = "task_tab"
    table_classes = (tables.TasksTable,)
    attrs = ()
    template_name = ("horizon/common/_detail_table.html")
    preload = True

    def get_tasks_data(self):
        try:
            return utils.fetch_tasks(self.request).json()
        except Exception:
            error_message = _('Unable to get tasks')
            exceptions.handle(self.request, error_message)
            return []

class TaskTabs(tabs.TabGroup):
    slug = "task_tabs"
    tabs = (TaskTab,)
    sticky = True