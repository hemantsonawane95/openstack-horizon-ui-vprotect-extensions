from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs

from openstack_dashboard.dashboards.vprotect.schedule import tables
from dashboards.vprotect import utils


class ScheduleTab(tabs.TableTab):
    name = _("Schedule Tab")
    slug = "schedules_tab"
    table_classes = (tables.SchedulesTable,)
    attrs = (tables.EditScheduleAction,)
    template_name = ("horizon/common/_detail_table.html")
    preload = True

    def get_schedules_data(self):
        try:
            return utils.fetch_schedules(self.request)
        except Exception:
            error_message = _('Unable to get schedules')
            exceptions.handle(self.request, error_message)

            return []

class ScheduleTabs(tabs.TabGroup):
    slug = "schedule_tabs"
    tabs = (ScheduleTab,)
    sticky = True