import os

from django.conf.urls.defaults import include, patterns, url, \
                                      handler404, handler500
from django.conf import settings
from django.contrib import admin
from djblets.util.misc import generate_cache_serials

from rbwebsite.happyusers.models import HappyUser
from rbwebsite.news.models import NewsPost
from rbwebsite.news.sitemaps import NewsSitemap
from rbwebsite.sitemaps import PageSitemap


generate_cache_serials()
admin.autodiscover()


def get_testimonial_user():
    users = HappyUser.objects.exclude(testimonial="").order_by('?')

    if users:
        return users[0]

    return None


sitemaps = {
    'news': NewsSitemap,
    'pages': PageSitemap,
}


urlpatterns = patterns('',
    url(r'^$',
        'django.views.generic.simple.direct_to_template',
        {'template': 'rbwebsite/frontpage.html',
         'extra_context': {
             'testimonial_user': get_testimonial_user,
             'latest_news': NewsPost.objects.filter(public=True)[:6],
         }
        },
        name="front-page"),

    # Donations
    (r'^donate/', include('rbwebsite.donations.urls')),

    # "About" links
    (r'^news/', include('rbwebsite.news.urls')),
    (r'^blog/', include('rbwebsite.blogfeeds.urls')),
    (r'^screenshots/', include('rbwebsite.screenshots.urls')),
    (r'^press/$', include('rbwebsite.press.urls')),

    # "Get Started" links
    (r'^downloads/', include('rbwebsite.releases.urls')),
    (r'^docs/', include('rbwebsite.docs.urls')),

    # "Community" links
    url(r'^mailing-lists/$',
        'django.views.generic.simple.direct_to_template',
        {'template': 'rbwebsite/mailing-lists.html'},
        name="mailing-lists"),
    (r'^users/', include('rbwebsite.happyusers.urls')),

    url('^summer-of-code/$',
        'django.views.generic.simple.direct_to_template',
        {'template': 'rbwebsite/summer-of-code.html'},
        name='summer-of-code'),
    url('^summer-of-code/hosting/$',
        'django.views.generic.simple.direct_to_template',
        {'template': 'rbwebsite/summer-of-code-hosting.html'}),
    url('^summer-of-code/2009/$',
        'django.views.generic.simple.direct_to_template',
        {'template': 'rbwebsite/summer-of-code-2009.html'}),

    url('^thirdparty/$',
        'django.views.generic.simple.direct_to_template',
        {'template': 'rbwebsite/third-party.html'},
        name='third-party'),

    # "Development" links
    url('^bugs/$',
        'django.views.generic.simple.redirect_to',
        {'url': 'http://code.google.com/p/reviewboard/issues/list'},
        name='bugs'),
    url('^bugs/new/$',
        'django.views.generic.simple.redirect_to',
        {'url': 'http://code.google.com/p/reviewboard/issues/entry'}),
    url('^bugs/(?P<bugnum>[0-9]+)/$',
        'django.views.generic.simple.redirect_to',
        {'url': 'http://code.google.com/p/reviewboard/issues/detail?id=%(bugnum)s'}),
    url('^wiki/$',
        'django.views.generic.simple.redirect_to',
        {'url': 'http://code.google.com/p/reviewboard/wiki/'},
        name='wiki'),
    url('^wiki/(?P<page>[^/]+)/$',
        'django.views.generic.simple.redirect_to',
        {'url': 'http://code.google.com/p/reviewboard/wiki/%(page)s'},
        name='wiki-page'),


    # Old redirects
    url('^users.php$',
        'django.views.generic.simple.redirect_to',
        {'url': 'users/'}),


    # Search
    (r'^search/$', 'rbwebsite.search.views.search'),

    # Admin UI
    (r'^admin/(.*)', admin.site.root),

    # Sitemaps
    (r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap',
     {'sitemaps': sitemaps}),
)


if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
        (r'^media/(?P<path>.*)$', 'serve', {
            'show_indexes': True,
            'document_root': os.path.join(settings.HTDOCS_ROOT, "media"),
            }),
    )
