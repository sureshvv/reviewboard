from django.shortcuts import render_to_response
from django.template.context import RequestContext


def search(request, template_name='rbwebsite/search.html'):
    mutable_get = request.GET.copy()
    if 'cof' in mutable_get:
        del mutable_get['cof']

    return render_to_response(template_name, RequestContext(request, {
        'query': request.GET.get('q'),
        'query_string': mutable_get.urlencode(),
    }))
