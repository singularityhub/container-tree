#/usr/bin/env python

from containertree.utils import get_template

import os
import pickle
import shutil
import pandas
import json
from glob import glob

here = os.getcwd()
outputdir = '%s/result' %(here)

data=pickle.load(open('database.pkl','rb'))
containers=list(data.root.tags)

scores = pandas.DataFrame(columns=containers, index=containers)

for container in containers:
    p = '%s/%s.pkl' %(outputdir, container.replace('/','-'))
    row = pickle.load(open(p,'rb'))
    scores.loc[container, containers] = row.loc[:,containers].values.tolist()[0]

# Generate the data.json
print('Exporting data for d3 visualization')

scores.to_pickle('scores-df.pkl')
nrow,ncol=scores.shape
scores['container1'] = scores.index.tolist()

# We need to melt the data frame, and put X and Y coords in columns
df = scores.melt('container1')
df.columns = ['container1', 'container2', 'values']

# Create a data structure of rows and columns
rows = []
cols = []
for r in range(nrow):
    for c in range(ncol):
        rows.append(r+1)
        cols.append(c+1)

df['x'] = rows
df['y'] = cols

df.to_csv('data.tsv', sep='\t', index=None)
template = get_template('heatmap-large')
shutil.copyfile(template, "%s/index.html" %here)

# This is the only meaningful way!

# Here is a busy plot for ALL containers, a heatmap that isn't so usable
import seaborn as sns
import matplotlib.pylab as plt
plotdf = pandas.DataFrame(scores.values.tolist())
plotdf.columns = scores.columns
plotdf.index = scores.index
sns.heatmap(plotdf, fmt="g", cmap='viridis')
plt.show()

# Let's be selfish and remove row sums that are lowest

# plotdf.sum().min()
# 1.7225635133120807

# plotdf.sum().max()
# 34.06988856152033

# plotdf.sum().mean()
# 19.615016782058525

# Remove the different versions
labels = [x for x in plotdf.index if not "@" in x]
subset = plotdf.loc[labels,labels]

# Look at min, max, mean
subset.sum().min()
# 1.3337867032502615

subset.sum().max()
# 20.768391522450734

subset.sum().mean()
# 11.37132272286213

# let's export this subset
subset = subset.loc[subset.sum() >= 15, subset.sum() >= 15]

# Just look at 26 highly similar containers
data = {"data": subset.values.tolist(), "X": subset.index.tolist(), "Y": subset.columns.tolist()}
with open('data.json', 'w') as filey:
    filey.writelines(json.dumps(data))

sns.clustermap(subset, fmt="g", cmap='viridis')
plt.show()

nrow,ncol=subset.shape
subset['container1'] = subset.index.tolist()

# We need to melt the data frame, and put X and Y coords in columns
df = subset.melt('container1')
df.columns = ['container1', 'container2', 'values']

# Create a data structure of rows and columns
rows = []
cols = []
for r in range(nrow):
    for c in range(ncol):
        rows.append(r+1)
        cols.append(c+1)

df['x'] = rows
df['y'] = cols

df.to_csv('data-subset.tsv', sep='\t', index=None)

# Here is how to subset to a specific container (across versions)
labels = [x for x in plotdf.index if "TomaszGolan/mlmpr" in x]
subset = plotdf.loc[labels,labels]

sns.clustermap(subset, fmt="g", cmap="YlGnBu")
plt.show()
