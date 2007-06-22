import os
import nose
import unittest

from django.test import TestCase as DjangoTestCase

from reviewboard.scmtools.core import SCMException, FileNotFoundException, \
                                      Revision, HEAD, PRE_CREATION, \
                                      ChangeSet
from reviewboard.scmtools.models import Repository, Tool

class CoreTests(unittest.TestCase):
    """Tests for the scmtools.core module"""

    def testGetTool(self):
        """Testing tool instantiation"""
        return

        # XXX This needs to be updated to use the new methods of loading
        #     tools.
        #tool = get_tool('reviewboard.scmtools.svn.SVNTool')
        #self.assertEqual(tool.__class__, SVNTool)

        #tool = get_tool('reviewboard.scmtools.perforce.PerforceTool')
        #self.assertEqual(tool.__class__, PerforceTool)

        #self.assertRaises(ImproperlyConfigured,
        #                  lambda: get_tool('blah.blah'))

        #self.assertRaises(ImproperlyConfigured,
        #                  lambda: get_tool('reviewboard.scmtools.svn.Foo'))


    def testInterface(self):
        """Testing basic scmtools.core API"""

        # Empty changeset
        cs = ChangeSet()
        self.assertEqual(cs.changenum, None)
        self.assertEqual(cs.summary, '')
        self.assertEqual(cs.description, '')
        self.assertEqual(cs.branch, '')
        self.assert_(len(cs.bugs_closed) == 0)
        self.assert_(len(cs.files) == 0)


class SubversionTests(unittest.TestCase):
    """Unit tests for subversion."""

    def setUp(self):
        svn_repo_path = os.path.join(os.path.dirname(__file__),
                                     'testdata/svn_repo')
        self.repository = Repository(name='Subversion SVN',
                                     path='file://' + svn_repo_path,
                                     tool=Tool.objects.get(name='Subversion'))

        try:
            self.tool = self.repository.get_scmtool()
        except ImportError:
            raise nose.SkipTest

    def testGetFile(self):
        """Testing SVNTool.get_file"""
        expected = 'include ../tools/Makefile.base-vars\nNAME = misc-docs\n' + \
                   'OUTNAME = svn-misc-docs\nINSTALL_DIR = $(DESTDIR)/usr/s' + \
                   'hare/doc/subversion\ninclude ../tools/Makefile.base-rul' + \
                   'es\n'

        # There are 3 versions of this test in order to get 100% coverage of
        # the svn module.
        rev = Revision('2')
        file = 'trunk/doc/misc-docs/Makefile'

        self.assertEqual(self.tool.get_file(file, rev), expected)

        self.assertEqual(self.tool.get_file('/' + file, rev), expected)

        self.assertEqual(self.tool.get_file(self.repository.path + '/' + file, rev),
                         expected)


        self.assert_(self.tool.file_exists('trunk/doc/misc-docs/Makefile'))
        self.assert_(not self.tool.file_exists('trunk/doc/misc-docs/Makefile2'))

        self.assertRaises(FileNotFoundException,
                          lambda: self.tool.get_file(''))

        self.assertRaises(FileNotFoundException,
                          lambda: self.tool.get_file('hello',
                                                     PRE_CREATION))

    def testRevisionParsing(self):
        """Testing revision number parsing"""
        self.assertEqual(self.tool.parse_diff_revision('', '(working copy)')[1],
                         HEAD)
        self.assertEqual(self.tool.parse_diff_revision('', '(revision 0)')[1],
                         PRE_CREATION)

        self.assertEqual(self.tool.parse_diff_revision('', '(revision 1)')[1],
                         '1')
        self.assertEqual(self.tool.parse_diff_revision('', '(revision 23)')[1],
                         '23')

        self.assertEqual(self.tool.parse_diff_revision('',
            '2007-06-06 15:32:23 UTC (rev 10958)')[1], '10958')

        self.assertRaises(SCMException,
                          lambda: self.tool.parse_diff_revision('', 'hello'))

    def testInterface(self):
        """Testing basic SVNTool API"""
        self.assertEqual(self.tool.get_diffs_use_absolute_paths(), False)

        self.assertRaises(NotImplementedError,
                          lambda: self.tool.get_changeset(1))

        self.assertRaises(NotImplementedError,
                          lambda: self.tool.get_pending_changesets(1))


