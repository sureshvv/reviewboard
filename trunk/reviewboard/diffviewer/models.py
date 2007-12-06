import base64
from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from reviewboard.scmtools.models import Repository


class FileDiff(models.Model):
    """
    A diff of a single file.

    This contains the patch and information needed to produce original and
    patched versions of a single file in a repository.
    """
    diffset = models.ForeignKey('DiffSet', edit_inline=models.STACKED,
                                related_name='files',
                                verbose_name=_("diff set"))

    source_file = models.CharField(_("source file"), max_length=256, core=True)
    dest_file = models.CharField(_("destination file"), max_length=256,
                                 core=True)
    source_revision = models.CharField(_("source file revision"), max_length=512)
    dest_detail = models.CharField(_("destination file details"), max_length=512)
    diff_base64 = models.TextField(_("diff (Base64)"))
    binary = models.BooleanField(_("binary file"), default=False)

    def _set_diff(self, data):
        self.diff_base64 = base64.encodestring(data)

    def _get_diff(self):
        return base64.decodestring(self.diff_base64)

    diff = property(fget=lambda self: self._get_diff(),
                    fset=lambda self, v: self._set_diff(v))

    def __unicode__(self):
        return u"%s (%s) -> %s (%s)" % (self.source_file, self.source_revision,
                                        self.dest_file, self.dest_detail)

    class Admin:
        list_display = ('source_file', 'source_revision',
                        'dest_file', 'dest_detail')
        fields = (
            (None, {
                'fields': ('diffset', ('source_file', 'source_revision'),
                           ('dest_file', 'dest_detail'),
                           'binary', 'diff_base64')
            }),
        )


class DiffSet(models.Model):
    """
    A revisioned collection of FileDiffs.
    """
    name = models.CharField(_('name'), max_length=256, core=True)
    revision = models.IntegerField(_("revision"), core=True)
    timestamp = models.DateTimeField(_("timestamp"), default=datetime.now)
    history = models.ForeignKey('DiffSetHistory', null=True, core=True,
                                edit_inline=models.STACKED,
                                verbose_name=_("diff set history"))
    repository = models.ForeignKey(Repository, verbose_name=_("repository"))
    diffcompat = models.IntegerField(
        _('differ compatibility version'),
        default=0,
        help_text=_("The diff generator compatibility version to use. "
                    "This can and should be ignored."))

    def save(self):
        """
        Saves this diffset.

        This will set an initial revision of 1 if this is the first diffset
        in the history, and will set it to on more than the most recent
        diffset otherwise.
        """
        if self.revision == 0 and self.history != None:
            if self.history.diffset_set.count() == 0:
                # Start on revision 1. It's more human-grokable.
                self.revision = 1
            else:
                self.revision = self.history.diffset_set.latest().revision + 1

        super(DiffSet, self).save()

    def __unicode__(self):
        return u"[%s] %s r%s" % (self.id, self.name, self.revision)

    class Admin:
        list_display = ('__unicode__', 'revision', 'timestamp')

    class Meta:
        get_latest_by = 'revision'
        ordering = ['revision', 'timestamp']


class DiffSetHistory(models.Model):
    """
    A collection of diffsets.

    This gives us a way to store and keep track of multiple revisions of
    diffsets belonging to an object.
    """
    name = models.CharField(_('name'), max_length=256)
    timestamp = models.DateTimeField(_("timestamp"), default=datetime.now)

    def __unicode__(self):
        return u'Diff Set History (%s revisions)' % (self.diffset_set.count())

    class Admin:
        pass