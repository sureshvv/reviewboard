from django.conf.urls.defaults import patterns, url

from rbwebsite.happyusers.models import HappyUserGroup


urlpatterns = patterns('',
    url(r'^$',
        'django.views.generic.simple.direct_to_template',
        {'template': 'rbwebsite/happy-users.html',
         'extra_context': {
             'groups': HappyUserGroup.objects.all(),
         }
        },
        name='happy-users'),
)
