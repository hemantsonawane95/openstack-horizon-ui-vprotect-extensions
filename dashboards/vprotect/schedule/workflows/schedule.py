
from horizon import workflows, forms, exceptions, messages
from django.utils.translation import ugettext_lazy as _

import json
import datetime
class SetDetailsAction(workflows.Action):
    backup_type_help = _("Incremental backup is available only for selected platforms")
    active = forms.BooleanField(label=_("Active"), required=False, initial=True)
    name = forms.CharField(label=_("Schedule name"), required = False)
    backup_type = forms.ChoiceField(help_text=backup_type_help, label = "Backup type", choices = ( ('FULL', _('Full')), ('INCREMENTAL', _('Incremental')) ))
    schedule_execution_type = forms.ChoiceField(label ="Schedule execution type",
                                                choices = [ ('time', _('Time')),
                                                            ('interval', _('Interval')) ],
                                                widget=forms.ThemableSelectWidget(
                                                    attrs={
                                                        'class': 'switchable',
                                                        'data-slug': 'source'
                                                    }
                                                ))
    time_of_the_day = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                'type': 'time',
                'class': 'switched',
                'data-switch-on': 'source',
                'data-source-time': _('Time of the day')
            }),
        label=_("Time of the day"),
        initial = datetime.datetime.now(),
        required=False)
    interval_start = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                'type': 'time',
                'class': 'switched',
                'data-switch-on': 'source',
                'data-source-interval': _('Choose time of interval start')
            }),
        label=_("Choose time of interval start"),
        initial=datetime.datetime(1970, 12, 31, 00, 00, 00),
        required=False)
    interval_end = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                'type': 'time',
                'class': 'switched',
                'data-switch-on': 'source',
                'data-source-interval': _('Choose time of interval end')
            }),
        label=_("Choose time of interval end"),
        initial=datetime.datetime(1970, 12, 31, 23, 59, 59),
        required=False)
    frequency = forms.IntegerField(label = "Frequency [min]",
                                             widget=forms.NumberInput(
                                                 attrs={
                                                     'class': 'switched',
                                                     'data-switch-on': 'source',
                                                     'data-source-interval': _('Frequency [min]')
                                                 }),
                                             initial = 120)

    start_window_length = forms.IntegerField(label = "Start Window length [min]", widget=forms.NumberInput(
        attrs={
            'class': 'switched',
            'data-switch-on': 'source',
            'data-source-time': _('Start window length [min]')
        }), initial = 300)

    class Meta(object):
        name = _("Details")

class SetDetailsStep(workflows.Step):
    action_class = SetDetailsAction
    contributes = ("active", "name", "schedule_execution_type", "backup_type", "time_of_the_day", "interval_start", "interval_end", "frequency", "start_window_length",)

    def contribute(self, data, context):
        if data:
            details = self.workflow.request.POST.getlist("details")
            if details:
                context['details'] = data
        context.update(data)
        return context

class UpdateSetDetailsStep(workflows.Step):
    action_class = SetDetailsAction
    contributes = ("active", "name", "schedule_execution_type", "backup_type", "time_of_the_day", "interval_start", "interval_end", "frequency", "start_window_length",)
    depends_on = ("schedule_guid",)

    def contribute(self, data, context):
        if data:
            details = self.workflow.request.POST.getlist("details")
            if details:
                context['details'] = data
        context.update(data)
        return context

class SetDaysAction(workflows.Action):
    days = forms.MultipleChoiceField(required=True, label="Days", widget=forms.CheckboxSelectMultiple, choices = (    ('MONDAY', _('Monday')),
                                                                                                                      ('TUESDAY', _('Tuesday')),
                                                                                                                      ('WEDNESDAY', _('Wednesday')),
                                                                                                                      ('THURSDAY', _('Thursday')),
                                                                                                                      ('FRIDAY', _('Friday')),
                                                                                                                      ('SATURDAY', _('Saturday')),
                                                                                                                      ('SUNDAY', _('Sunday')) ))
    class Meta(object):
        name = _("Days")

