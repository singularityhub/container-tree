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

from containertree import ContainerDiffTree
from random import choice
import requests
import tempfile

# Path to database of container-api
database = "https://singularityhub.github.io/api/files"
print('Selecting container from %s...' %database)
containers = requests.get(database).json()
container1 = containers[0]
container2 = containers[1]

# Google Container Diff Structure
print('Generating tree!')
tree = ContainerDiffTree(container1['url'])
tree.update(container2['url'])

print(tree)
# ContainerTree<38008>

# Create temporary directory and copy file there
from containertree.utils import get_template
from containertree.server import serve_template
import shutil
import tempfile

# Copy the file to the webroot
webroot = tempfile.mkdtemp()
print('Webroot: %s' %webroot)
template = get_template('shub_tree')
shutil.copyfile(template, "%s/index.html" %webroot)

# Generate the data.json
print('Exporting data for d3 visualization')
tree.export_tree(filename='%s/data.json' %webroot)
serve_template(webroot)
