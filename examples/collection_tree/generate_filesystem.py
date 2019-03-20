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


if os.path.exists('/container-collection-tree-final.pkl'):
    tree = pickle.load(open('/container-collection-tree-final.pkl','rb'))

else:

    print('Add /container-collection-tree-final.pkl, creating dummy example.')

    # Initialize a collection tree
    tree = CollectionTree()
    tree.update('continuumio/miniconda3', 'library/debian')
    tree.update('vanessa/pancakes', 'library/debian')
    tree.update('singularityhub/containertree', 'continuumio/miniconda3')
    tree.update('singularityhub/singularity-cli', 'continuumio/miniconda3')
    tree.update('continuumio/miniconda3:1.0', 'library/debian')
    tree.update('childof/miniconda3','continuumio/miniconda3:1.0')
    tree.update('continuumio/miniconda3', 'library/python')
    
print('Creating paths and adding count metadata...')
for path in tree.get_paths(tag_prefix='tag-', leaves_only=True):
    print('mkdir -p %s' % path)
