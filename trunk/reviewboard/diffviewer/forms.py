import base64

from django import newforms as forms
from django.conf import settings
from django.core import validators
from django.core.validators import ValidationError
from reviewboard.diffviewer.models import DiffSet, FileDiff
import reviewboard.diffviewer.parser as diffparser
import reviewboard.scmtools as scmtools
from scmtools import PRE_CREATION

class UploadDiffForm(forms.Form):
    # XXX: it'd be really nice to have "required" dependent on scmtool
    basedir = forms.CharField(required=False)
    path = forms.CharField(widget=forms.FileInput())

    def create(self, file, diffset_history=None):
        # Parse the diff
        files = diffparser.parse(file["content"])

        if len(files) == 0:
            raise Exception("Empty diff") # XXX

        # Check that we can actually get all these files.
        tool = scmtools.get_tool()

        if tool.get_diffs_use_absolute_paths():
            basedir = ''
        else:
            basedir = str(self.clean_data['basedir']) + '/'

        for f in files:
            f2, revision = tool.parse_diff_revision(f.origFile, f.origInfo)
            filename = basedir + f2

            if revision != PRE_CREATION and \
               not tool.file_exists(filename, revision):
                raise scmtools.FileNotFoundException(filename, revision)

        diffset = DiffSet(name=file["filename"], revision=0,
                          history=diffset_history)
        diffset.save()

        for file in files:
            filediff = FileDiff(diffset=diffset,
                                source_file=basedir + file.origFile,
                                dest_file=basedir + file.newFile,
                                source_detail=file.origInfo,
                                dest_detail=file.newInfo,
                                diff=base64.encodestring(file.data))
            filediff.save()

        return diffset
