#!/usr/bin/env python
#
# Copyright (C) 2018 Vanessa Sochat.
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

from glob import glob
import json
import os


class ContainerTree(object):

    def __init__(self, filelist, folder_sep='/'):
        '''construct a container tree from a container-diff
           export of flies. See "load" for the logic to construct
           the tree.

           Parameters
           ==========
           filelist: the json export (files.json) of a tar
           folder_sep: the character that separates path names

        '''

        # The root node is the root of the fs
        self.root = Node('', {'size': 0})
        
        # The character that separates folder/files
        self.folder_sep = folder_sep

        # Count the nodes
        self.count = 1

        # Sets self.data and builds self.tree
        self.load(filelist)


    def load(self, filelist):
        ''' Load a set of files from json into the container tree.
            This means:
 
            1/ Reading in the data file
            2/ Creating a Node for each path portion
            3/ Assembling the nodes into the tree
        '''

        # Read in the raw data file
        with open(filelist) as filey:
            data = json.load(filey)
        
        # Data is stored at 0['Analysis']
        self.data = data[0]['Analysis'] 
        self._make_tree()

    def __str__(self):
        return "ContainerTree<%s>" % self.count
    def __repr__(self):
        return "ContainerTree<%s>" % self.count

    
    def _make_tree(self):
        '''construct the tree from the loaded data (self.data)
           we should already have a root defined.
        '''

        for attrs in self.data:

            # The starting node is the root node
            node = self.root

            filepaths = attrs['Name'].split(self.folder_sep)
        
            # Add the path to the correct spot in the tree    
            for filepath in filepaths:

                found = False

                # We are at the root
                if filepath == node.filepath:
                    found = True             

                else:

                    # Search in present node
                    for child in node.children:

                        # We found the parent
                        if child.filepath == filepath:

                            # Keep track of how many we have
                            child.counter += 1

                            # update node to be child that was found
                            node = child
                            found = True
                            break


                # If not found, add new node (child)
                if not found:
                    new_node = Node(filepath, attrs)
                    self.count +=1

                    # Add to the root (or the last where found)
                    node.children.append(new_node)

                    # Keep working down the tree
                    node = new_node

            # The last in the list is the leaf (file)
            node.leaf = True


    def find(self, filepath):
        '''find a prefix in the tree, meaning the beginning of  path
           Returns how many paths are under the prefix path.
        '''
 
        # We always start at the root  
        node = self.root

        # No children, no search
        if len(node.children) == 0:

            # They were looking for the root
            if node.filepath == filepath:
                return node

            return
        
        filepaths = filepath.split(self.folder_sep)
        assembled='/'.join(filepaths)

        # Look for the path in the tree
        for filepath in filepaths:

            if filepath == node.filepath:

                # if we have the complete assembled path, return node
                if filepath == assembled:
                    return node

            else:

                # Try and find the filepath in the tree
                for child in node.children:
                    if child.filepath == filepath:
                        node = child

                        # If the name is what we are looking for, return Node
                        if node.Name == assembled:
                            return node
                        break



class Node(object):
    
    def __init__(self, filepath, attrs):
        ''' a Node is a node in the Trie, meaning that
            it stores a word (a folder or file) and some
            number of children from it. If a Node is a leaf 
            this coincides with the end of a path.

            Parameters
            ==========
            filepath: the name of the folder or file
            attrs: a dict of attributes to give to the node

        '''
        self.filepath = filepath
        self.children = []
        self.set_attributes(attrs)
        
        # The end of the file path
        self.leaf = False

        # How many times this character appeared in the addition process
        self.counter = 1

    def __str__(self):
        return "Node<%s>" % self.filepath
    def __repr__(self):
        return "Node<%s>" % self.filepath
    
    def set_attributes(self, attrs):
        '''Set a variable number of attributes, likely
           size of the file/folder

           Parameters
           ==========
           attrs: a dict of key,value attribute pairs

        '''

        for name, value in attrs.items():
            self.__setattr__(name, value)


# Helper Functions

def find_rawdata(database):

    filelist = {}
    packages = {}
    
    for root, dirs, files in os.walk(database, topdown=False):
        for name in files:
            fullpath = os.path.join(root, name)
            uid = fullpath.replace(data,'')
            if name == 'packages.json':
                packages[uid] = fullpath
            elif name == "files.json":
                filelist[uid] = fullpath

    return packages, filelist


if __name__ == "__main__":

    # Path to database of container-api 
    database = "/home/vanessa/Documents/Dropbox/Code/Google/container-api/data/singularityhub"

    # Container data files
    packages, files = find_rawdata(database)
    for uid, filelist in files.items():
        tree = ContainerTree(filelist)

    # To find a node based on path
    tree.find('/etc/ssl')
    # Node<ssl>

