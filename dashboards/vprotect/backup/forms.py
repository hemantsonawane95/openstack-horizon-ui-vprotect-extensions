from django.utils.translation import ugettext_lazy as _

from horizon import forms
from horizon import messages
from django.urls import reverse
from horizon import exceptions

from dashboards.vprotect import utils


class Backup(forms.SelfHandlingForm):
    backup_destination = forms.ChoiceField(label=_("Backup Destination"), required = True)
    backup_type = forms.ChoiceField(label=_("Backup type"), choices=(('FULL', _('Full')), ('INCREMENTAL', _('Incremental')),), required = True)

    error_message = _('Couldn\'t backup "%s".')
    success_message = _('Created export task for instance "%s".')

    def __init__(self, *args, **kwargs):
        super(Backup, self).__init__(*args, **kwargs)
        backup_destinations = kwargs.get('initial', {}).get("backup_destinations", [])
        self.kwargs = kwargs
        self.fields['backup_destination'].choices = backup_destinations

    def handle(self, request, data):
        try:
            backup_destination = data['backup_destination']
            backup_type = data['backup_type']
            vm_guid = self.kwargs['initial']['instance_id']
            payload = { "backupType" : backup_type,
                        "backupDestination" : { "guid" : backup_destination},
                        "protectedEntities" : [ {"guid" : vm_guid} ],
                        "projectId" : request.user.tenant_id}
            export_task = utils.create_export_task(payload)
            messages.success(request, self.success_message % self.kwargs['initial']['instance']['name'] )
            return export_task
        except Exception as e:
            redirect = reverse("horizon:vprotect:backup:index")
            error_msg = self.error_message % e
            exceptions.handle(request, error_msg, redirect=redirect)
