import os
import re
from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q

from reviewboard.diffviewer.models import DiffSet, DiffSetHistory, FileDiff
from reviewboard.scmtools.models import Repository
from reviewboard.utils.fields import ModificationTimestampField
from utils.templatetags.htmlutils import thumbnail


class Group(models.Model):
    name = models.CharField(maxlength=64)
    display_name = models.CharField(maxlength=64)
    mailing_list = models.EmailField()
    users = models.ManyToManyField(User, core=False, blank=True,
                                   filter_interface=models.HORIZONTAL)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "/groups/%s/" % self.name

    class Admin:
        pass


class Screenshot(models.Model):
    caption = models.CharField(maxlength=256, blank=True)
    draft_caption = models.CharField(maxlength=256, blank=True)
    image = models.ImageField(upload_to=os.path.join('images', 'uploaded'))

    def thumb(self):
        url = thumbnail(self.image)
        return '<img src="%s" alt="%s" />' % (url, self.caption)
    thumb.allow_tags = True

    def __str__(self):
        return "%s (%s)" % (self.caption, self.image)

    def get_absolute_url(self):
        try:
            review = self.review_request.all()[0]
        except IndexError:
            review = self.inactive_review_request.all()[0]
        return "/r/%s/s/%s/" % (review.id, self.id)

    class Admin:
        list_display = ('thumb', 'caption', 'image')
        list_display_links = ('thumb', 'caption')


class ReviewRequest(models.Model):
    STATUSES = (
        ('P', 'Pending Review'),
        ('S', 'Submitted'),
        ('D', 'Discarded'),
    )

    submitter = models.ForeignKey(User, verbose_name="Submitter")
    time_added = models.DateTimeField("Time Added", default=datetime.now)
    last_updated = ModificationTimestampField("Last Updated")
    status = models.CharField(maxlength=1, choices=STATUSES)
    public = models.BooleanField("Public", default=False)
    changenum = models.PositiveIntegerField("Change Number", blank=True,
                                            null=True, db_index=True)
    repository = models.ForeignKey(Repository)
    email_message_id = models.CharField("E-Mail Message ID", maxlength=255,
                                        blank=True, null=True)
    time_emailed = models.DateTimeField("Time E-Mailed", null=True,
                                        default=None, blank=True)

    summary = models.CharField("Summary", maxlength=300, core=True)
    description = models.TextField("Description")
    testing_done = models.TextField("Testing Done")
    bugs_closed = models.CommaSeparatedIntegerField("Bugs Closed",
                                                    maxlength=300, blank=True)
    diffset_history = models.ForeignKey(DiffSetHistory,
                                        verbose_name='diff set history',
                                        blank=True)
    branch = models.CharField("Branch", maxlength=300, blank=True)
    target_groups = models.ManyToManyField(Group, verbose_name="Target Groups",
                                           core=False, blank=True)
    target_people = models.ManyToManyField(User, verbose_name="Target People",
                                           related_name="directed_review_requests",
                                           core=False, blank=True)
    screenshots = models.ManyToManyField(Screenshot, verbose_name="Screenshots",
                                         related_name="review_request",
                                         core=False, blank=True)
    inactive_screenshots = models.ManyToManyField(Screenshot,
        related_name="inactive_review_request", core=False, blank=True)

    def get_bug_list(self):
        bugs = re.split(r"[, ]+", self.bugs_closed)
        bugs.sort(cmp=lambda x,y: int(x) - int(y))
        return bugs

    def get_absolute_url(self):
        return "/r/%s/" % self.id

    def __str__(self):
        return self.summary

    def _pre_save(self):
        self.bugs_closed = self.bugs_closed.strip()

    class Admin:
        list_display = ('summary', 'submitter', 'status', 'public', \
                        'last_updated')
        list_filter = ('public', 'status', 'time_added', 'last_updated')

    class Meta:
        ordering = ['-last_updated', 'submitter', 'summary']
        unique_together = (('changenum', 'repository'),)
        permissions = (
            ("can_change_status", "Can change status"),
        )


class ReviewRequestDraft(models.Model):
    review_request = models.ForeignKey(ReviewRequest,
                                       verbose_name="Review Request", core=True)
    last_updated = ModificationTimestampField("Last Updated")
    summary = models.CharField("Summary", maxlength=300, core=True)
    description = models.TextField("Description")
    testing_done = models.TextField("Testing Done")
    bugs_closed = models.CommaSeparatedIntegerField("Bugs Closed",
                                                    maxlength=300, blank=True)
    diffset = models.ForeignKey(DiffSet, verbose_name='diff set', blank=True,
                                null=True, core=False)
    branch = models.CharField("Branch", maxlength=300, blank=True)
    target_groups = models.ManyToManyField(Group, verbose_name="Target Groups",
                                           core=False, blank=True)
    target_people = models.ManyToManyField(User, verbose_name="Target People",
                                           related_name="directed_drafts",
                                           core=False, blank=True)
    screenshots = models.ManyToManyField(Screenshot, verbose_name="Screenshots",
                                         core=False, blank=True)
    inactive_screenshots = models.ManyToManyField(Screenshot,
        related_name="inactive_drafts", core=False, blank=True)

    def get_bug_list(self):
        bugs = re.split(r"[, ]+", self.bugs_closed)
        bugs.sort(cmp=lambda x,y: int(x) - int(y))
        return bugs

    def __str__(self):
        return self.summary

    def _submitter(self):
        return self.review_request.submitter

    def _pre_save(self):
        self.bugs_closed = self.bugs_closed.strip()

    @staticmethod
    def create(review_request):
        draft, draft_is_new = \
            ReviewRequestDraft.objects.get_or_create(
                review_request=review_request,
                defaults={
                    'summary': review_request.summary,
                    'description': review_request.description,
                    'testing_done': review_request.testing_done,
                    'bugs_closed': review_request.bugs_closed,
                    'branch': review_request.branch,
                })

        if draft_is_new:
            map(draft.target_groups.add, review_request.target_groups.all())
            map(draft.target_people.add, review_request.target_people.all())
            for screenshot in review_request.screenshots.all():
                screenshot.draft_caption = screenshot.caption
                screenshot.save()
                draft.screenshots.add(screenshot)

            if review_request.diffset_history.diffset_set.count() > 0:
                draft.diffset = review_request.diffset_history.diffset_set.latest()

        return draft

    def save_draft(self):
        request = self.review_request

        request.summary = self.summary
        request.description = self.description
        request.testing_done = self.testing_done
        request.bugs_closed = self.bugs_closed
        request.branch = self.branch

        request.target_groups.clear()
        map(request.target_groups.add, self.target_groups.all())

        request.target_people.clear()
        map(request.target_people.add, self.target_people.all())

        screenshots = self.screenshots.all()
        for s in request.screenshots.all():
            if s in screenshots:
                s.caption = s.draft_caption
                s.save()
        request.screenshots.clear()
        map(request.screenshots.add, self.screenshots.all())

        request.inactive_screenshots.clear()
        map(request.inactive_screenshots.add, self.inactive_screenshots.all())

        if self.diffset:
            self.diffset.history = request.diffset_history
            self.diffset.save()

        request.save()

    class Admin:
        list_display = ('summary', '_submitter', 'last_updated')
        list_filter = ('last_updated',)

    class Meta:
        ordering = ['-last_updated']


