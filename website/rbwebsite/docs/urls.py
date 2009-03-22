from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('',
    url(r'^$',
        'django.views.generic.simple.direct_to_template',
        {'template': 'docs/doc-frontpage.html'},
        name="doc-index"),
)

urlpatterns += patterns('rbwebsite.docs.views',
    url(r'^(?P<section>[\w.-]+)/(?P<version>[\w.-]+)/$', 'document',
        name='doc-section-index'),
    url(r'^(?P<section>[\w.-]+)/(?P<version>[\w.-]+)/(?P<path>[\w./-]*)/$',
        'document',
        name='doc-page'),
    url(r'^(?P<section>[\w.-]+)/(?P<version>[\w.-]+)/_images/(?P<path>[\w./-]*)$',
        'images'),
    url(r'^(?P<section>[\w.-]+)/(?P<version>[\w.-]+)/_source/(?P<path>[\w./-]*)$',
        'source'),
    url(r'^(?P<section>[\w.-]+)/(?P<version>[\w.-]+)/objects.inv$',
        'objects_inv'),
)
