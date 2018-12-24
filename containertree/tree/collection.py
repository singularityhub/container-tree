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
    run_container_diff 
)
import requests
import json

from .base import ContainerTreeBase

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
        self.root = Node('', {'size': 0, 'Name': 'scratch'}, tag=None)

    def __str__(self):
        return "CollectionTree<%s>" % self.count
    def __repr__(self):
        return "CollectionTree<%s>" % self.count


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
            print('Loaded inputs must be list for Container Diff')
        else:

            # The user loaded files, but the result is empty
            if len(data) == 0:
                print('Loaded inputs is empty')

            # Data is stored at 0['Analysis']                
            if "Analysis" not in data[0]:
                print('Analysis key missing, is this ContainerDiff export?')
            else:
                return data[0]['Analysis']

