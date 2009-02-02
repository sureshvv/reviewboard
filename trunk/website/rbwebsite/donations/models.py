from datetime import datetime

from django.db import models


class FundRun(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    public = models.BooleanField(default=True)
    goal = models.PositiveIntegerField()

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.goal)


class Goal(models.Model):
    fund_run = models.ForeignKey(FundRun, related_name="goals")
    name = models.CharField(max_length=64)
    amount = models.PositiveIntegerField()
    public = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.amount)


class Donation(models.Model):
    fund_run = models.ForeignKey(FundRun, related_name="donations")
    name = models.CharField(max_length=64)
    email = models.EmailField(blank=True)
    amount = models.PositiveIntegerField()
    date = models.DateField(default=datetime.now)

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.amount)
