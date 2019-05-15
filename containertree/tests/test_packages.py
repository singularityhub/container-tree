#!/usr/bin/python

# Copyright (C) 2019 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

import unittest
import containertree
import tempfile
import shutil
import json
import os


print("######################################################### test_packages")

class TestPackages(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_create_apt_tree(self):
        '''test creation of APT package tree function'''
        print("Testing package apt tree creation.")
        from containertree.tree import ContainerAptTree
 
        # Initilize a tree with packages from a container
        apt = ContainerAptTree('singularityhub/sregistry-cli')

        nodes = apt.trace('wget')
        self.assertTrue(len(nodes)==3)
        self.assertTrue(apt.find('wget').label == 'wget')
        self.assertTrue(len(apt.search('bin'))==5)

    def test_create_pip_tree(self):
        '''test creation of pip package tree function'''
        print("Testing package pip tree creation.")
        from containertree.tree import ContainerPipTree
 
        # Initilize a tree with packages from a container
        pip = ContainerPipTree('vanessa/expfactory-builder')
        self.assertTrue(pip.count, 9)

        nodes = pip.trace('pyaml')
        self.assertTrue(len(nodes)==3)
        self.assertTrue(pip.find('pyaml').label == 'pyaml')

        # Check regular expression searching
        self.assertTrue(len(pip.search('(aml|AML)'))==2)

    def test_package_tree_tags(self):
        '''test creation of pip package tree function'''
        print("Testing package pip tree creation.")
        from containertree.tree import ContainerAptTree
 
        apt = ContainerAptTree('singularityhub/sregistry-cli',
                               tag='singularityhub/sregistry-cli')

        self.assertTrue('singularityhub/sregistry-cli' in apt.root.tags)
        wget = apt.find('wget')
        self.assertTrue('singularityhub/sregistry-cli' in wget.tags)

        apt.update('library/debian', tag='library/debian')
        find = apt.find('findutils')
        self.assertTrue('singularityhub/sregistry-cli' in find.tags)
        self.assertTrue('library/debian' in find.tags)

    def test_export_apt_data(self):
        '''test export of data for apt package trees'''
        print("Testing package data export.")
        from containertree.tree import ContainerAptTree

        apt = ContainerAptTree('singularityhub/sregistry-cli',
                               tag='singularityhub/sregistry-cli')
        apt.update('library/debian', tag='library/debian')
        apt.update('library/ubuntu', tag='library/ubuntu')

        df = apt.export_vectors()
        self.assertTrue('adduser' in df.columns.tolist())
        self.assertTrue('library/debian' in df.index.tolist())
        df = df.fillna(0)

        # Only include subset of tags
        df = apt.export_vectors(include_tags=['library/debian'])
        self.assertTrue('library/ubuntu' not in df.index.tolist())

        # Try skipping a tag for a container
        df = apt.export_vectors(skip_tags=['library/debian'])
        self.assertTrue('library/debian' not in df.index.tolist())

        # Regular expression
        df = apt.export_vectors(regexp_tags="^library")
        self.assertTrue('singularityhub/sregistry-cli' not in df.index.tolist())
         
        # Include package versions
        df = apt.export_vectors(include_versions=True)
        addusers = [x for x in df.columns.tolist() if x.startswith('adduser-')]
        self.assertTrue(len(addusers)==2)

    def test_export_pip_data(self):
        '''test export of data for pip package trees'''
        print("Testing package data export.")
        from containertree.tree import ContainerAptTree

        from containertree import ContainerPipTree
        pip = ContainerPipTree('singularityhub/container-tree',
        tag='singularityhub/container-tree')
        df = pip.export_vectors()
        self.assertTrue('singularityhub/container-tree' in df.index.tolist())
        self.assertTrue('pip' in df.columns.tolist())

        # check versions
        df = pip.export_vectors(include_versions=True)
        six = [x for x in df.columns.tolist() if x.startswith('six-')]
        self.assertTrue(len(six) == 1)

if __name__ == '__main__':
    unittest.main()
