import urllib2

from django.core.management.base import NoArgsCommand
from djblets.feedview import feedparser
from djblets.feedview.templatetags.feedtags import feeddate

from rbwebsite.blogfeeds.models import BlogFeed, BlogFeedPost


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        for blogfeed in BlogFeed.objects.all():
            data = urllib2.urlopen(blogfeed.feed_url).read()
            parser = feedparser.parse(data)

            for entry in parser.entries:
                timestamp = feeddate(entry.updated_parsed)
                post, is_new = BlogFeedPost.objects.get_or_create(
                    feed=blogfeed,
                    post_id=entry.id,
                    defaults={
                        'timestamp': timestamp,
                    })

                post.url = entry.link
                post.title = entry.title
                post.timestamp = timestamp
                post.content = entry.content[0].value
                post.save()
