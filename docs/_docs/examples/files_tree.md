---
title: Create a Container File Tree
category: Examples
order: 2
---

These examples are also provided in the 
[examples](https://github.com/singularityhub/container-tree/tree/master/examples) folder.
For this example, we will be using the [Container API](https://singularityhub.github.io/api/) 
served by the Singularity Hub robots to read in lists of files.

```python
from containertree import ContainerFileTree
import requests

# Path to database of container-api 
database = "https://singularityhub.github.io/api/files"
containers = requests.get(database).json()
entry = containers[0]  

# Google Container Diff Analysis Type "File" Structure
tree = ContainerFileTree(entry['url'])

# To find a node based on path
tree.find('/etc/ssl')
# Node<ssl>

# Trace a path, returning all nodes
tree.trace('/etc/ssl')
# [Node<>, Node<etc>, Node<ssl>]

# Insert a new node path
tree.insert('/etc/tomato')
tree.trace('/etc/tomato')
# [Node<>, Node<etc>, Node<tomato>]

# Get count of a node
tree.get_count('/etc/tomato')
# 1
tree.insert('/etc/tomato')
tree.get_count('/etc/tomato')
# 2

# Update the tree with a second container!
new_entry = containers[1]  
tree.update(new_entry['url'])
```

### Add a URI

Let's say that we don't have a list of files, either local or via http. If
we have [container-diff](https://github.com/GoogleContainerTools/container-diff) installed, 
we can add containers to the tree based on unique resource identifier (URI).

```python
from containertree import ContainerFileTree

# Google Container Diff Analysis Type "File" Structure
tree = ContainerFileTree("vanessa/salad")

# Find a node directly
tree.find('/code/salad')
Node<salad>

# Do a general search for "salad"
tree.search('salad')
[Node<salad>, Node<salad>, Node<salad.go>]

# These are different salads!
for res in tree.search('salad'):
    print(res.name)

/code/salad
/go/src/github.com/vsoch/salad
/go/src/github.com/vsoch/salad/salad.go
```

### Add Containers

If you are adding more than one container to a tree, you should keep track of
the containers that are represented at each node (meaning the file/folder exists
in the container). You can do this by using node tags. Here is how to create
(and update a tree) using these tags!

```python
entry1 = containers[0]  
entry2 = containers[1]
tag1=entry1['collection']
#'54r4/sara-server-vre'
tag2=entry2['collection']
#'A33a/sjupyter'
tree = ContainerFileTree(entry1['url'], tag=tag1)

# What are the tags for the root node?
tree.root.tags
Out[18]: ['54r4/sara-server-vre']

# Update the container tree with the second container
tree.update(entry2['url'], tag=tag2)
tree.root.tags
# ['54r4/sara-server-vre', 'A33a/sjupyter']
```

You can imagine having a tagged Trie will be very useful for different algorithms
to traverse the tree and compare the entities defined at the different nodes!

### Container Comparisons

Once we have added a second tree, we can traverse the trie to calculate comparisons!
The score represents the percentage of nodes defined in one or more containers (call
this total) that are represented in BOTH containers.

```python
# using the tree from above, where we have two tags
tags = tree.root.tags
# ['54r4/sara-server-vre', 'A33a/sjupyter']

# Calculate the similarity
scores = tree.similarity_score(tags)

# {'diff': 44185,
# 'same': 12201,
# 'score': 0.21638349945021815,
# 'tags': ['54r4/sara-server-vre', 'A33a/sjupyter'],
# 'total': 56386}
```
You can then use this to generate a heatmap / matrix of similarity scores, or anything
else you desire! For example, [here is the heatmap](https://singularityhub.github.io/container-tree/examples/heatmap/demo/) that I made.

What would we do next? Would we want to know what files change between versions of a container? If you want to do some sort of mini analysis with me, please reach out! I'd like to do this soon.
