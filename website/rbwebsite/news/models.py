import os
import re
from datetime import datetime

from django.db import models
from django.db.models import permalink
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify


class Category(models.Model):
    slug = models.SlugField(max_length=64)
    name = models.CharField(max_length=64)

    @permalink
    def get_absolute_url(self):
        return ('news-category', None, {
            'slug': self.slug,
        })

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"


class NewsPost(models.Model):
    categories = models.ManyToManyField(Category, related_name="posts")
    author = models.ForeignKey(User, related_name="news_posts")

    slug = models.SlugField(max_length=256)
    title = models.CharField(max_length=256)
    timestamp = models.DateTimeField()
    public = models.BooleanField(default=True)
    content = models.TextField()

    @permalink
    def get_absolute_url(self):
        return ("news-post", None, {
            'year': self.timestamp.strftime("%Y"),
            'month': self.timestamp.strftime("%m"),
            'day': self.timestamp.strftime("%d"),
            'slug': self.slug,
        })

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(self.title)

            counter_finder = re.compile(r'-\d+$')
            counter = 1

            while 1:
                existing_count = NewsPost.objects.filter(slug=slug).count()

                if existing_count == 0:
                    break

                counter += 1
                counter_str = "-%i" % counter
                slug = "%s%s" % (slug[:256 - len(counter_str)],
                                 counter_str)

            self.slug = slug

        super(NewsPost, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['-timestamp']


class Image(models.Model):
    caption = models.CharField(max_length=256, blank=True)
    timestamp = models.DateTimeField(default=datetime.now)
    image = models.ImageField(upload_to=os.path.join("uploaded", "images",
                                                     "%Y", "%m", "%d"))

    def thumb(self):
        url = thumbnail(self.image, size="400x300")
        return mark_safe('<img src="%s" alt="%s" />' % (url, self.caption))
    thumb.allow_tags = True

    def __unicode__(self):
        return u"%s (%s)" % (self.caption, self.image)

    def get_absolute_url(self):
        return self.image.url