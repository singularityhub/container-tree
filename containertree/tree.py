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
from random import choice
import requests
import json

class ContainerTree(object):

    def __init__(self, filelist, folder_sep='/', tag=None):
        '''construct a container tree from a container-diff
           export of flies. See "load" for the logic to construct
           the tree.

           Parameters
           ==========
           filelist: the json export (files.json) of a tar, can be https
           folder_sep: the character that separates path names
           tag: if defined, ascribe a unique id to the list at each node
                to identify the container. We can add other containers to
                the count.
 
        '''

        # The root node is the root of the fs
        self.root = Node('', {'size': 0, 'Name': '/'}, tag=tag)
        self.data = None
        
        # The character that separates folder/files
        self.folder_sep = folder_sep

        # Count the nodes
        self.count = 1
        
        # Sets self.data and builds self.tree
        self.load(filelist)

        # If data is loaded, make the tree
        if self.data:
            self._make_tree(tag=tag)


# Loading Functions
    
    def _load_http(self, url):
        '''load json from http. We assume it to be json because other formats
           aren't supported yet
        '''
        response = requests.get(url)

        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                print('The web address must be for json!')
                sys.exit(1)


    def _load_json(self, filelist):
        '''read the filelist from a json file
        '''

        # Read in the raw data file
        with open(filelist) as filey:
            data = json.load(filey)
        return data


    def update(self, filelist, tag=None):
        '''update will load in new data (without distributing an old self.data)

           Parameters
           ==========
           filelist: the list of files (json/url export from ContainerDiff
           tag: if defined, a tag or label to identify

        '''
        data = None

        # Load data from web / url
        if filelist.startswith('http'):
            data = self._load_http(filelist)

        # Load data from file
        elif os.path.exists(filelist):
            if filelist.endswith('json'):
                data = self._load_file(filelist)

        # If we have loaded data, continue
        else:
            print('Error loading %s' %filelist)

        if data:
            data = self._load(data)
            self._make_tree(data=data, tag=tag)


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
            self.data = self._load_http(filelist)

        # Load data from file
        elif os.path.exists(filelist):
            if filelist.endswith('json'):
                self.data = self._load_file(filelist)

        # If we have loaded data, continue
        else:
            print('Error loading %s' %filelist)

        if self.data:
            self.data = self._load()


    def _load(self, data=None):
        '''a function called by load, intended for subclass to call if additional
           parsing is needed.
        '''
        return self.data


    def __str__(self):
        return "ContainerTree<%s>" % self.count
    def __repr__(self):
        return "ContainerTree<%s>" % self.count


    def insert(self, filepath, attrs=None, tag=None):
        '''insert a node into the tree.
        '''
        entry = { 'Name': filepath }
        if attrs is not None:
            for key,val in attrs.items():
                entry[key] = val

        self._make_tree(data=[entry], tag=tag)
    

    def _make_tree(self, data=None, tag=None):
        '''construct the tree from the loaded data (self.data)
           we should already have a root defined.
        '''

        # If function is used for insert, called
        if data is None:
            data = self.data

        for attrs in data:

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


                # Add the tag to the new (or existing) node
                if tag is not None:
                    if tag not in node.tags:
                        node.tags.add(tag)

            # The last in the list is the leaf (file)
            node.leaf = True


    def export_tree(self, filename=None):
        '''export a data structure for a weighted, colored tree, either just
           the data or the full html / visualization. If filename is defined,
           export the raw data json to the file. If the generate_html is
           True, do the same but embed in html.

           Parameters
           ==========
           filename: if defined, write data to file (and return) otherwise
           return data structure

        '''

        # We will call this recursively
 
        def traverse(nodes={}, current=None):

            colors = ['#0000FF', # blue
                      '#FF7F00', # orange
                      '#FF0000', # red
                      '#7F007F', # purple
                      '#00FFFF', # cyan
                      '#0560D0'] # generic blue

            if current is None:
                current = self.root

            new_node = {'color': choice(colors),
                        'key': current.name,
                        'name': current.name.split('/')[-1],
                        'tags': current.tags,
                        'size': current.size,
                        'attrs': current.get_attributes(),
                        'children': [] }

            if len(nodes) == 0:
                nodes.update(new_node)
            else:            
                nodes['children'].append(new_node)

            # Iterate through children, add to data structure
            for child in current.children:
                traverse(nodes=new_node, current=child)

        nodes = dict()

        if self.data:
            traverse(nodes, current=self.root)
                
        # If the user provided a file, export to it
        if filename is not None:
            with open(filename, 'w') as filey:
                filey.writelines(json.dumps(nodes))
            return filename

        return nodes


