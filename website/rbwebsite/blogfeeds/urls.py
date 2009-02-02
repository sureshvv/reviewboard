from django.conf.urls.defaults import patterns, url

from rbwebsite.blogfeeds.models import BlogFeedPost
from rbwebsite.blogfeeds.feeds import RssBlogFeed, AtomBlogFeed


rss_feeds = {
    'latest': RssBlogFeed,
}

atom_feeds = {
    'latest': AtomBlogFeed,
}


urlpatterns = patterns('',
    url(r'^$', 'django.views.generic.list_detail.object_list',
        { 'template_name': 'rbwebsite/blogs.html',
          'template_object_name': 'post',
          'paginate_by': 5,
          'queryset': BlogFeedPost.objects.all(),
        },
        name='developer-blogs'),
)

urlpatterns += patterns('django.contrib.syndication.views',
    # Feeds
    url(r'^feeds/rss/(?P<url>.*)/$', 'feed',
        {'feed_dict': rss_feeds},
        name="rss-feed"),
    url(r'^feeds/atom/(?P<url>.*)/$', 'feed',
        {'feed_dict': atom_feeds},
        name="atom-feed"),
)

# Redirect the main feed to FeedBurner
urlpatterns += patterns('django.views.generic.simple',
    url(r'^feeds/$', 'redirect_to',
        {'url': 'http://feeds.feedburner.com/ReviewBoard'}),
)
