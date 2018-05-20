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

import os
import requests
import json

class ContainerTree(object):

    def __init__(self, filelist, folder_sep='/'):
        '''construct a container tree from a container-diff
           export of flies. See "load" for the logic to construct
           the tree.

           Parameters
           ==========
           filelist: the json export (files.json) of a tar, can be https
           folder_sep: the character that separates path names

        '''

        # The root node is the root of the fs
        self.root = Node('', {'size': 0})
        self.data = None
        
        # The character that separates folder/files
        self.folder_sep = folder_sep

        # Count the nodes
        self.count = 1

        # Sets self.data and builds self.tree
        self.load(filelist)

        # If data is loaded, make the tree
        if self.data:
            self._make_tree()


# Loading Functions
    
    def _load_http(self, url):
        '''load json from http. We assume it to be json because other formats
           aren't supported yet
        '''
        response = requests.get(url)

        if response.status_code == 200:
            try:
                self.data = response.json()
            except json.JSONDecodeError:
                print('The web address must be for json!')
                sys.exit(1)


    def _load_json(self, filelist):
        '''read the filelist from a json file
        '''

        # Read in the raw data file
        with open(filelist) as filey:
            self.data = json.load(filey)

    def load(self, filelist):
        ''' Load a set of files from json into the container tree.
            This means:
 
            1/ Reading in the data file
            2/ Creating a Node for each path portion
            3/ Assembling the nodes into the tree

            The data format must be a list of files, minimally
            with "Name" corresponding to the full path.

        '''

        # Load data from web / url
        if filelist.startswith('http'):
            self._load_http(filelist)

        # Load data from file
        elif os.path.exists(filelist):
            if filelist.endswith('json'):
                self._load_file(filelist)

        # If we have loaded data, continue
        else:
            print('Error loading %s' %filelist)

        if self.data:
            self._load()


    def _load(self):
        '''a function called by load, intended for subclass to call if additional
           parsing is needed.
        '''
        pass


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


# Searching Functions

    def trace(self, filepath):
        '''trace a path in the tree, return all nodes up to it.
        '''
        return self.find(filepath, trace=True)

    def find(self, filepath, trace=False):
        '''find a path in the tree and return the node if found
        '''

        # if the user wants a trace, we return all paths up to it
        traces = []
 
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

                        # Does the user want to return a trace of all nodes?
                        if trace is True:
                            traces.append(node)

                        # If the name is what we are looking for, return Node
                        if node.Name == assembled:
                            if trace is True:
                                return traces
                            return node
                        break


# Visualization and Export



class ContainerDiffTree(ContainerTree):
    '''a container diff tree is a subclass of ContainerTree, specifically
       ready to read in the result of a files export from Google's Container
       Diff. We simply define the _load method to expect the format of:

       [0]['Analysis'] --> [{"Name":"...", "Size": 123 }]

    '''

    def _load(self):
        ''' class instantiated by subclass to do custom parsing of loaded data.
            In the case of Google container diff, whether from local file
            or web http, we need to index the list at 1 (only one in
            list since a Singularity container is one tar file) and then
            index the list of files at the "Analysis" key.
        '''

        if not self.data:
            print('This function should be called with load() to define data.')
            sys.exit(1)

        # User can provide loaded data, as long as correct structure
        if not isinstance(self.data, list):
            print('Loaded Filelist must be list for Container Diff')
        else:

            # The user loaded files, but the result is empty
            if len(self.data) == 0:
                print('Loaded Filelist is empty')

            # Data is stored at 0['Analysis']                
            if "Analysis" not in self.data[0]:
                print('Analysis key missing, is this ContainerDiff export?')
            else:
                self.data = self.data[0]['Analysis'] 


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