# Searching Functions

    def similarity_score(self, tags):
        '''calculate a similarity score for one or more tags. The score is
           a basic information coefficient where we take into account:
 
           1/ the number of total nodes in context of the tags, meaning
              we add any node that has one or more of containers there
           2/ the number of nodes where the tags are all present
           3/ the number of nodes where one or more tags are missing

        '''
        total = 0       # total number of nodes with one or more
        intersect = 0   # all tags present at nodes
        diff = 0        # one or more tags missing

        def traverse(tags, current, total, intersect, diff):
 
            # All tags are represented in the node
            if all(t in current.tags for t in tags):
                intersect+=1
            else:
                diff+=1

            # If any of the tags are present, we add to total
            if any(t in current.tags for t in tags):
                total+=1

            # Iterate through children, add to data structure
            for child in current.children:
                total,intersect,diff = traverse(tags, child, total, intersect, diff)

            return total, intersect, diff

        # Return data structure so the user knows the components
        total, intersect, diff = traverse(tags, self.root, total, intersect, diff)
 
        result = {'total': total, 
                  'tags': tags,
                  'same': intersect,
                  'diff': diff }

        # Calculate score, percentage of nodes shared

        result['score'] = 0
        if total > 0:
           result['score'] = intersect / total

        return result


    def trace(self, filepath):
        '''trace a path in the tree, return all nodes up to it.
        '''
        return self.find(filepath, trace=True)


    def get_count(self, filepath):
        '''find a path in the tree and return the node if found
        '''
        counter = 0
        node = self.find(filepath)
        if node:
            counter = node.counter
        return counter


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
                        if node.name == assembled:
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

    def _load(self, data=None):
        ''' class instantiated by subclass to do custom parsing of loaded data.
            In the case of Google container diff, whether from local file
            or web http, we need to index the list at 1 (only one in
            list since a Singularity container is one tar file) and then
            index the list of files at the "Analysis" key.
        '''
        if data is None:
            data = self.data

        if not data:
            print('This function should be called with load() to define data.')
            sys.exit(1)

        # User can provide loaded data, as long as correct structure
        if not isinstance(data, list):
            print('Loaded Filelist must be list for Container Diff')
        else:

            # The user loaded files, but the result is empty
            if len(data) == 0:
                print('Loaded Filelist is empty')

            # Data is stored at 0['Analysis']                
            if "Analysis" not in data[0]:
                print('Analysis key missing, is this ContainerDiff export?')
            else:
                return data[0]['Analysis'] 


class Node(object):
    
    def __init__(self, filepath, attrs, tag=None):
        ''' a Node is a node in the Trie, meaning that
            it stores a word (a folder or file) and some
            number of children from it. If a Node is a leaf 
            this coincides with the end of a path.

            Parameters
            ==========
            filepath: the name of the folder or file
            attrs: a dict of attributes to give to the node
            tag: a tag or label (goes into a list) to identify objects belonging

        '''
        self.filepath = filepath
        self.children = []
        self.set_attributes(attrs)
        
        # The end of the file path
        self.leaf = False

        # If the tag is defined, tag the node
        self.tags = set()
        if tag is not None:
            self.tags.add(tag)

        # How many times this character appeared in the addition process
        self.counter = 1

    def __str__(self):
        return "Node<%s>" % self.filepath
    def __repr__(self):
        return "Node<%s>" % self.filepath
    

    def has(tag):
        '''determine if a node has a tag
        '''
        # All supplied tags are in the list
        if isinstance(tag, list):
            if all(tag) in self.tags:
                return True

        # The single tag is in the list
        if tag in self.tags:
            return True
        return False
              

    def get_attributes(self):
        '''return all attributes of the node (aside from children)'''
        ats = {key:val for key,val in self.__dict__.items() if key!="children"}
        return ats


    def set_attributes(self, attrs):
        '''Set a variable number of attributes, likely
           size of the file/folder

           Parameters
           ==========
           attrs: a dict of key,value attribute pairs

        '''

        for name, value in attrs.items():
            self.__setattr__(name.lower(), value)
