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


from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import tabs
from horizon import exceptions
from horizon import forms

from horizon.utils import memoized

from openstack_dashboard.dashboards.vprotect.restore \
    import forms as project_forms
from openstack_dashboard.dashboards.vprotect.restore \
    import tabs as vprotect_tabs
from dashboards.vprotect import utils


class IndexView(tabs.TabbedTableView):
    tab_group_class = vprotect_tabs.RestoreTabs
    template_name = 'vprotect/restore/index.html'

    def get_data(self, request, context, *args, **kwargs):
        return context

class RestoreView(forms.ModalFormView):
    form_class = project_forms.Restore
    template_name = 'vprotect/restore/restore.html'
    success_url = reverse_lazy("horizon:vprotect:restore:index")
    modal_id = "restore_modal"
    modal_header = _("Restore")
    submit_label = _("Restore")
    submit_url = "horizon:vprotect:restore:restore"

    @memoized.memoized_method
    def get_object(self):
        try:
            return utils.fetch_vprotect_vm(self.kwargs['instance_id'])
        except Exception:
            exceptions.handle(self.request, _("Unable to retrieve virtual machine."))

    def get_initial(self):
        return {"instance_id": self.kwargs['instance_id'], "backups": utils.fetch_backups_for_vm(self.kwargs['instance_id'])}

    def get_context_data(self, **kwargs):
        context = super(RestoreView, self).get_context_data(**kwargs)
        instance_id = self.kwargs['instance_id']
        context['instance_id'] = instance_id
        context['instance'] = self.get_object()
        context['submit_url'] = reverse(self.submit_url, args=[instance_id])
        return context