from django.views import generic


class IndexView(generic.TemplateView):
    template_name = 'vprotect/policies_and_schedules/index.html'
