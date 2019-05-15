#
# Copyright (C) 2018-2019 Vanessa Sochat.
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
import json
import re
from .node import Node
from .loading import (
    load,
    update,
    _load,
    _update,
    _load_http,
    _load_list,
    _load_json,
    _load_container_diff,
)

class ContainerTreeBase(object):

    def __init__(self, inputs=None, tag=None, folder_sep='/'):
        '''construct a container tree from some export of files or 
           a string to indicate a container. This is determined by
           the subclass.

           Parameters
           ==========
           list: the json export (files.json) of a tar, can be https
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
        if inputs != None:
            self.load(inputs)

        # If data is loaded, make the tree
        if self.data:
            self._make_tree(tag=tag)


    def __str__(self):
        return "ContainerTreeBase<%s>" % self.count
    def __repr__(self):
        return "ContainerTreeBase<%s>" % self.count


    def insert(self, name, attrs=None, tag=None):
        '''insert a node into the tree.
        '''
        entry = {'Name': name }
        
        if attrs is not None:
            for key,val in attrs.items():
                entry[key] = val

        self._make_tree(data=[entry], tag=tag)


    def add(self, name, node, attrs={}, tag=None):
        '''add a node based on name to the tree, or return found node
        '''             
        # Do we have the package?    
        found = False
        for child in node.children:

           # We found the parent
           if child.label == name:

               # Keep track of how many we have
               child.counter += 1

               # update node to be child that was found
               node = child
               found = True
               break

        # If we get down here, not found, add new node
        if not found:
            new_node = Node(name, attrs)
            self.count +=1

            # Add to the root (or the last where found)
            node.children.append(new_node)
            node = new_node

        # Add the tag to the new (or existing) node
        if tag is not None:
            if tag not in node.tags:
                node.tags.add(tag)

        return node


    def _make_tree(self, data=None, tag=None):
        '''must be instantiated by subclass.'''
        print('_make_tree must be instantiated by the subclass.')


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

            tags = list(current.tags)
            new_node = {'color': choice(colors),
                        'key': current.label,
                        'name': current.label.split('/')[-1],
                        'tags': tags,
                        'attrs': current.get_attributes(),
                        'children': [] }

            # Add the size if was provided!
            if hasattr(current, 'size'):
                new_node['size'] = current.size

            if len(nodes) == 0:
                nodes.update(new_node)
            else:            
                nodes['children'].append(new_node)

            # Iterate through children, add to data structure
            for child in current.children:
                traverse(nodes=new_node, current=child)

        nodes = dict()

        if self.data not in [None, [], {}, ""]:
            traverse(nodes)
                
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


    def trace(self, name, node=None):
        '''find a path in the tree and return the node if found.
           This base function is suited for searches that don't build
           on themselves (e.g., not filepaths or words)
         '''
        if node == None:
            node = self.root

        # Find the node, is it in the tree?
        tracedNode = self.find(name)

        # Trace it's path
        if tracedNode != None:
            for child in node.children:
                traces = self._trace(tracedNode, child)
                if tracedNode in traces:
                    return [self.root] + traces


    def _trace(self, tracedNode, node, traces=None):
        '''find a path in the tree and return the node if found.
           This base function is suited for searches that don't build
           on themselves (e.g., not filepaths or words)

           Parameters
           ==========
           tracedNode: the node we are looking for.
           node: the current node we are searching
           traces: a list of nodes we have traced thus far
        '''
        if traces == None:
            traces = []

        # Always add node
        traces.append(node)

        # Did we find the node?
        if tracedNode in node.children:
            return traces + [tracedNode]

        # Keep searching over children        
        for child in node.children:
            self._trace(tracedNode, child, traces)
        return traces
       
    def get_count(self, name):
        '''find a path in the tree and return the node if found
        '''
        counter = 0
        node = self.find(name)
        if node:
            counter = node.counter
        return counter


    def find(self, name, node=None):
        '''find a path in the tree and return the node if found.
           This base function is suited for searches that don't build
           on themselves (e.g., not filepaths or words)
         '''

        if node == None:
            node = self.root

        # Did we find a node?
        if node.label == name:
            return node

        # No children, we finished search
        if len(node.children) == 0:
            return None

        for child in node.children:
            node = self.find(name, child)
            if node != None:
                return node


    def remove(self, name, node=None):
        '''find a path in the tree and remove (and return) the node if found.
           The function returns None if the Node wasn't in the tree (and wasn't
           found and removed). The way this is designed, we cannot remove the
           root node (but we just return it).
         '''

        if node == None:
            node = self.root

        # Did we find the node?
        if node.label == name:
            return node

        # No children, we finished search
        if len(node.children) > 0:
            for c in range(len(node.children)):
                child = node.children[c]
                to_remove = self.remove(name, child)
                if to_remove != None:
                    del node.children[c]
                    return to_remove


    def search(self, name, number=None, node=None):
        '''find a basename in the tree. If number is defined, return
           up to that number. 
        '''
        found = []
 
        # We always start at the root  
        if node == None:
            node = self.root

        # Look for the name in the current node
        if re.search(name, node.label):
            found.append(node)

        # No children, no search
        if len(node.children) == 0:
            return found

        # Does the user want to cut out early?
        if number != None:
            if len(found) >= number:
                return found

        # Not at current node, search children!
        for child in node.children:
            found += self.search(name, number, child)
            if number != None:
                if len(found) >= number:
                    return found
        return found


# Loading Functions
ContainerTreeBase.load = load
ContainerTreeBase._load = _load
ContainerTreeBase.update = update
ContainerTreeBase._update = _update
ContainerTreeBase._load_http = _load_http
ContainerTreeBase._load_json = _load_json
ContainerTreeBase._load_list = _load_list
ContainerTreeBase._load_container_diff = _load_container_diff
