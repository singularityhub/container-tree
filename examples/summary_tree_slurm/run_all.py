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
import sys
import os

database = 'database.pkl'
if not os.path.exists(database):
    print('Database not found at %s' %database)
    sys.exit(1)

print('Loading Saved Container Tree:')
tree = pickle.load(open(database, 'rb'))

here = os.getcwd()
os.system('mkdir -p result')
os.system('mkdir -p jobs')

# Do the comparison with the rest
containers = list(tree.root.tags)

print('%s of containers are found in tree!' %len(containers)) 

# This is a general script to submit the job files
with open('run_jobs.sh', 'w') as run_jobs:
    run_jobs.writelines('#!/bin/bash\n')
    for c in range(len(containers)):
        run_jobs.writelines('sbatch -p russpold %s/jobs/run_%s.sh\n' %(here, c))

# Write a bash file to submit jobs
for c in range(len(containers)):
    container = containers[c]
    with open('jobs/run_%s.sh' %c, 'w') as filey:
        name = container.replace('/','-')
        filey.writelines('#!/bin/bash\n')
        outfile = '%s/result/%s.pkl' %(here, name)
        print ("Processing container %s" %(c))
        # Write job to file
        filey.writelines("#SBATCH --job-name=containertree_%s\n" %(c))
        filey.writelines("#SBATCH --output=%s/jobs/containertree%s.out\n" %(here,c))
        filey.writelines("#SBATCH --error=%s/jobs/containertree%s.err\n" %(here,c))
        filey.writelines("#SBATCH --time=60:00\n")
        filey.writelines("#SBATCH --mem=8000\n")
        filey.writelines('ml python/3.6.1\n')
        filey.writelines('python3 %s/run.py %s %s\n' %(here,container,outfile))
