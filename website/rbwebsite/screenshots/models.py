import os
from datetime import datetime

from django.db import models
from django.utils.safestring import mark_safe
from djblets.util.templatetags.djblets_images import thumbnail

from rbwebsite.releases.models import Release


class Screenshot(models.Model):
    release = models.ForeignKey(Release, related_name="screenshots")
    caption = models.CharField(max_length=256, blank=True)
    timestamp = models.DateTimeField(default=datetime.now)
    image = models.ImageField(upload_to=os.path.join("screenshots",
                                                     "%Y", "%m", "%d"))
    thumb_image = models.ImageField(upload_to=os.path.join("screenshots",
                                                           "%Y", "%m", "%d"))
    public = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    def thumb(self):
        return mark_safe('<img src="%s" alt="%s" />' %
                         (self.thumb_image.url, self.caption))
    thumb.allow_tags = True

    def __unicode__(self):
        return u"%s (%s)" % (self.caption, self.image)

    def get_absolute_url(self):
        return self.image.url


    class Meta:
        ordering = ['timestamp']
