from django.db import models


class PressGroup(models.Model):
    name = models.CharField(max_length=256)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']


class PressItem(models.Model):
    group = models.ForeignKey(PressGroup, related_name="press_items")
    name = models.CharField(max_length=256)
    url = models.URLField()
    press_date = models.DateField(null=True)
    public = models.BooleanField(default=True)

    author = models.CharField(max_length=256, blank=True)
    author_url = models.URLField(blank=True)

    location = models.CharField(max_length=128, blank=True)
    location_url = models.URLField(blank=True)

    publication = models.CharField(max_length=128, blank=True)
    publication_url = models.URLField(blank=True)

    language = models.CharField(max_length=64, blank=True)

    description = models.TextField(blank=True, null=True)
    private_notes = models.TextField(blank=True, null=True,
        help_text="Private notes about this item, for admin eyes only.")

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['-press_date', 'name']
