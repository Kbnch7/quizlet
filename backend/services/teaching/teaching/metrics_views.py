from django.http import HttpResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from common.monitoring.common import registry


def metrics(request):
    output = generate_latest(registry)
    return HttpResponse(output, content_type=CONTENT_TYPE_LATEST)

