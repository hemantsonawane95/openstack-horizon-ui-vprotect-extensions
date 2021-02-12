from django.views import generic
from django.http import JsonResponse
from django.core import serializers
import requests
import yaml

CONFIG = yaml.safe_load(open('/usr/share/openstack-dashboard/openstack_dashboard/dashboards/vprotect/config.yaml', 'r'))
VPROTECT_API_URL = CONFIG['REST_API_URL']
USER = CONFIG['USER']
PASSWORD = CONFIG['PASSWORD']

class IndexView(generic.TemplateView):
    template_name = 'vprotect/dashboard2/index.html'


class JsonView(generic.TemplateView):
    def get(self, request):
        return JsonResponse(request.body.decode('utf-8'), safe=False)

def login():
    payload = {
        "login": CONFIG['USER'],
        "password": CONFIG['PASSWORD']
    }
    headers = {'content-type': 'application/json'}
    session = requests.Session()
    session.post(VPROTECT_API_URL + '/session/login', data=json.dumps(payload), headers=headers)
    return session

def json(request):
    url = request.build_absolute_uri()
    if request.method == 'POST':
        #login().get(VPROTECT_API_URL + ).json()
        return JsonResponse({url: url})
    else:
        return render(request,'accounts/register.html')

    # return JsonResponse(request.decode('utf-8'), safe=False)
