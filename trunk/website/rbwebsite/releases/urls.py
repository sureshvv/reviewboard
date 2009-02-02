from django.conf.urls.defaults import patterns, url

from rbwebsite.releases.models import Product


urlpatterns = patterns('',
    url('^$', 'django.views.generic.simple.direct_to_template',
        {'template': 'rbwebsite/downloads.html',
         'extra_context': {
             'products': Product.objects.filter(visible=True,
                                                third_party=False),
         }
        },
        name='downloads'),
)
