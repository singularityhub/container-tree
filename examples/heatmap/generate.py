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

from containertree import ContainerFileTree
from random import choice
import requests
import tempfile
import json

# Path to database of container-api
database = "https://singularityhub.github.io/api/files"
print('Selecting container from %s...' %database)
containers = requests.get(database).json()
container1 = containers[0]
container2 = containers[1]

# Google Container Diff Structure
tree = ContainerFileTree(container1['url'],
                         tag=container1['collection'])

# Add the second container to the tree
tree.update(container2['url'],
            tag=container2['collection'])

# All the containers (tags) represented in the tree
tags = tree.root.tags

# Calculate the similarity
scores = tree.similarity_score(tags)

# {'diff': 44185,
# 'same': 12201,
# 'score': 0.21638349945021815,
# 'tags': ['54r4/sara-server-vre', 'A33a/sjupyter'],
# 'total': 56386}

# We can now generate a matrix of similarity scores for containers!
# Let's build from scratch

print('Generating comparison tree!')
tree = ContainerFileTree(containers[0]['url'],
                         tag=containers[0]['collection'])

names = []
for c in range(len(containers)):
    if len(names) < 10:
        container = containers[c]

        # Some containers have different versions, thus have same collection name
        name = container['collection']

        # Let's just use different collections for this example
        if name not in names:
            names.append(name)

            print('Adding %s' %name)
            tree.update(container['url'], tag=name)
    else:
        break

# Generating comparison tree!
# Adding 54r4/sara-server-vre
# Adding A33a/sjupyter
# Adding AaronTHolt/openmpi_singularity
# Adding AlanKuurstra/qsm_sstv
# Adding BIDS-Apps/ndmg
# Adding CAIsr/antsCorticalThickness
# Adding CAIsr/optimizing_exercise
# Adding CAIsr/qsm
# Adding CHRUdeLille/nextflow
# Adding CHRUdeLille/vep_containers

score_matrix = []

# Now we can generate a little matrix of similarity scores!
print('Calculating (non optimized) score matrix!')
for container1 in names:
    score_row = []
    for container2 in names:
        tags = [container1, container2]
        result = tree.similarity_score(tags)
        score_row.append(result['score'])        
    score_matrix.append(score_row)

# Create temporary directory and copy file there
from containertree.utils import get_template
from containertree.server import serve_template
import shutil
import tempfile

# Copy the file to the webroot
webroot = tempfile.mkdtemp()
print('Webroot: %s' %webroot)
template = get_template('heatmap')
shutil.copyfile(template, "%s/index.html" %webroot)

# Generate the data.json
print('Exporting data for d3 visualization')
data = {"data": score_matrix, "X": names, "Y": names}
with open('%s/data.json' %webroot, 'w') as filey:
    filey.writelines(json.dumps(data))

serve_template(webroot)
