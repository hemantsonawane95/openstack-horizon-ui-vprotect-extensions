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

from django.urls import reverse_lazy
from horizon import tabs

from openstack_dashboard.dashboards.vprotect.schedule \
    import tabs as vprotect_tabs
from horizon import workflows

from dashboards.vprotect import utils
from openstack_dashboard.dashboards.vprotect.schedule.workflows import schedule, update_schedule, policy


class IndexView(tabs.TabbedTableView):
    tab_group_class = vprotect_tabs.ScheduleTabs
    template_name = 'vprotect/schedule/index.html'

    def get_data(self, request, context, *args, **kwargs):
        return context

class ScheduleView(workflows.WorkflowView):
    workflow_class = schedule.Schedule
    success_url = reverse_lazy("horizon:vprotect:schedule:index")
    submit_url = "horizon:vprotect:schedule:create-schedule"

    def get_initial(self):
        backup_destinations = utils.fetch_backup_destinations()
        policies = utils.fetch_policies()
        return {"backup_destinations": backup_destinations, "policies" : policies}

class EditScheduleView(workflows.WorkflowView):
    workflow_class = update_schedule.EditSchedule
    success_url = reverse_lazy("horizon:vprotect:schedule:index")
    submit_url = "horizon:vprotect:schedule:edit-schedule"

    def get_object(self):
        return utils.fetch_schedule(self.kwargs['schedule_id'])

    def get_context_data(self, **kwargs):
        context = super(EditScheduleView, self).get_context_data(**kwargs)
        context['schedule'] = self.get_object()
        return context

    def get_initial(self):
        schedule = self.get_object()
        data = {'active' : schedule['active'],
                'backup_type' : schedule['backupType']['name'],
                'day_of_week_occurences': list(map(lambda sch: sch['name'], schedule['dayOfWeekOccurrences'])),
                'days' : list(map(lambda sch: sch['name'], schedule['daysOfWeek'])),
                'schedule_execution_type' : schedule['executionType']['name'].lower(),
                'schedule_guid' : schedule['guid'],
                'time_of_the_day' : utils.convert_long_to_date(self.request, schedule['hour']),
                'interval_start' : utils.convert_long_to_date(self.request, self.get_nested_field(schedule, 'interval', 'startHour')),
                'interval_end' : utils.convert_long_to_date(self.request, self.get_nested_field(schedule, 'interval', 'endHour')),
                'frequency': int(self.get_nested_field(schedule, 'interval', 'frequency')) / 60000,
                'months' : list(map(lambda sch: sch['name'], schedule['months'])),
                'name' : schedule['name'],
                'rules' : schedule['rules'],
                'start_window_length' : int(schedule['startWindowLength'] / 60000),
                'policies' : [policy['guid'] for policy in utils.fetch_policies_by_rules(schedule['rules'])],
                'type' : schedule['type']
                }
        return data

    def get_nested_field(self, object, field, nested_field):
        try:
            return object[field][nested_field]
        except KeyError:
            return 0


class CreatePolicyView(workflows.WorkflowView):
    workflow_class = policy.Policy
    success_url = reverse_lazy("horizon:vprotect:schedule:index")
    submit_url = "horizon:vprotect:schedule:create-policy"

    def get_initial(self):
        backup_destinations = utils.fetch_backup_destinations()
        vms = utils.sanitize_vms(utils.fetch_vms(self.request))
        schedules = list(map(lambda schedule: (schedule['guid'], schedule['name']), utils.fetch_schedules(self.request)))
        return {"backup_destinations": backup_destinations,
                "virtual_machines" : vms,
                "schedules" : schedules}