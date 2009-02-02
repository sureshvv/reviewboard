from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('rbwebsite.donations.views',
    url(r'^$', 'donate_page', name="donate"),
)