class SetDaysStep(workflows.Step):
    action_class = SetDaysAction
    contributes = ("days",)

    def contribute(self, data, context):
        if data:
            days = self.workflow.request.POST.getlist("days")
            if days:
                context['days'] = days
        return context

class SetDaysOfWeekAction(workflows.Action):
    day_of_week_occurences = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple, label="Day of week occurence", choices = (('FIRST_IN_MONTH', _('First in month')),
                                                                                                                                                      ('SECOND_IN_MONTH', _('Second in month')),
                                                                                                                                                      ('THIRD_IN_MONTH', _('Third in month')),
                                                                                                                                                      ('FOURTH_IN_MONTH', _('Fourth in month')),
                                                                                                                                                      ('LAST_IN_MONTH', _('Last in month'))))
    class Meta(object):
        name = _("Days of week occurences")


class SetDaysOfWeekStep(workflows.Step):
    action_class = SetDaysOfWeekAction
    contributes = ("day_of_week_occurences",)

    def contribute(self, data, context):
        if data:
            day_of_week_occurences = self.workflow.request.POST.getlist("day_of_week_occurences")
            context['day_of_week_occurences'] = day_of_week_occurences
        return context

class SetMonthsAction(workflows.Action):
    months = forms.MultipleChoiceField(required=False, label="Months",widget=forms.CheckboxSelectMultiple, choices = (    ('JANUARY', _('January')),
                                                                                                                          ('FEBRUARY', _('February')),
                                                                                                                          ('MARCH', _('March')),
                                                                                                                          ('APRIL', _('April')),
                                                                                                                          ('MAY', _('May')),
                                                                                                                          ('JUNE', _('June')),
                                                                                                                          ('JULY', _('July')),
                                                                                                                          ('AUGUST', _('August')),
                                                                                                                          ('SEPTEMBER', _('September')),
                                                                                                                          ('OCTOBER', _('October')),
                                                                                                                          ('NOVEMBER', _('November')),
                                                                                                                          ('DECEMBER', _('December')) ))
    class Meta(object):
        name = _("Months")

class SetMonthsStep(workflows.Step):
    action_class = SetMonthsAction
    contributes = ("months",)

    def contribute(self, data, context):
        if data:
            months = self.workflow.request.POST.getlist("months")
            context['months'] = months
        return context


from dashboards.vprotect import utils


class SetPoliciesAction(workflows.Action):
    policies = utils.fetch_policies()
    policiesChoices = [(policy[0], policy[1]) for policy in policies]
    policies = forms.MultipleChoiceField(label=_("Choose policies"), required=False,widget=forms.CheckboxSelectMultiple, choices = policiesChoices)

    class Meta(object):
        name = _("Policies")

class SetPoliciesStep(workflows.Step):
    action_class = SetPoliciesAction
    contributes = ("policies",)

    def contribute(self, data, context):
        if data:
            policies = self.workflow.request.POST.getlist("policies")
            context['policies'] = policies
        return context

class Schedule(workflows.Workflow):
    slug = "schedule"
    name = _("Schedule")
    finalize_button_name = _("Add")
    failure_message = _('Unable to add schedule "%s".')
    success_url = "horizon:vprotect:schedule:index"
    failure_url = "horizon:vprotect:schedule:index"
    default_steps = (SetDetailsStep, SetDaysStep, SetDaysOfWeekStep, SetMonthsStep, SetPoliciesStep)

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
                        "months" : months,
                        "tenantId": self.request.user.tenant_id}
            schedule = utils.create_schedule(json.dumps(payload))
            messages.success(request, 'Added schedule "%s".' % schedule.json()['name'])
            return schedule
        except Exception as e:
            error_msg = self.failure_message % e
            exceptions.handle(request, error_msg)