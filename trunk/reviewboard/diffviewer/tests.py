import os
import unittest

import reviewboard.diffviewer.parser as diffparser
import diffutils


class MyersDifferTest(unittest.TestCase):
    def diff(self):
        self.__test_diff(["1", "2", "3"],
                         ["1", "2", "3"],
                         [("equal", 0, 0, 3, 3),])

        self.__test_diff(["1", "2", "3"],
                         [],
                         [("delete", 0, 0, 3, 0),])

        self.__test_diff("1\n2\n3\n",
                         "0\n1\n2\n3\n",
                         [("insert", 0, 0, 0, 1),
                          ("equal",  0, 1, 3, 3)])

        self.__test_diff("1\n2\n3\n7\n",
                         "1\n2\n4\n5\n6\n7\n",
                         [("equal",   0, 0, 2, 2),
                          ("replace", 2, 2, 1, 1),
                          ("insert",  3, 3, 0, 2),
                          ("equal",   3, 5, 1, 1)])


    def __test_diff(self, a, b, expected):
        opcodes = list(diffutils.MyersDiffer(a, b).get_opcodes())
        self.failUnless(opcodes == expected)


class DiffParserTest(unittest.TestCase):
    PREFIX = 'diffviewer/testdata'

    def diff(self, options=''):
        f = os.popen('diff -rN -x .svn %s %s/orig_src %s/new_src' %
                     (options, self.PREFIX, self.PREFIX))
        data = f.read()
        f.close()
        return data

    def compareDiffs(self, files, testdir):
        self.failUnless(len(files) == 3)
        for file in files:
            f = open("%s/diffs/%s/%s.diff" %
                     (self.PREFIX, testdir, os.path.basename(file.newFile)))
            data = f.read()
            f.close()

            self.failUnless(file.origFile.startswith("%s/orig_src/" %
                                                     self.PREFIX))
            self.failUnless(file.newFile.startswith("%s/new_src/" %
                                                    self.PREFIX))
            self.assertNotEquals(file.origInfo, "")
            self.assertNotEquals(file.newInfo, "")

            self.assertNotEquals(file.data, "")
            self.assertNotEquals(data, "")

            # Can't really compare the strings because of timestamps...

    def testUnifiedDiff(self):
        """Testing parse on a unified diff"""
        data = self.diff('-u')
        files = diffparser.parse(data)
        self.compareDiffs(files, "unified")

    def testContextDiff(self):
        """Testing parse on a context diff"""
        data = self.diff('-c')
        files = diffparser.parse(data)
        self.compareDiffs(files, "context")

    def testPatch(self):
        """Testing patching"""

        def get_file(*relative):
            f = open(os.path.join(*tuple([self.PREFIX] + list(relative))))
            data = f.read()
            f.close()
            return data

        file = 'foo.c'

        old = get_file('orig_src', file)
        new = get_file('new_src', file)
        diff = get_file('diffs', 'unified', 'foo.c.diff')

        patched = diffutils.patch(diff, old, file)
        self.assertEqual(patched, new)

        diff = get_file('diffs', 'unified', 'README.diff')
        self.assertRaises(Exception, lambda: diffutils.patch(diff, old, file))

    def testInterline(self):
        """Testing inter-line diffs"""

        def deepEqual(A, B):
            typea, typeb = type(A), type(B)
            self.assertEqual(typea, typeb)
            if typea is tuple or typea is list:
                for a, b in map(None, A, B):
                    deepEqual(a, b)
            else:
                self.assertEqual(A, B)

        deepEqual(diffutils.get_line_changed_regions(None, None),
                  (None, None))

        old = 'submitter = models.ForeignKey(Person, verbose_name="Submitter")'
        new = 'submitter = models.ForeignKey(User, verbose_name="Submitter")'
        regions = diffutils.get_line_changed_regions(old, new)
        deepEqual(regions, ([(30, 36)], [(30, 34)]))


        old = '-from reviews.models import ReviewRequest, Person, Group'
        new = '+from .reviews.models import ReviewRequest, Group'
        regions = diffutils.get_line_changed_regions(old, new)
        deepEqual(regions, ([(0, 1), (6, 6), (43, 51)],
                            [(0, 1), (6, 7), (44, 44)]))

        old = 'abcdefghijklm'
        new = 'nopqrstuvwxyz'
        regions = diffutils.get_line_changed_regions(old, new)
        deepEqual(regions, (None, None))