from django.utils.translation import ugettext_lazy as _

from horizon import tables

class TasksTable(tables.DataTable):
    state = tables.Column('state_description', \
                         verbose_name=_("State"))
    progress = tables.Column('progress', \
                             verbose_name=_("Progress"))
    type = tables.Column('task_type', \
                           verbose_name=_("Type"))
    instance = tables.Column('instance_name', \
                                 verbose_name=_("Instance"))
    backup_destination = tables.Column('backup_destination_name', \
                             verbose_name= ("Backup destination"))

    @staticmethod
    def get_object_id(datum):
        datum['state_description'] = datum['state']['description']
        datum['task_type'] = datum['type']['description']
        datum['instance_name'] = TasksTable.field_or_empty(datum, 'protectedEntity')
        datum['backup_destination_name'] = TasksTable.field_or_empty(datum, 'backupDestination')
        return datum['guid']

    @staticmethod
    def field_or_empty(datum, field):
        try:
            return datum[field]['name']
        except KeyError:
            return ""

    class Meta(object):
        name = "tasks"
        verbose_name = _("Tasks")