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

# This scrips will produce a massive summary tree (and save to file, if 
# argument is provided

# before we ran this script, we installed containertree
# pip install --user containertree

from containertree import ContainerFileTree
from random import choice
import requests
import sys

# Path to database of container-api
database = "https://singularityhub.github.io/api/files"
print('Selecting container from %s...' %database)
containers = requests.get(database).json()

print('Generating comparison tree!')
tree = ContainerFileTree(containers[0]['url'],
                         tag=containers[0]['collection'])

names = []
for c in range(len(containers)):
    container = containers[c]

    if len(container) > 0:

        # Some containers have different versions, thus have same collection name
        name = container['collection']

        # If we already have the container, add based on hash
        if name in names:
            name = "%s@%s" %(name, container['hash'])
        try:
            print('Adding %s' %name)
            tree.update(container['url'], tag=name)
            names.append(name)
        except:
            print('Skipping %s, issue loading json!' %name)
            pass

# Save to output file, if defined
if len(sys.argv) > 1:
    import pickle
    output =  sys.argv[1]
    print('Saving to %s' %output)
    pickle.dump(tree, open(output, 'wb'))
