from django.utils.translation import ugettext_lazy as _

from dashboards.vprotect import utils
from horizon import workflows
from horizon import forms
from horizon import messages
from horizon import exceptions
import itertools


class SetDetailsAction(workflows.Action):
    name = forms.CharField(label= _("Policy name"), required = True)
    auto_remove_absent_vms = forms.BooleanField(label=_("Auto remove non-present VEs"), required = False)

    class Meta(object):
        name = _("Details")

class SetDetailsStep(workflows.Step):
    action_class = SetDetailsAction
    contributes = ("details",)

    def contribute(self, data, context):
        context.update(data)
        return context

class SetVirtualEnvironmentsAction(workflows.Action):
    ves = forms.MultipleChoiceField(label = "Select Virtual Environments", widget=forms.CheckboxSelectMultiple)

    class Meta(object):
        name = _("Virtual Environments")

    def __init__(self, *args, **kwargs):
        super(SetVirtualEnvironmentsAction, self).__init__(*args, **kwargs)
        self.fields['ves'].choices = [(ve[0], ve[1]) for ve in utils.sanitize_vms(utils.fetch_vms(self.request))]

class SetVirtualEnvironmentsStep(workflows.Step):
    action_class = SetVirtualEnvironmentsAction
    contributes = ("ves",)

    def contribute(self, data, context):
        if data:
            ves = self.workflow.request.POST.getlist("ves")
            context['ves'] = ves
        return context

class SetRulesAction(workflows.Action):
    backup_destination = forms.MultipleChoiceField(required=True, label="Select backup destination",widget=forms.CheckboxSelectMultiple)
    schedules = forms.MultipleChoiceField(required=False, label="Choose schedules",widget=forms.CheckboxSelectMultiple)

    def __init__(self, request, context, *args, **kwargs):
        super(SetRulesAction, self).__init__(request, context, *args,
                                                     **kwargs)
        self.fields['backup_destination'].choices = [(bd[0], bd[1]) for bd in utils.fetch_backup_destinations()]
        self.fields['schedules'].choices = [(schedule['guid'], schedule['name']) for schedule in utils.fetch_schedules(request)]

    class Meta(object):
        name = _("Rule")

class SetRulesStep(workflows.Step):
    action_class = SetRulesAction
    contributes = ("rule",)

    def contribute(self, data, context):
        context.update(data)
        return context

class SetOtherAction(workflows.Action):
    fail_remaining_backup_tasks_export_enabled = forms.IntegerField(initial = 100, label=_("Fail rest of the backup tasks if more than X % of EXPORT tasks already failed (Define percent of already failed EXPORT tasks)"), required = False)
    fail_remaining_backup_tasks_store_enabled = forms.IntegerField(initial = 100, label=_("Fail rest of the backup tasks if more than X % of STORE tasks already failed(Define percent of already failed STORE tasks)"), required = False)

    class Meta(object):
        name = _("Other")

class SetOtherStep(workflows.Step):
    action_class = SetOtherAction
    contributes = ("fail_remaining_backup_tasks_export_enabled", "fail_remaining_backup_tasks_store_enabled",)

    def contribute(self, data, context):
        context.update(data)
        return context

class Policy(workflows.Workflow):
    slug = "policy"
    name = _("Policy")
    finalize_button_name = _("Add")
    failure_message = _('Unable to add policy "%s".')
    success_url = "horizon:vprotect:schedule:index"
    failure_url = "horizon:vprotect:schedule:index"
    default_steps = (SetDetailsStep, SetVirtualEnvironmentsStep, SetRulesStep, SetOtherStep)

    def handle(self, request, data):
        try:
            policy = self.create_policy(data).json()
            rule = self.create_rule(data, policy)
            messages.success(request, self.success_message % policy['name'])
            return rule
        except Exception as e:
            error_msg = self.failure_message % e
            exceptions.handle(request, error_msg)

    def create_rule(self, data, policy):
        name = "Default"
        schedule_guids = list(itertools.chain(data['schedules']))
        backup_destination_guids = list(itertools.chain(data['backup_destination']))
        policy_guid = policy['guid']
        return utils.create_rule(name, schedule_guids, backup_destination_guids, policy_guid)


    def create_policy(self, data):
        data = {"name" : data['name'],
               "autoRemoveNonPresent" : data['auto_remove_absent_vms'],
               "autoAssignSettings" : { "mode" : "DISABLED"},
               "vms": list(itertools.chain(data['ves'])),
               "failRemainingBackupTasksExportThreshold": data['fail_remaining_backup_tasks_export_enabled'],
               "failRemainingBackupTasksStoreThreshold": data['fail_remaining_backup_tasks_store_enabled'],
               "tenantId" : self.request.user.tenant_id}
        return utils.create_policy(data)


