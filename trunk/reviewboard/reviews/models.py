import os
import re

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from reviewboard.diffviewer.models import DiffSet, DiffSetHistory, FileDiff


class Quip(models.Model):
    PLACES = (
        ('dn', 'Dashboard: By Name'),
        ('dg', 'Dashboard: By Group'),
        ('de', 'Dashboard: Empty'),
        ('dm', 'Dashboard: Mine'),
    )
    place = models.CharField(maxlength=2, choices=PLACES)
    text = models.TextField()

    def __str__(self):
        if len(self.text) < 100:
            return self.text
        else:
            return '%s...' % self.text[:97]

    class Admin:
        pass


class Group(models.Model):
    name = models.CharField(maxlength=64)
    mailing_list = models.EmailField()
    users = models.ManyToManyField(User, core=False, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "/groups/%s/" + self.name

    class Admin:
        pass


class ReviewRequest(models.Model):
    STATUSES = (
        ('P', 'Pending Review'),
        ('S', 'Submitted'),
        ('D', 'Discarded'),
    )

    submitter = models.ForeignKey(User, verbose_name="Submitter")
    time_added = models.DateTimeField("Time Added", auto_now_add=True)
    last_updated = models.DateTimeField("Last Updated", auto_now=True)
    status = models.CharField(maxlength=1, choices=STATUSES)
    public = models.BooleanField("Public", default=False)
    changenum = models.PositiveIntegerField("Change Number", blank=True,
                                            null=True, unique=True,
                                            db_index=True)
    email_message_id = models.CharField("E-Mail Message ID", maxlength=255)

    summary = models.CharField("Summary", maxlength=300, core=True)
    description = models.TextField("Description")
    testing_done = models.TextField("Testing Done")
    bugs_closed = models.CommaSeparatedIntegerField("Bugs Closed",
                                                    maxlength=300, blank=True)
    diffset_history = models.ForeignKey(DiffSetHistory,
                                        verbose_name='diff set history',
                                        blank=True)
    branch = models.CharField("Branch", maxlength=30)
    target_groups = models.ManyToManyField(Group, verbose_name="Target Groups",
                                           core=False, blank=True)
    target_people = models.ManyToManyField(User, verbose_name="Target People",
                                           related_name="target_people",
                                           core=False, blank=True)

    def get_bug_list(self):
        bugs = re.split(r"[, ]+", self.bugs_closed)
        bugs.sort(cmp=lambda x,y: int(x) - int(y))
        return bugs

    def get_absolute_url(self):
        return "/r/%s/" % self.id

    def __str__(self):
        return self.summary

    def save(self):
        self.bugs_closed = self.bugs_closed.strip()
        super(ReviewRequest, self).save()

    class Admin:
        list_display = ('summary', 'submitter', 'status', 'public', \
                        'last_updated')

    class Meta:
        ordering = ['-last_updated', 'submitter', 'summary']


class Screenshot(models.Model):
    caption = models.CharField(maxlength=256, blank=True)
    image = models.ImageField(upload_to=os.path.join('images', 'uploaded'))
    review = models.ForeignKey(ReviewRequest,
                               verbose_name='Review Request')

    class Admin:
        pass


class ReviewRequestDraft(models.Model):
    review_request = models.ForeignKey(ReviewRequest,
                                       verbose_name="Review Request", core=True)
    last_updated = models.DateTimeField("Last Updated", auto_now=True)
    summary = models.CharField("Summary", maxlength=300, core=True)
    description = models.TextField("Description")
    testing_done = models.TextField("Testing Done")
    bugs_closed = models.CommaSeparatedIntegerField("Bugs Closed",
                                                    maxlength=300, blank=True)
    diffset = models.ForeignKey(DiffSet, verbose_name='diff set', blank=True,
                                null=True, core=False)
    branch = models.CharField("Branch", maxlength=30)
    target_groups = models.ManyToManyField(Group, verbose_name="Target Groups",
                                           core=False, blank=True)
    target_people = models.ManyToManyField(User, verbose_name="Target People",
                                           related_name="draft_target_people",
                                           core=False, blank=True)
    screenshots = models.ManyToManyField(Screenshot, verbose_name="Screenshots",
                                         core=False, blank=True)

    def get_bug_list(self):
        bugs = re.split(r"[, ]+", self.bugs_closed)
        bugs.sort(cmp=lambda x,y: int(x) - int(y))
        return bugs

    def __str__(self):
        return self.summary

    def _submitter(self):
        return self.review_request.submitter

    def save(self):
        self.bugs_closed = self.bugs_closed.strip()
        super(ReviewRequestDraft, self).save()

    class Admin:
        list_display = ('summary', '_submitter', 'last_updated')

    class Meta:
        ordering = ['-last_updated']


class Comment(models.Model):
    filediff = models.ForeignKey(FileDiff, verbose_name='File')
    reply_to = models.ForeignKey("self", blank=True, null=True,
                                 related_name="replies")
    timestamp = models.DateTimeField('Timestamp', auto_now_add=True)
    text = models.TextField("Comment Text");

    # A null line number applies to an entire diff.  Non-null line numbers are
    # the line within the entire file, starting at 1.
    first_line = models.PositiveIntegerField("First Line", blank=True,
                                             null=True)
    num_lines = models.PositiveIntegerField("Number of lines", blank=True,
                                            null=True)

    def last_line(self):
        return self.first_line + self.num_lines - 1

    def __str__(self):
        return self.text

    class Admin:
        list_display = ('text', 'filediff', 'first_line', 'num_lines',
                        'timestamp')

    class Meta:
        ordering = ['timestamp']


class Review(models.Model):
    review_request = models.ForeignKey(ReviewRequest)
    user = models.ForeignKey(User)
    timestamp = models.DateTimeField('Timestamp', auto_now_add=True)
    public = models.BooleanField("Public", default=False)
    ship_it = models.BooleanField("Ship It", default=False)
    base_reply_to = models.ForeignKey("self", blank=True, null=True,
                                      related_name="replies")
    email_message_id = models.CharField("E-Mail Message ID", maxlength=255,
                                        blank=True)

    body_top = models.TextField("Body (Top)", blank=True)
    body_bottom = models.TextField("Body (Bottom)", blank=True)

    body_top_reply_to = models.ForeignKey("self", blank=True, null=True,
                                          related_name="body_top_replies")
    body_bottom_reply_to = models.ForeignKey("self", blank=True, null=True,
                                             related_name="body_bottom_replies")

    comments = models.ManyToManyField(Comment, verbose_name="Comments",
                                      core=False, blank=True)
    reviewed_diffset = models.ForeignKey(DiffSet, verbose_name="Reviewed Diff",
                                         blank=True, null=True)

    def __str__(self):
        return "Review of '%s'" % self.review_request

    def is_reply(self):
        return self.base_reply_to != None

    class Admin:
        list_display = ('review_request', 'user', 'public', 'ship_it',
                        'is_reply', 'timestamp')

    class Meta:
        ordering = ['timestamp']
