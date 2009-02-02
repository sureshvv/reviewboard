from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.syndication.feeds import Feed
from django.core.exceptions import ObjectDoesNotExist
from django.utils.feedgenerator import Atom1Feed

from rbwebsite.news.models import NewsPost


def add_domain(url):
    if not (url.startswith("https://") or url.startswith("http://")):
        url = "http://%s%s" % (Site.objects.get_current().domain, url)

    return url


class RssNewsFeed(Feed):
    title = "News Posts"
    link = "/news/"
    description = "Latest Review Board news posts"

    title_template = "news/feed_title.html"
    description_template = "news/feed_description.html"

    def item_author_link(self, item):
        try:
            return add_domain(item.author.blog_feeds.get().site_url)
        except BlogFeed.DoesNotExist:
            return None

    def item_author_name(self, item):
        return item.author.username

    def item_author_email(self, item):
        return item.author.email

    def item_pubdate(self, item):
        return item.timestamp

    def item_link(self, item):
        return add_domain(item.get_absolute_url())

    def items(self):
        return NewsPost.objects.filter(public=True)[:20]


class AtomNewsFeed(RssNewsFeed):
    feed_type = Atom1Feed
