#/usr/bin/env python

from containertree.utils import get_template

import os
import pickle
import shutil
import json
from glob import glob

here = os.getcwd()
outputdir = '%s/result' %(here)

pickles = glob('%s/*/pkl' %here)
scores = dict()

for p in pickles:
    result = pickle.load(open(p,'rb'))
    container = result['container']
    scores[container] = result['row']
    containers = result['containers']

# We need to assemble the scores in rows in the same order as "containers"
score_matrix = []
for container in containers:
    score_matrix.append(scores[container])

template = get_template('heatmap')
shutil.copyfile(template, "%s/index.html" %here)

# Generate the data.json
print('Exporting data for d3 visualization')
data = {"data": score_matrix, "X": containers, "Y": containers}
with open('%s/data.json' %here, 'w') as filey:
    filey.writelines(json.dumps(data))
