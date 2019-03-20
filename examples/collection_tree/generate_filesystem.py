#
# Copyright (C) 2019 Vanessa Sochat.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
# License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from containertree import CollectionTree
import xattr
import sys
import os


if not os.path.exists('/container-collection-tree-final.pkl'):
    print('Add /container-collection-tree-final.pkl, creating dummy example.')
    tree = pickle.load(open('/container-collection-tree-final.pkl','rb'))

else:

    # Initialize a collection tree
    tree = CollectionTree()
    tree.update('continuumio/miniconda3', 'library/debian')
    tree.update('vanessa/pancakes', 'library/debian')
    tree.update('singularityhub/containertree', 'continuumio/miniconda3')
    tree.update('singularityhub/singularity-cli', 'continuumio/miniconda3')
    tree.update('continuumio/miniconda3:1.0', 'library/debian')
    tree.update('childof/miniconda3','continuumio/miniconda3:1.0')
    tree.update('continuumio/miniconda3', 'library/python')
    
print('Creating paths and adding count metadata...')
for path in tree.get_paths(tag_prefix='tag-', leaves_only=True):
    print('mkdir -p %s' % path)

        # Create the attribute
        attribute = xattr.xattr(path)

        os.makedirs(path)

        # Solaris 11 and forward contain system attributes (file flags) in
        # extended attributes present on all files, so cons them up into a
        # comparison dict.
        d = {}
        if sys.platform == 'sunos5' and 'SUNWattr_ro' in x:
            d['SUNWattr_ro'] = x['SUNWattr_ro']
            d['SUNWattr_rw'] = x['SUNWattr_rw']

        # SELinux systems use an attribute which must be accounted for
        if sys.platform.startswith('linux') and 'security.selinux' in x:
            d['security.selinux'] = x['security.selinux']

        self.assertEqual(list(x.keys()), list(d.keys()))
        self.assertEqual(list(x.list()), list(d.keys()))
        self.assertEqual(dict(x), d)

        x['user.sopal'] = b'foo'
        x['user.sop.foo'] = b'bar'
        x[u'user.\N{SNOWMAN}'] = b'not a snowman'
        del x

        x = xattr.xattr(self.tempfile)
        attrs = set(x.list())
        self.assertTrue('user.sopal' in x)
        self.assertTrue(u'user.sopal' in attrs)
        self.assertEqual(x['user.sopal'], b'foo')
        self.assertTrue('user.sop.foo' in x)
        self.assertTrue(u'user.sop.foo' in attrs)
        self.assertEqual(x['user.sop.foo'], b'bar')
        self.assertTrue(u'user.\N{SNOWMAN}' in x)
        self.assertTrue(u'user.\N{SNOWMAN}' in attrs)
        self.assertEqual(x[u'user.\N{SNOWMAN}'],
                         b'not a snowman')

        del x[u'user.\N{SNOWMAN}']
        del x['user.sop.foo']
        del x

        x = xattr.xattr(self.tempfile)
        self.assertTrue('user.sop.foo' not in x)

    def test_setxattr_unicode_error(self):
        x = xattr.xattr(self.tempfile)
        def assign():
            x['abc'] = u'abc'
        self.assertRaises(TypeError, assign)

        if sys.version_info[0] >= 3:
            msg = "Value must be bytes, str was passed."
        else:
            msg = "Value must be bytes, unicode was passed."

        try:
            assign()
        except TypeError:
            e = sys.exc_info()[1]
            self.assertEqual(str(e), msg)

    def test_symlink_attrs(self):
        symlinkPath = self.tempfilename + '.link'
        os.symlink(self.tempfilename, symlinkPath)
        try:
            symlink = xattr.xattr(symlinkPath, options=xattr.XATTR_NOFOLLOW)
            realfile = xattr.xattr(self.tempfilename)
            try:
                symlink['user.islink'] = b'true'
            except IOError:
                # Solaris, Linux don't support extended attributes on symlinks
                raise unittest.SkipTest("XATTRs on symlink not allowed"
                                        " on filesystem/platform")
            self.assertEqual(dict(realfile), {})
            self.assertEqual(symlink['user.islink'], b'true')
        finally:
            os.remove(symlinkPath)


class TestFile(TestCase, BaseTestXattr):
    def setUp(self):
        self.tempfile = NamedTemporaryFile(dir=self.TESTDIR)
        self.tempfilename = self.tempfile.name

    def tearDown(self):
        self.tempfile.close()


class TestDir(TestCase, BaseTestXattr):
    def setUp(self):
        self.tempfile = mkdtemp(dir=self.TESTDIR)
        self.tempfilename = self.tempfile

    def tearDown(self):
        os.rmdir(self.tempfile)


try:
    # SkipTest is only available in Python 2.7+
    unittest.SkipTest
except AttributeError:
    pass
else:
    class TestFileWithSurrogates(TestFile):
        def setUp(self):
            if sys.platform not in ('linux', 'linux2'):
                raise unittest.SkipTest('Files with invalid encoded names are only supported under linux')
            if sys.version_info[0] < 3:
                raise unittest.SkipTest('Test is only available on Python3') # surrogateescape not avail in py2
            self.tempfile = NamedTemporaryFile(prefix=b'invalid-\xe9'.decode('utf8','surrogateescape'), dir=self.TESTDIR)
            self.tempfilename = self.tempfile.name