class PerforceTests(unittest.TestCase):
    """Unit tests for perforce.

       This uses the open server at public.perforce.com to test various
       pieces.  Because we have no control over things like pending
       changesets, not everything can be tested.
       """

    def setUp(self):
        self.repository = Repository(name='Perforce.com',
                                     path='public.perforce.com:1666',
                                     tool=Tool.objects.get(name='Perforce'))

        try:
            self.tool = self.repository.get_scmtool()
        except ImportError:
            raise nose.SkipTest

    def testChangeset(self):
        """Testing PerforceTool.get_changeset"""

        desc = self.tool.get_changeset(157)
        self.assertEqual(desc.changenum, 157)
        self.assertEqual(hash(desc.description), -209144366)

        expected_files = [
            '//public/perforce/api/python/P4Client/P4Clientmodule.cc',
            '//public/perforce/api/python/P4Client/p4.py',
            '//public/perforce/api/python/P4Client/review.py',
            '//public/perforce/python/P4Client/P4Clientmodule.cc',
            '//public/perforce/python/P4Client/p4.py',
            '//public/perforce/python/P4Client/review.py',
        ]
        for file, expected in map(None, desc.files, expected_files):
            self.assertEqual(file, expected)

        self.assertEqual(hash(desc.summary), 588429333)

    def testGetFile(self):
        """Testing PerforceTool.get_file"""

        file = self.tool.get_file('//public/perforce/api/python/P4Client/p4.py',
                                  1)
        self.assertEqual(hash(file), 1392492355)


class VMWareTests(DjangoTestCase):
    """Tests for VMware specific code"""
    fixtures = ['vmware.json']

    def setUp(self):
        self.repository = Repository(name='VMware Test',
                                     path='perforce.eng.vmware.com:1666',
                                     tool=Tool.objects.get(name='VMware Perforce'))

        try:
            self.tool = self.repository.get_scmtool()
        except ImportError:
            raise nose.SkipTest

    def testParse(self):
        """Testing VMwarePerforceTool.parse_change_desc"""

        file = open(os.path.join(os.path.dirname(__file__), 'testdata',
                                 'vmware.changeset'), 'r')
        data = file.read().split('\n')
        file.close()

        changeset = self.tool.parse_change_desc(data, 123456)
        self.assertEqual(changeset.summary, "Emma")
        self.assertEqual(hash(changeset.description), 315618127)
        self.assertEqual(changeset.changenum, 123456)
        self.assertEqual(changeset.testing_done, "- Read a book.")

        self.assertEqual(len(changeset.bugs_closed), 1)
        self.assertEqual(changeset.bugs_closed[0], '128700')

        expected_files = [
            '//depot/bora/hosted07-rel/foo.cc',
            '//depot/bora/hosted07-rel/foo.hh',
            '//depot/bora/hosted07-rel/bar.cc',
            '//depot/bora/hosted07-rel/bar.hh',
        ]
        for file, expected in map(None, changeset.files, expected_files):
            self.assertEqual(file, expected)

        self.assertEqual(changeset.branch,
                         'hosted07-rel &rarr; hosted07 &rarr; bfg-main (manual)')


    def testParseSingleLineDesc(self):
        """
        Testing VMwarePerforceTool.parse_change_desc with a single line
        description.
        """
        file = open(os.path.join(os.path.dirname(__file__), 'testdata',
                                 'vmware-single-line-desc.changeset'), 'r')
        data = file.read().split('\n')
        file.close()

        changeset = self.tool.parse_change_desc(data, 1234567)
        self.assertEqual(changeset.summary,
                         "There is only a single line in this changeset description.")
        self.assertEqual(changeset.description,
                         "There is only a single line in this changeset description.")
        self.assertEqual(changeset.changenum, 1234567)
        self.assertEqual(changeset.testing_done, "")

        self.assertEqual(len(changeset.bugs_closed), 0)

        expected_files = [
            '//depot/qa/foo/bar',
        ]
        for file, expected in map(None, changeset.files, expected_files):
            self.assertEqual(file, expected)

    def testParseMultiLineSummary(self):
        """
        Testing VMwarePerforceTool.parse_change_desc with a summary spanning
        multiple lines.
        """
        file = open(os.path.join(os.path.dirname(__file__), 'testdata',
                                 'vmware-phil-is-crazy.changeset'), 'r')
        data = file.read().split('\n')
        file.close()

        changeset = self.tool.parse_change_desc(data, 123456)
        self.assertEqual(changeset.summary, "Changes: Emma")

        self.assertEqual(changeset.branch, 'bfg-main')