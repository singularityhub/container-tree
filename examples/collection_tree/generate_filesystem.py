#
# Copyright (C) 2019 Vanessa Sochat.
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

from containertree import CollectionTree
import pickle
import xattr
import sys
import os


# Option 1: Load a tree provided by the user
if os.path.exists('/tree.pkl'):
    tree = pickle.load(open('/tree.pkl','rb'))


# Option 2: build a dummy one
else:

    print('Add /tree.pkl to load tree from pickle. Creating dummy example.')

    tree = CollectionTree()
    tree.update('continuumio/miniconda3', 'library/debian')
    tree.update('vanessa/pancakes', 'library/debian')
    tree.update('singularityhub/containertree', 'continuumio/miniconda3')
    tree.update('singularityhub/singularity-cli', 'continuumio/miniconda3')
    tree.update('continuumio/miniconda3:1.0', 'library/debian')
    tree.update('childof/miniconda3','continuumio/miniconda3:1.0')
    tree.update('continuumio/miniconda3', 'library/python')
    

print('Creating paths and adding count metadata...')

# Since we want to get the count of nodes, we will ask for paths based on the node name
for node in tree.get_nodes():
    path = tree.get_paths(label=node.name)[0]
    if not os.path.exists(path):
        os.makedirs(path)
   
    # Create the attribute for the counter - the number of times the node was added as parent or child
    attribute = xattr.xattr(path)
    attribute['user.count'] = bytes(node.counter)
