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

# We expect to have a pickled tree as first argument (being used in container)
import pickle
import json
import time
import sys
import os

container1 = sys.argv[1]
outfile = sys.argv[2]

database = 'database.pkl'
if not os.path.exists(database):
    print('Database not found at %s' %database)
    sys.exit(1)

print('Loading Saved Container Tree:')
tree = pickle.load(open(database, 'rb'))

containers = tree.root.tags
score_row = []

# Now we can generate a little matrix of similarity scores!
print('Calculating (non optimized) score matrix!')
for container2 in containers:
    tags = [container1, container2]
    result = tree.similarity_score(tags)
    score_row.append(result['score'])        
    
saveme = {'row': score_row, 'container': container1, 'containers': containers}
pickle.dump(saveme, open(outfile,'wb'))
