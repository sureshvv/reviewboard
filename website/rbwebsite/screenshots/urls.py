from django.conf.urls.defaults import patterns, url

from rbwebsite.releases.models import Product
from rbwebsite.screenshots.models import Screenshot


def get_screenshots():
    product = Product.objects.get(slug="reviewboard")
    latest_release = product.releases.latest()
    return Screenshot.objects.filter(
        release__major_version=latest_release.major_version)


urlpatterns = patterns('',
    url('^$', 'django.views.generic.simple.direct_to_template',
        {'template': 'rbwebsite/screenshots.html',
         'extra_context': {
             'screenshots': get_screenshots,
         }
        },
        name='screenshots'),
)
