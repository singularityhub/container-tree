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


print("####################################################### test_collection")

class TestCollection(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_create_collection_tree(self):
        '''test creation function'''
        print("Testing collection tree creation.")
        from containertree import CollectionTree

        # Initialize a collection tree
        tree = CollectionTree()
        self.assertTrue(isinstance(tree, containertree.tree.CollectionTree))

        # Root node is scratch
        self.assertTrue(tree.root.name == 'scratch')

        # Adding a non-library container will not work
        print("Adding non library to tree will not work.")
        self.assertTrue(tree.update('vanessa/salad', 'vanessa/sregistry') == False)

        # library/ubuntu is a child of scratch
        self.assertTrue(tree.update('scratch', 'library/ubuntu'))
        self.assertTrue(len(tree.root.children) == 1)

        child = tree.root.children[0]
        self.assertTrue(isinstance(child, containertree.tree.node.MultiNode))

        # Create tree that allows non library nodes
        anyTree = CollectionTree(first_level='') 
        self.assertTrue(anyTree.update('vanessa/salad', 'vanessa/sregistry'))

        # The children are indexed by tag (dict)
        self.assertTrue("latest" in anyTree.root.children[0].children)        
        self.assertTrue(anyTree.root.children[0].name == 'vanessa/sregistry')
        self.assertTrue(anyTree.root.children[0].children['latest'][0].name == 'vanessa/salad')


    def test_update_collection_tree(self):
        '''test update functions'''
        print("Testing collection tree update functions")
        from containertree import CollectionTree
        from containertree.utils import get_installdir

        tree = CollectionTree()
        tree.update('continuumio/miniconda3', 'library/debian')
        tree.update('singularityhub/containertree', 'continuumio/miniconda3')
        tree.update('singularityhub/singularity-cli', 'continuumio/miniconda3')
        self.assertTrue(tree.root.children[0].name == 'library/debian')
        self.assertTrue(len(tree.root.children[0].children['latest'][0].children['latest']) == 2)

        # Test trace and order
        trace = tree.trace('continuumio/miniconda3')
        self.assertEqual(len(trace), 3)
        self.assertTrue(trace[0].name == 'scratch')
        self.assertTrue(trace[1].name == 'library/debian')
        self.assertTrue(trace[2].name == 'continuumio/miniconda3')

        # Add custom tag, assert is added as key
        tree.update('continuumio/miniconda3:1.0', 'library/debian')
        self.assertTrue("1.0" in tree.find('continuumio/miniconda3').children)
        tree.update('childof/miniconda3','continuumio/miniconda3:1.0')
        self.assertTrue(len(tree.find('continuumio/miniconda3').children['1.0'])==1)
        self.assertTrue(tree.find('continuumio/miniconda3').children['1.0'][0].name=='childof/miniconda3')

        # Test adding from Dockerfile
        dockerfile = os.path.join(get_installdir(), 'tests', 'Dockerfile')

        # should be invalid to add as uri
        self.assertEqual(tree.update(dockerfile, 'library/ubuntu'), None)

        # It's valid to add as a fromuri 
        self.assertTrue(tree.update('vanessa/sneeze', dockerfile))

        self.assertTrue(tree.root.children[1].name == 'library/golang')
        self.assertTrue(len(tree.root.children[1].children) == 1)
        self.assertTrue('1.11.3-stretch' in tree.root.children[1].children)

        # Test changing parent, should remove from golang
        tree.update('vanessa/sneeze', "library/ubuntu") 
        self.assertTrue(len(tree.root.children[1].children['1.11.3-stretch'])==0)

        # Added to ubuntu
        parent = tree.find('library/ubuntu')
        node = tree.find('vanessa/sneeze')
        self.assertTrue(node in parent.children['latest'])


    def test_query_collection_tree(self):
        '''test query and search functions'''
        print("Testing query and search functions")
        from containertree import CollectionTree

        tree = CollectionTree()
        tree.update('continuumio/miniconda3', 'library/debian')
        tree.update('singularityhub/containertree', 'continuumio/miniconda3')
        tree.update('singularityhub/singularity-cli', 'continuumio/miniconda3:1.0')

        # Both 1.0 and latest should be children
        node = tree.find('continuumio/miniconda3')
        for tag in ['latest', '1.0']:
            self.assertTrue(tag in node.children)        
        
        # Test that iterating works
        self.assertEqual(len([x for x in tree]), 4)

        # Test find on existing node
        node = tree.find('singularityhub/containertree')
        self.assertTrue(node.name == 'singularityhub/containertree')
        node = tree.find('blark/blark')
        self.assertEqual(node, None)

        # Search for a string
        nodes = tree.search('hub')
        self.assertTrue(len(nodes) == 2)

        # Test remove, first with just a tag - the node without tag returned
        node = tree.remove('continuumio/miniconda3', tag='1.0')
        self.assertTrue(node.name == 'continuumio/miniconda3')
        
        # Ensure still in tree with other tags
        node = tree.find('continuumio/miniconda3')
        self.assertTrue('1.0' not in node.children)        

        # Now remove entire node, shouldn't be found.
        node = tree.remove('continuumio/miniconda3')
        self.assertTrue(node.name == 'continuumio/miniconda3')
        node = tree.find('continuumio/miniconda3')
        self.assertEqual(node, None)


    def test_collection_tree_fs(self):
        '''test collection filesystems'''
        print("Testing query and search functions")
        from containertree import CollectionTree

        tree = CollectionTree()
        tree.update('continuumio/miniconda3', 'library/debian')
        tree.update('singularityhub/containertree', 'continuumio/miniconda3')
        tree.update('singularityhub/singularity-cli', 'continuumio/miniconda3:1.0')

        nodes = tree.get_nodes()
        print(nodes)
        self.assertTrue(len(nodes) == 4)
        paths = tree.get_paths()

        # Paths also returns the root node, nodes doesn't
        self.assertTrue(len(paths) == 5)
        self.assertTrue('/scratch/library/debian/.latest/continuumio/miniconda3' in paths)

        # Test paths with a prefix
        paths = tree.get_paths(tag_prefix="TAG_")
        self.assertTrue('/scratch/library/debian/TAG_latest/continuumio/miniconda3' in paths)

        # Test only returning leaf nodes
        paths = tree.paths(leaves_only=True)
        self.assertTrue('/scratch') not in paths


if __name__ == '__main__':
    unittest.main()
