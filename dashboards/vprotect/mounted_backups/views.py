from django.views import generic


class IndexView(generic.TemplateView):
    template_name = 'vprotect/mounted_backups/index.html'
