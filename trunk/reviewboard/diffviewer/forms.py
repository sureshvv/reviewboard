import os

from django import newforms as forms

from reviewboard.diffviewer.diffutils import DEFAULT_DIFF_COMPAT_VERSION
from reviewboard.diffviewer.models import DiffSet, FileDiff
from reviewboard.scmtools.models import Repository
import reviewboard.scmtools as scmtools
from scmtools import PRE_CREATION

class EmptyDiffError(ValueError):
    pass


class UploadDiffForm(forms.Form):
    repositoryid = forms.IntegerField(required=True, widget=forms.HiddenInput)
    # XXX: it'd be really nice to have "required" for these things be
    # dependent on the scmtool for the repository
    basedir = forms.CharField(required=False)
    path = forms.CharField(widget=forms.FileInput())

    # Extensions used for intelligent sorting of header files
    # before implementation files.
    HEADER_EXTENSIONS = ["h", "H", "hh", "hpp", "hxx", "h++"]
    IMPL_EXTENSIONS   = ["c", "C", "cc", "cpp", "cxx", "c++", "m", "mm", "M"]

    def create(self, file, diffset_history=None):
        # Parse the diff
        repository = Repository.objects.get(pk=self.cleaned_data['repositoryid'])
        tool = repository.get_scmtool()
        files = tool.getParser(file["content"]).parse()

        if len(files) == 0:
            raise EmptyDiffError

        # Check that we can actually get all these files.
        if tool.get_diffs_use_absolute_paths():
            basedir = ''
        else:
            basedir = str(self.cleaned_data['basedir'])

        for f in files:
            f2, revision = tool.parse_diff_revision(f.origFile, f.origInfo)
            filename = os.path.join(basedir, f2)

            # FIXME: this would be a good place to find permissions errors
            if revision != PRE_CREATION and \
               not tool.file_exists(filename, revision):
                raise scmtools.FileNotFoundError(filename, revision)

            f.origFile = filename
            f.origInfo = revision

        diffset = DiffSet(name=file["filename"], revision=0,
                          history=diffset_history,
                          diffcompat=DEFAULT_DIFF_COMPAT_VERSION)
        diffset.repository = repository
        diffset.save()

        # Sort the files so that header files come before implementation.
        files.sort(cmp=self._compare_files, key=lambda f: f.origFile)

        for f in files:
            filediff = FileDiff(diffset=diffset,
                                source_file=f.origFile,
                                dest_file=os.path.join(basedir, f.newFile),
                                source_revision=str(f.origInfo),
                                dest_detail=f.newInfo,
                                diff=f.data,
                                binary=f.binary)
            filediff.save()

        return diffset

    def _compare_files(self, filename1, filename2):
        """
        Compares two files, giving precedence to header files over source
        files. This allows the resulting list of files to be more
        intelligently sorted.
        """
        if filename1.find('.') != -1 and filename2.find('.') != -1:
            basename1, ext1 = filename1.rsplit('.')
            basename2, ext2 = filename2.rsplit('.')

            if basename1 == basename2:
                if ext1 in self.HEADER_EXTENSIONS and \
                   ext2 in self.IMPL_EXTENSIONS:
                    return -1
                elif ext1 in self.IMPL_EXTENSIONS and \
                     ext2 in self.HEADER_EXTENSIONS:
                    return 1

        return cmp(filename1, filename2)