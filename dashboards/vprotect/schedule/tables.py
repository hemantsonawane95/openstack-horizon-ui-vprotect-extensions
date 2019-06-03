from django.utils.translation import ugettext_lazy as _

from horizon import tables
from dashboards.vprotect import utils


class CreateScheduleAction(tables.LinkAction):
    name = "create_schedule"
    verbose_name = _("Create Schedule")
    url = "horizon:vprotect:schedule:create-schedule"
    classes = ("ajax-modal",)
    icon = "camera"

class CreatePolicyAction(tables.LinkAction):
    name = "create_policy"
    verbose_name = _("Create Policy")
    url = "horizon:vprotect:schedule:create-policy"
    classes = ("ajax-modal",)
    icon = "camera"

class EditScheduleAction(tables.LinkAction):
    name = "schedule"
    verbose_name = _("Edit Schedule")
    url = "horizon:vprotect:schedule:edit-schedule"
    classes = ("ajax-modal",)
    icon = "camera"


def fetch_shortened_day_names(days_of_week):
    return ", ".join(list(map(lambda x: x[:3], days_of_week)))


def determine_schedule_time_by_type(request, datum):
    if datum['executionType']['name'] == 'INTERVAL':
        return "Every " + str(int(datum['interval']['frequency'] / 60000)) + " minutes"
    else:
        return "At " + utils.convert_long_to_date(request, datum['hour']).strftime("%H:%M")


class SchedulesTable(tables.DataTable):
    name = tables.Column('name', \
                         verbose_name=_("Name"))
    active = tables.Column('active_status', \
                         verbose_name=_("Active"))
    days_of_week = tables.Column('daysOfWeekShortNames', \
                           verbose_name=_("Days"))
    schedule = tables.Column('schedule', \
                             verbose_name= ("Schedule"))
    backup_type = tables.Column('backupTypeDescription', \
                         verbose_name=_("Backup Type"))
    policies = tables.Column('policiesCount', \
                             verbose_name= ("Policies"))
    start_window = tables.Column('startWindowLengthInMinutes', \
                                 verbose_name= ("Start window [min]"))

    def get_object_id(self, schedule):
        schedule['active_status'] = "Yes" if schedule['active'] else "No"
        schedule['policiesCount'] = len(schedule['rules'])
        schedule['startWindowLengthInMinutes'] = int(schedule['startWindowLength'] / 60000)
        schedule['backupTypeDescription'] = schedule['backupType']['description']
        schedule['daysOfWeekShortNames'] = fetch_shortened_day_names(list(map(lambda day: day['description'], schedule['daysOfWeek'])))
        schedule['schedule'] = determine_schedule_time_by_type(self.request, schedule)
        return schedule['guid']

    class Meta(object):
        name = "schedules"
        verbose_name = _("Schedules")
        row_actions = (EditScheduleAction,)
        table_actions = (CreateScheduleAction, CreatePolicyAction)