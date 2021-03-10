from django.views import generic


class IndexView(generic.TemplateView):
    template_name = 'vprotect/virtual_environments/index.html'
