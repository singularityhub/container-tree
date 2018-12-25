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
from containertree.utils import (
    check_install, 
    DockerInspector
)
import requests
import json

from .base import ( ContainerTreeBase, Node )

class CollectionTree(ContainerTreeBase):
    '''a collection tree is a subclass of container tree that walks up
       the tree (finding parents via the Dockerfile) until we get to scratch
       or cannot proceed (with a 404, etc.) We produce a tree of containers
       that are based on FROM statements, and we obtain the metadata about
       the containers from container-diff.

    '''
    def __init__(self, inputs=None, tag=None):
        super(CollectionTree, self).__init__(inputs, tag=tag)

        # Update the root to be for scratch
        self.root = Node('', {'size': 0, 'Name': 'scratch'}, tag=None)


    def __str__(self):
        return "CollectionTree<%s>" % self.count
    def __repr__(self):
        return "CollectionTree<%s>" % self.count


    def _load(self, data=None):
        '''when we start here, we've been passed either a container-diff
           data structure, or a loaded container URI, or a Dockerfile.'''

        # Case 1. if we loaded a container-diff uri, it will be a list, get uri
        self.data = "scratch"

        if isinstance(data, list):
            self.data = data[0]['Image']

        # Case 2: Data is actually a Dockerfile that needs to be parsed
        elif "Dockerfile" in data:
            if os.path.exists(data):
                froms = self._load_dockerfile(data, action="FROM")

                # If we find the FROM, we want to extract history to get all from
                # In future, could support more than one from here
                if len(froms) > 0:
                    self.data = self.data[0]

        # When we get down here, we have either self.data as scratch, or a uri


    def _load_dockerfile(self, dockerfile, action=None):
        '''extract one or more actions from a Dockerfile. If action is not
           defined, then return all that are found.
        '''
        lines = []
        with open(dockerfile, 'r') as filey:
            for line in filey.readlines():
                if action != None:
                    if action in line:
                        line = line.replace('FROM','').strip()
                        lines.append(line)
                else:
                    lines.append(line)
        return lines

    def _make_tree(self, data=None, tag=None):
        '''construct the tree from the loaded data (self.data) which for
           this collection tree is a URI for a Docker image. Since we are making
           the tree starting with a single container and building based on
           FROM statements, the nodes correspond to different containers,
           and they are tagged with container tags.
        '''

        # The URI of a docker container to start parsing
        if data is None:
            data = self.data

        # Load the URI into the docker inspector
        inspect = DockerInspector(data)

        for attrs in data:

            # The starting node is the root node
            node = self.root

            filepaths = attrs['Name'].split(self.folder_sep)
        
            # Add the path to the correct spot in the tree    
            for filepath in filepaths:

                if not filepath:
                    continue

                found = False

                # We are at the root
                if filepath == node.label:
                    found = True             
                    
                else:

                    # Search in present node
                    for child in node.children:

                        # We found the parent
                        if child.label == filepath:

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
