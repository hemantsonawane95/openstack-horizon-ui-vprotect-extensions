from django.views import generic


class IndexView(generic.TemplateView):
    template_name = 'vprotect/dashboard2/index.html'
