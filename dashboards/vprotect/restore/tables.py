from django.utils.translation import ugettext_lazy as _

from horizon import tables

class RestoreAction(tables.LinkAction):
    name = "restore"
    verbose_name = _("Restore")
    url = "horizon:vprotect:restore:restore"
    classes = ("ajax-modal",)
    icon = "camera"

class InstancesTable(tables.DataTable):
    name = tables.Column('name', \
                         verbose_name=_("Name"))
    uuid = tables.Column('guid', \
                         verbose_name=_("GUID"))
    present = tables.Column('present_status', \
                            verbose_name=_("Present"))

    @staticmethod
    def get_object_id(instance):
        instance['present_status'] = "Yes" if instance['present'] else "No"
        return instance['guid']

    class Meta(object):
        name = "instances"
        verbose_name = _("Instances")
        row_actions = (RestoreAction,)