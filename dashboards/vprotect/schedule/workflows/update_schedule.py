from horizon import workflows, exceptions, messages
from django.utils.translation import ugettext_lazy as _
from dashboards.vprotect.schedule.workflows.schedule import UpdateSetDetailsStep, SetDaysStep, SetDaysOfWeekStep, SetMonthsStep, SetPoliciesStep
import json
from dashboards.vprotect import utils


class EditSchedule(workflows.Workflow):
    slug = "edit_schedule"
    name = _("Edit Schedule")
    finalize_button_name = _("Edit")
    failure_message = _('Unable to edit schedule "%s".')
    success_url = "horizon:vprotect:schedule:index"
    failure_url = "horizon:vprotect:schedule:index"
    default_steps = (UpdateSetDetailsStep, SetDaysStep, SetDaysOfWeekStep, SetMonthsStep, SetPoliciesStep)

    def handle(self, request, data):
        try:
            active = data['active']
            name = data['name']
            execution_type = data['schedule_execution_type'].upper()
            type = { "name" : "VM_BACKUP"}
            backup_type = data['backup_type']
            days = data['days']
            time_of_the_day = utils.convert_date_to_long(data['time_of_the_day'])
            interval = { "startHour" : utils.convert_date_to_long(data['interval_start']),
                         "endHour" : utils.convert_date_to_long(data['interval_end']),
                         "frequency": data['frequency'] * 60000}
            day_of_week_occurences = data['day_of_week_occurences']
            start_window_length = data['start_window_length'] * 60 * 1000
            rules = utils.fetch_rules_for_policies(data['policies'])
            months = data['months']
            payload = { "active": active,
                        "name" : name,
                        "type" : type,
                        "executionType": execution_type,
                        "backupType" : backup_type,
                        "daysOfWeek": days,
                        "rules" : rules,
                        "dayOfWeekOccurrences": day_of_week_occurences,
                        "startWindowLength" : start_window_length,
                        "hour": time_of_the_day,
                        "interval" : interval,
                        "months" : months}

            schedule = utils.update_schedule(json.dumps(payload), data['schedule_guid'])
            messages.success(request, 'Updated schedule "%s".' % schedule.json()['name'])
            return schedule
        except Exception as e:
            error_msg = self.failure_message % e
            exceptions.handle(request, error_msg)
