from django.conf.urls.defaults import patterns, url

from rbwebsite.news.feeds import RssNewsFeed, AtomNewsFeed
from rbwebsite.news.models import Category, NewsPost


news_info = {
    'template_name': 'news/news.html',
    'date_field': 'timestamp',
    'queryset': NewsPost.objects.filter(public=True),
    'extra_context': {
        'categories': Category.objects.all(),
        'all_posts': NewsPost.objects.filter(public=True),
        'dates': NewsPost.objects.all().dates("timestamp", "month", "DESC"),
    },
}

news_post_info = news_info.copy()
news_post_info.update({
    'template_name': 'news/post.html',
    'template_object_name': 'post',
    'queryset': NewsPost.objects.all(),
    'month_format': '%m',
    'slug_field': 'slug',
})

rss_feeds = {
    'latest': RssNewsFeed,
}

atom_feeds = {
    'latest': AtomNewsFeed,
}


urlpatterns = patterns('django.views.generic.date_based',
    url(r'^$', 'archive_index',
        dict({
            'num_latest': 10,
            'template_object_name': 'object_list',
        }, **news_info),
        name='news'),
    url(r'^(?P<year>\d{4})/$', 'archive_year',
        dict({
            'make_object_list': True,
        }, **news_info)),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'archive_month',
        dict({
            'month_format': '%m',
        }, **news_info)),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$',
        'archive_day', news_info),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$',
        'object_detail',
        news_post_info,
        name="news-post"),
)

urlpatterns += patterns('django.contrib.syndication.views',
    # Feeds
    url(r'^feed/rss/(?P<url>.*)/$', 'feed',
        {'feed_dict': rss_feeds},
        name="rss-feed"),
    url(r'^feed/atom/(?P<url>.*)/$', 'feed',
        {'feed_dict': atom_feeds},
        name="atom-feed"),
)

# Redirect the main feed to FeedBurner
urlpatterns += patterns('django.views.generic.simple',
    url(r'^feed/$', 'redirect_to',
        {'url': 'http://feeds.feedburner.com/ReviewBoardNews'}),
)
