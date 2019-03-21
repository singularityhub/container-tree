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

class Node(object):
    
    def __init__(self, name, attrs, tag=None):
        ''' a Node is a node in the Trie, meaning that
            it stores a word (a folder, name, or file) and some
            number of children from it. If a Node is a leaf 
            this coincides with the end of a path.

            Parameters
            ==========
            name: the name of the folder or file
            attrs: a dict of attributes to give to the node
            tag: a tag or label (goes into a list) to identify objects belonging

        '''
        self.label = name
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
        return "Node<%s>" % self.label
    def __repr__(self):
        return "Node<%s>" % self.label
    

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
        ats = {} 
        for key, val in self.__dict__.items():
            if key !="children":
                if isinstance(val, set):
                    val = list(val)
                ats[key] = val
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

    def get_children(self):
        '''a helper function to get children for a node. This is an iterator,
           if the list is large enough to warrant it.
        '''
        for child in self.children:
            yield child


class MultiNode(Node):
    '''a MultiNode is intended to hold multiple sets of children, indexed by
       the tag. This is intended for a Collection, where each single node
       is a container namespace (e.g., library/ubuntu) and the keys are
       tags, and each tag is associated with a list of children.
    '''
     
    def __init__(self, name, attrs, tag=None):
        super(MultiNode, self).__init__(name, attrs, tag=None)
        self.children = {}

    def __str__(self):
        return "MultiNode<%s>" % self.label
    def __repr__(self):
        return "MultiNode<%s>" % self.label

    def get_children(self):
        '''a helper function to get children for a node. This helps the user
           because the we need to loop over a dictionary. This isn't an iterator
           because it's expected that a node have a reasonably small number
           of children.
        '''
        children = []
        for child_tag in self.children:
            for child in self.children[child_tag]:
                yield child
