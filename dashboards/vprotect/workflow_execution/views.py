from django.views import generic


class IndexView(generic.TemplateView):
    template_name = 'vprotect/workflow_execution/index.html'
