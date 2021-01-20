# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from django.utils.translation import ugettext_lazy as _

import horizon

# from dashboards.vprotect.dashboard2.panel import Dashboard2


class VirtualEnvironmentsGroup(horizon.PanelGroup):
    slug = "virtualEnvironmentsGroup"
    name = _("Virtual Environments")
    panels = ('virtualEnvironments', 'policies', 'schedules', 'mountedBackups')


class DashboardGroup(horizon.PanelGroup):
    slug = "dashboardGroup"
    name = _("Dashboard")
    panels = ('dashboard2',)


class TaskConsoleGroup(horizon.PanelGroup):
    slug = "taskConsoleGroup"
    name = _("Task Console")
    panels = ('taskConsole',)


class VProtect(horizon.Dashboard):
    name = _("vProtect")
    slug = "vprotect"
    panels = (DashboardGroup, VirtualEnvironmentsGroup, TaskConsoleGroup,)
    default_panel = "dashboard2"

horizon.register(VProtect)
