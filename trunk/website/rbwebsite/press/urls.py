from django.conf.urls.defaults import patterns, url

from rbwebsite.press.models import PressGroup


urlpatterns = patterns('',
    url('^$', 'django.views.generic.simple.direct_to_template',
        {'template': 'rbwebsite/press.html',
         'extra_context': {
             'groups': PressGroup.objects.all(),
         }
        },
        name='press'),
)