class Comment(models.Model):
    filediff = models.ForeignKey(FileDiff, verbose_name='File')
    reply_to = models.ForeignKey("self", blank=True, null=True,
                                 related_name="replies")
    timestamp = models.DateTimeField('Timestamp', default=datetime.now)
    text = models.TextField("Comment Text")

    # A null line number applies to an entire diff.  Non-null line numbers are
    # the line within the entire file, starting at 1.
    first_line = models.PositiveIntegerField("First Line", blank=True,
                                             null=True)
    num_lines = models.PositiveIntegerField("Number of lines", blank=True,
                                            null=True)

    def last_line(self):
        return self.first_line + self.num_lines - 1

    def public_replies(self, user=None):
        if user:
            return self.replies.filter(Q(review__public=True) |
                                       Q(review__user=user))
        else:
            return self.replies.filter(review__public=True)

    def __str__(self):
        return self.text

    class Admin:
        list_display = ('text', 'filediff', 'first_line', 'num_lines',
                        'timestamp')
        list_filter = ('timestamp',)

    class Meta:
        ordering = ['timestamp']


class ScreenshotComment(models.Model):
    screenshot = models.ForeignKey(Screenshot, verbose_name='Screenshot')
    reply_to = models.ForeignKey('self', blank=True, null=True,
                                 related_name='replies')
    timestamp = models.DateTimeField('Timestamp', default=datetime.now)
    text = models.TextField('Comment Text')

    # This is a sub-region of the screenshot.  Null X indicates the entire
    # image.
    x = models.PositiveSmallIntegerField("Sub-image X", null=True)
    y = models.PositiveSmallIntegerField("Sub-image Y")
    w = models.PositiveSmallIntegerField("Sub-image width")
    h = models.PositiveSmallIntegerField("Sub-image height")

    def public_replies(self, user=None):
        if user:
            return self.replies.filter(Q(review__public=True) |
                                       Q(review__user=user))
        else:
            return self.replies.filter(review__public=True)

    def __str__(self):
        return self.text

    class Admin:
        list_display = ('text', 'screenshot', 'timestamp')
        list_filter = ('timestamp',)

    class Meta:
        ordering = ['timestamp']


class Review(models.Model):
    review_request = models.ForeignKey(ReviewRequest)
    user = models.ForeignKey(User)
    timestamp = models.DateTimeField('Timestamp', default=datetime.now)
    public = models.BooleanField("Public", default=False)
    ship_it = models.BooleanField("Ship It", default=False)
    base_reply_to = models.ForeignKey("self", blank=True, null=True,
                                      related_name="replies")
    email_message_id = models.CharField("E-Mail Message ID", maxlength=255,
                                        blank=True, null=True)
    time_emailed = models.DateTimeField("Time E-Mailed", null=True,
                                        default=None, blank=True)

    body_top = models.TextField("Body (Top)", blank=True)
    body_bottom = models.TextField("Body (Bottom)", blank=True)

    body_top_reply_to = models.ForeignKey("self", blank=True, null=True,
                                          related_name="body_top_replies")
    body_bottom_reply_to = models.ForeignKey("self", blank=True, null=True,
                                             related_name="body_bottom_replies")

    comments = models.ManyToManyField(Comment, verbose_name="Comments",
                                      core=False, blank=True)
    screenshot_comments = models.ManyToManyField(ScreenshotComment,
                                                 verbose_name="Screenshot Comments",
                                                 core=False, blank=True)
    reviewed_diffset = models.ForeignKey(DiffSet, verbose_name="Reviewed Diff",
                                         blank=True, null=True)

    def __str__(self):
        return "Review of '%s'" % self.review_request

    def is_reply(self):
        return self.base_reply_to != None
    is_reply.boolean = True

    def public_replies(self):
        return self.replies.filter(public=True)

    def get_absolute_url(self):
        return "%s#review%s" % (self.review_request.get_absolute_url(),
                                self.id)

    class Admin:
        list_display = ('review_request', 'user', 'public', 'ship_it',
                        'is_reply', 'timestamp')
        list_filter = ('public', 'timestamp')

    class Meta:
        ordering = ['timestamp']