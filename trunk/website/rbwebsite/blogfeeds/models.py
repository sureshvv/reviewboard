from django.db import models
from django.contrib.auth.models import User


class BlogFeed(models.Model):
    author = models.ForeignKey(User, related_name="blog_feeds")
    site_url = models.URLField()
    feed_url = models.URLField()

    def __unicode__(self):
        return u"%s's feed" % self.author

    class Meta:
        ordering = ['author']


class BlogFeedPost(models.Model):
    feed = models.ForeignKey(BlogFeed, related_name="posts")
    post_id = models.CharField(max_length=256)
    url = models.URLField()
    title = models.CharField(max_length=256)
    timestamp = models.DateTimeField()
    content = models.TextField()

    def get_absolute_url(self):
        return self.url

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['-timestamp']
