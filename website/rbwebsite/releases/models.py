from datetime import datetime

from django.db import models


class Product(models.Model):
    slug = models.SlugField(max_length=128)
    name = models.CharField(max_length=128)
    visible = models.BooleanField(default=True)
    third_party = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class Release(models.Model):
    RELEASE_TYPES = (
        ("alpha", "Alpha"),
        ("beta",  "Beta"),
        ("rc",    "RC"),
        ("final", "Final"),
    )

    product = models.ForeignKey(Product, related_name="releases")
    name = models.CharField(max_length=128, blank=True)
    major_version = models.PositiveIntegerField()
    minor_version = models.PositiveIntegerField()
    micro_version = models.PositiveIntegerField()
    release_type = models.CharField(max_length=5, choices=RELEASE_TYPES)
    release_num = models.PositiveIntegerField("release number", blank=True)

    timestamp = models.DateTimeField(default=datetime.now)

    scm_revision = models.CharField(max_length=128, blank=True,
        help_text="The revision the release is based on.")

    description = models.TextField(blank=True)
    changes = models.TextField(blank=True)
    bugs_fixed = models.CommaSeparatedIntegerField("bugs fixed",
                                                   max_length=1024,
                                                   blank=True)

    @property
    def version(self):
        ver = "%s.%s" % (self.major_version, self.minor_version)

        if self.micro_version != 0:
            ver += ".%s" % self.micro_version

        if self.release_type != "final":
            ver += " %s %s" % (self.release_type, self.release_num)

        return ver

    def __unicode__(self):
        return u"%s %s" % (self.product, self.version)

    class Meta:
        ordering = ['timestamp']
        get_latest_by = 'timestamp'
