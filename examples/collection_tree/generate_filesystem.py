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
import sys
import os

################################################################################
# Generate Collection Tree
################################################################################


if not os.path.exists('container-collection-tree.pkl'):
    print('Please put container-collection-tree.pkl in PWD, creating dummy.')
    tree = pickle.load(open('container-collection-tree.pkl','rb'))

else:

    # Initialize a collection tree
    tree = CollectionTree()
    tree.update('continuumio/miniconda3', 'library/debian')
    tree.update('singularityhub/containertree', 'continuumio/miniconda3')
    tree.update('singularityhub/singularity-cli', 'continuumio/miniconda3')
    tree.update('continuumio/miniconda3:1.0', 'library/debian')
    tree.update('childof/miniconda3','continuumio/miniconda3:1.0')
    tree.update('continuumio/miniconda3', 'library/python')
    
    print('Creating paths...')
    for path in tree.get_paths():
        os.makedirs(path)
