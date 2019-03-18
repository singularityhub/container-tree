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

from containertree import CollectionTree
from containertree.utils import recursive_find
from random import choice
from copy import deepcopy
import requests
import tempfile
import pickle
import os

################################################################################
# Pair Generation
################################################################################

# These files are from vsoch/dockerfiles on Github, scraped in 2017
# The pickle of the list of images is also included here. The scraping
# I did in 2019 I wasn't able to obtain the URI and dockerfile.
# List of [<container>, <Dockerfile>]
pairs = []

if os.path.exists('dockerfile-pairs.pkl'):

    # pickle.dump(open('dockerfile-pairs.pkl', 'wb'))
    pairs = pickle.load(open('dockerfile-pairs.pkl', 'rb'))

else:

    # Here I'll show you how I generated the data file, you don't need to run this!
    database = "/home/vanessa/Documents/Dropbox/Code/database/dockerfiles/data"
    for dockerfile in recursive_find(database, "Dockerfile"):
        container_name = '/'.join(os.path.dirname(dockerfile).split('/')[-2:])
        pairs.append([container_name, dockerfile])    

# How many pairs (containers) to add?
len(pairs)
# 129519


################################################################################
# Generate Collection Tree
################################################################################


if os.path.exists('container-collection-tree.pkl'):
    tree = pickle.load(open('container-collection-tree.pkl','rb'))
else:
    tree = CollectionTree()

    # First addition will only add library containers to root
    for pair in pairs:
        tree.update(uri=pair[0], fromuri=pair[1])

    # We skip over containers with variables in name (eg., FROM $BASE) and
    # parse away as build, etc.

    # Save intermediate tree
    pickle.dump(tree, open('container-collection-tree-library-only.pkl','wb'))

    len(tree.root.children)
    # 184

    # Now add nodes onto library
    for pair in pairs:
        tree.update(uri=pair[0], fromuri=pair[1])

    pickle.dump(tree, open('container-collection-tree.pkl','wb'))


    for pair in pairs:
        tree.update(uri=pair[0], fromuri=pair[1])

    # Save final tree
    pickle.dump(tree, open('container-collection-tree.pkl','wb'))
