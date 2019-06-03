from django.utils.translation import ugettext_lazy as _

from dashboards.vprotect import utils
from horizon import forms
from horizon import messages
from django.urls import reverse
from horizon import exceptions

class Restore(forms.SelfHandlingForm):
    backup = forms.ChoiceField(label=_("Backup"), required = True)
    restored_name = forms.CharField(label=_("Virtual machine name (optional)"), required = False)

    error_message = _('Couldn\'t restore "%s".')
    success_message = _('Created restore task for instance "%s".')

    def __init__(self, *args, **kwargs):
        super(Restore, self).__init__(*args, **kwargs)
        self.fields['backup'].choices = kwargs.get('initial', {}).get("backups", [])
        self.kwargs = kwargs

    def handle(self, request, data):
        try:
            backup = data['backup']
            restored_name = data['restored_name']
            vm_guid = self.kwargs['initial']['instance_id']
            hypervisor_manager = utils.fetch_hypervisor_manager(backup)
            payload = { "backup" : backup,
                        "dstProtectedEntity" :  {"guid" : vm_guid, "type" : "VM" },
                        "hypervisorManager": { "guid" : hypervisor_manager[0]['guid'] },
                        "restoredPeName" : restored_name,
                        "projectId" : self.request.user.tenant_id}
            restore_and_import_task = utils.create_restore_and_import_task(payload)
            messages.success(request, self.success_message % restore_and_import_task.json()['dstProtectedEntity']['name'])
            return restore_and_import_task
        except Exception as e:
            redirect = reverse("horizon:vprotect:restore:index")
            error_msg = self.error_message % e
            exceptions.handle(request, error_msg, redirect=redirect)