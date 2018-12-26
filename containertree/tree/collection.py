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
    def __init__(self):
        super(CollectionTree, self).__init__()

        # Update the root to be for scratch
        self.root = Node('scratch', {'size': 0, 'Name': 'scratch'}, tag=None)
        self.orphans = {}

    def __str__(self):
        return "CollectionTree<%s>" % self.count
    def __repr__(self):
        return "CollectionTree<%s>" % self.count

    def _load(self, uri, fromuri):
        '''when we start here, we've been passed a Dockerfile.
        '''

        # Case 1. if we loaded a container-diff uri, it will be a uri
        if "Dockerfile" in fromuri:        
            if os.path.exists(fromuri):
                froms = self._load_dockerfile(fromuri, action="FROM")

                # If we find the FROM, we want to extract history to get all from
                # In future, could support more than one from here
                if len(froms) > 0:
                    fromuri = froms[0]

        return {"Image": uri, "From": fromuri}


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

    def _make_tree(self, uri, fromuri, tag=None):
        '''construct the tree from the loaded data (self.data) which for
           this collection tree is a URI for a Docker image. Since we are making
           the tree starting with a single container and building based on
           FROM statements, the nodes correspond to different containers,
           and they are tagged with container tags.
        '''

        # Find the node in the tree, if it exists
        nodeImage = self.find(uri)
        nodeFrom = self.find(fromuri)                

        # Case 1: both exist, do nothing.
        if nodeImage != None and nodeFrom != None:
            return

        # Case 2: Parent is in tree, but not child
        elif nodeImage == None and nodeFrom != None:
            nodeImage = Node(uri, {"Name": uri })
            nodeImage.leaf = True
            nodeFrom.children.append(nodeImage)

        # Case 3: Child is in tree, but not parent
        elif nodeImage != None and nodeFrom == None:
            nodeFrom = Node(fromuri, {"Name": fromuri })
            # Remove the nodeImage
            nodeImage = self.remove(uri)
            # Add as child to new parent
            nodeFrom.children.append(nodeImage)
            self.root.children.append(nodeFrom)

        # Case 4: Both aren't in tree
        if nodeImage == None and nodeFrom == None:
            nodeFrom = Node(fromuri, {"Name": fromuri })
            nodeImage = Node(uri, {"Name": uri })
            nodeImage.leaf = True
            nodeFrom.children = [nodeImage]
            self.root.children.append(nodeFrom)

        if tag is not None:
            if tag not in nodeImage.tags:
                nodeImage.tags.add(tag)


    def update(self, uri, fromuri, tag=None):
        '''update will load in new data (without distributing an old self.data)
        '''

        # Loads {"Image": ... "From": ...}
        data = self._load(uri, fromuri)

        # If we have loaded data, continue
        if data:
            self._make_tree(data['Image'], data['From'], tag=tag)


    def load(self, uri, fromuri, tag=None):
        ''' uri must be the uri for a container. fromuri can be a uri OR
            a Dockerfile for the uri given (to extract from)
        '''
        self.update(uri, fromuri, tag)
