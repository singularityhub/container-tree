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


print("######################################################## test_container")

class TestContainer(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_create_container_tree(self):
        '''test creation of filesystem tree function'''
        print("Testing collection tree creation.")
        from containertree import ContainerFileTree
        import requests

        # Path to database of container-api 
        database = "https://singularityhub.github.io/api/files"
        containers = requests.get(database).json()
        entry = containers[0]  

        # Google Container Diff Analysis Type "File" Structure
        tree = ContainerFileTree(entry['url'])

        # To find a node based on path
        node = tree.find('/etc/ssl')
        self.assertTrue(isinstance(node, containertree.tree.node.Node))
        self.assertTrue(node.name == '/etc/ssl')

        # Trace a path, returning all nodes
        trace = tree.trace('/etc/ssl')
        self.assertEqual(len(trace), 3)
        names = [x.name for x in trace]

        # [Node<>, Node<etc>, Node<ssl>]
        self.assertEqual(names[0], '/')
        self.assertEqual(names[1], '/etc')
        self.assertEqual(names[2], '/etc/ssl')
          
        # Test node counter
        self.assertEqual(tree.get_count('/etc/ssl'), 1)     

        # Insert a new node path
        self.assertEqual(tree.find('/etc/tomato'), None)
        tree.insert('/etc/tomato')
        self.assertTrue(tree.find('/etc/tomato') != None)

        trace = tree.trace('/etc/tomato')
        self.assertEqual(len(trace), 3)
        names = [x.name for x in trace]

        # [Node<>, Node<etc>, Node<tomato>]
        self.assertEqual(names[0], '/')
        self.assertEqual(names[1], '/etc')
        self.assertEqual(names[2], '/etc/tomato')

        # Get count of a node
        self.assertEqual(tree.get_count('/etc/tomato'), 1)
        tree.insert('/etc/tomato')
        self.assertEqual(tree.get_count('/etc/tomato'), 2)

        # Update the tree with a second container!
        self.assertEqual(tree.get_count('/etc/ssl'), 1)
        new_entry = containers[1]
        tree.update(new_entry['url'])

        # Test node counter
        self.assertEqual(tree.get_count('/etc/ssl'), 2)   

    def test_create_from_uri(self):
        '''test creation of tree from unique resource identifier'''
        from containertree import ContainerFileTree
        print("Testing creation from unique resource identifier.")

        tree = ContainerFileTree("vanessa/salad")

        self.assertTrue(tree.find('/code/salad') != None)
        bins = tree.search('bin')
        self.assertEqual(len(bins), 5)

    def test_container_tree_tags(self):
        '''test adding tags to a container tree'''
        print("Testing creation with tags.")

        from containertree import ContainerFileTree
        import requests

        database = "https://singularityhub.github.io/api/files"
        containers = requests.get(database).json()

        tree = ContainerFileTree("vanessa/salad")
        entry1 = containers[0]  
        entry2 = containers[1]

        tag1=entry1['collection']
        #'54r4/sara-server-vre'
        tag2=entry2['collection']
        #'A33a/sjupyter'

        tree = ContainerFileTree(entry1['url'], tag=tag1)

        self.assertTrue('54r4/sara-server-vre' in tree.root.tags)

        # Update the container tree with the second container
        tree.update(entry2['url'], tag=tag2)
        self.assertTrue('54r4/sara-server-vre' in tree.root.tags)
        self.assertTrue('A33a/sjupyter' in tree.root.tags)

        # calculate similarity between tags
        tags = tree.root.tags
        scores = tree.similarity_score(tree.root.tags)

        # {'diff': 44185,
        # 'same': 12201,
        # 'score': 0.21638349945021815,
        # 'tags': ['54r4/sara-server-vre', 'A33a/sjupyter'],
        # 'total': 56386}

        self.assertEqual(scores['diff'], 44185)
        self.assertEqual(scores['same'], 12201)


if __name__ == '__main__':
    unittest.main()
