from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.syndication.feeds import Feed
from django.core.exceptions import ObjectDoesNotExist
from django.utils.feedgenerator import Atom1Feed

from rbwebsite.blogfeeds.models import BlogFeedPost


def add_domain(url):
    if not (url.startswith("https://") or url.startswith("http://")):
        url = "http://%s%s" % (Site.objects.get_current().domain, url)

    return url


class RssBlogFeed(Feed):
    title = "Developer Blog Posts"
    link = "/news/"
    description = "Latest Review Board developer blog posts"

    title_template = "news/feed_title.html"
    description_template = "news/feed_description.html"

    def item_author_link(self, item):
        return add_domain(item.feed.site_url)

    def item_author_name(self, item):
        return item.feed.author.username

    def item_author_email(self, item):
        return item.feed.author.email

    def item_pubdate(self, item):
        return item.timestamp

    def item_link(self, item):
        return item.get_absolute_url()

    def items(self):
        return BlogFeedPost.objects.filter()[:20]


class AtomBlogFeed(RssBlogFeed):
    feed_type = Atom1Feed
