from django.db import models


class HappyUserGroup(models.Model):
    name = models.CharField(max_length=256)

    def ordered_happy_users(self):
        return HappyUser.objects.filter(group=self).extra({
            'lower_name': 'lower(name)'
        }).order_by('lower_name')

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']


class HappyUser(models.Model):
    group = models.ForeignKey(HappyUserGroup, related_name="happy_users")
    name = models.CharField(max_length=64)
    url = models.URLField()
    public = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    testimonial = models.TextField(blank=True, null=True)
    private_notes = models.TextField(blank=True, null=True,
        help_text="Private notes about this user, for admin eyes only.")

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
