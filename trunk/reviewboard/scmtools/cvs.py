import re
import subprocess

from reviewboard.scmtools.core import SCMError, FileNotFoundError, \
                                      SCMTool, HEAD, PRE_CREATION
from reviewboard.diffviewer.parser import DiffParser, DiffParserError

class CVSTool(SCMTool):
    regex_rev = re.compile(r'^.*?(\d+(\.\d+)+)\r?$')

    def __init__(self, repository):
        try:
            self.repopath = repository.path.split(':')[1]
            self.CVSROOT = ":pserver:%s@%s" % (repository.username, repository.path)
        except IndexError:
            self.repopath = self.CVSROOT = repository.path
        self.client = CVSClient(self.CVSROOT)

        SCMTool.__init__(self, repository)

    def get_file(self, path, revision=HEAD):
        if not path:
            raise FileNotFoundError(path, revision)

        return self.client.cat_file(path, revision)

    def parse_diff_revision(self, file_str, revision_str):
        if revision_str == "PRE-CREATION":
            return file_str, PRE_CREATION

        m = self.regex_rev.match(revision_str)
        if not m:
            raise SCMError("Unable to parse diff revision header '%s'" %
                           revision_str)
        return file_str, m.group(1)

    def get_diffs_use_absolute_paths(self):
        return True

    def get_fields(self):
        return ['diff_path']

    def getParser(self, data):
        return CVSDiffParser(data, self.repopath)

class CVSDiffParser(DiffParser):
    """
        This class is able to parse diffs created with CVS.
    """

    regex_small = re.compile('^RCS file: (.+)$')

    def __init__(self, data, repo):
        DiffParser.__init__(self, data)
        self.regex_full = re.compile('^RCS file: %s/(.*),v$' % re.escape(repo))

    def _parseRevisionInfo(self, linenum, file):
        m = self.regex_full.match(self.lines[linenum-3])
        if not m:
            m = self.regex_small.match(self.lines[linenum-2])

        if m:
            filename = m.group(1)
        else:
            raise DiffParserError('Unable to find RCS line around line "%d"' % linenum)

        try:
            file.origFile, file.origInfo = self.lines[linenum].split(None, 2)[1:]
            file.newFile,  file.newInfo  = self.lines[linenum + 1].split(None, 2)[1:]
            if file.origFile == '/dev/null':
                file.origFile, file.origInfo = (file.newFile, 'PRE-CREATION')
            else:
                file.origFile = filename
        except ValueError:
            raise DiffParserError("The diff file is missing revision information")


class CVSClient:
    def __init__(self, repository):
        self.repository = repository

    def cat_file(self, filename, revision):
        p = subprocess.Popen(['cvs', '-d', self.repository, 'checkout',
                              '-r', str(revision), '-p', filename],
                             stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                             close_fds=True)
        contents = p.stdout.read()
        errmsg = p.stderr.read()
        failure = p.wait()

        if failure:
            raise FileNotFoundError(errmsg)
        return contents
