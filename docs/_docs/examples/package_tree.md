---
title: Create a Container Package Tree
category: Examples
order: 2
---

These examples are also provided in the 
[examples](https://github.com/singularityhub/container-tree/tree/master/examples) folder.
For this example, we will again be using the [Container API](https://singularityhub.github.io/api/) 
served by the Singularity Hub robots to read in lists of files.

### Create a Container Package Tree

You can also create trees to map different containers to packages maintained
under Pip and Apt.

**Apt Packages**

```python
from containertree.tree import ContainerAptTree

# Initilize a tree with packages from a container
apt = ContainerAptTree('singularityhub/sregistry-cli')

apt.trace('wget')
# [Node<>, Node<wget>, Node<1.18-5 deb9u2>]

apt.find('wget')
# Node<wget>

apt.search('bin')
[Node<binutils>,
 Node<libc-bin>,
 Node<libc-dev-bin>,
 Node<libpam-modules-bin>,
 Node<ncurses-bin>]
```


**Pip Packages**

```python
from containertree.tree import ContainerPipTree

# Initilize a tree with packages from a container
pip = ContainerPipTree('neurovault/neurovault')

# How many nodes?
pip.count
175

pip.trace('nilearn')
# [Node<>, Node<nilearn>, Node<0.4.2>]
```
The idea would be to add containers to the tree with "update" and as you do,
tag the nodes with the container name (or other interesting metadata).

## Tagged Trees

If you want to use a package tree to represent more than one container, then
you should tag the nodes (packages) with the containers as you go. Let's
go through the previous example with apt, but add tags to the nodes.

By tagging nodes (packages) with the containers that include them, 
we can use the data structure for interesting purposes like exporting data 
frames (for analysis) or calculating comparisons. Let's first walk through 
how to tag our container package trees.

```python
from containertree.tree import ContainerAptTree

# Initilize a tree with packages from a container
apt = ContainerAptTree('singularityhub/sregistry-cli', tag = 'singularityhub/sregistry-cli')
ContainerAptTree<433>
```

Now we can see that the root node (and all package nodes) have a tag for the container!

```python
apt.root.tags
# {'singularityhub/sregistry-cli'}

wget = apt.find('wget')
# wget.tags
{'singularityhub/sregistry-cli'}
```

And if you add a container, you can see that the nodes tags will expand. If both
containers have wget, the node will be tagged with both. If only one node has
wget, you'll only see the one tag.

```python
apt.update('library/debian', tag='library/debian')

find = apt.find('findutils').tags
{'library/debian', 'singularityhub/sregistry-cli'}
```

The reason that the library doesn't do the tagging for you when you add a container
is that it doesn't enforce how you might want to use the container package tree.
For example, let's say that you are interested in comparing containers between
institutions or users. Your tag might be a user or institution name.

```python
apt.update('library/debian', tag='Stanford')
apt.update('library/ubuntu', tag='Berkeley')
```

### Export Package Data

Why is this useful? If we store information at each node about the containers
that have the packages, we can parse the tree to extract data or calculate
similarity. Let's start with showing how to export package data. If you
use this feature, you will additionally need the pandas module installed.
Here are a few ways to install pandas:

```bash
pip install pandas
pip install containertree[analysis]
apt-get install -y python3-pandas
```

We would likely want to do some kind of analysis over container packages, and the
first step would be to extract a data frame. Here is how to do that. First,
create your tree and add some containers to it.

```python
from containertree.tree import ContainerAptTree

# Initilize a tree with packages from a container, add others
apt = ContainerAptTree('singularityhub/sregistry-cli', tag='singularityhub/sregistry-cli')
apt.update('library/debian', tag='library/debian')
apt.update('library/ubuntu', tag='library/ubuntu')
```

Here is how to export a pandas data frame with the packages:

```python
df = apt.export_vectors()
df.head()

                              adduser  3.115  3.116ubuntu1  apt  1.4.8  1.6.6  \
library/ubuntu                    1.0    NaN           1.0  1.0    NaN    1.0   
library/debian                    1.0    1.0           NaN  1.0    1.0    NaN   
singularityhub/sregistry-cli      1.0    1.0           NaN  1.0    1.0    NaN   
```

The rows represent the containers, and the columns the packages. A value of
NaN indicates the package isn't installed in the container, and 1.0 indicates
that it is. Here is how to fill in 0 for the NaN values, if you prefer.

```python
df = df.fillna(0)
```

You can optionally subset to a particular set of tags, either including
only a specific set:

```python
df = apt.export_vectors(include_tags=['library/debian'])
df.head()
                adduser  3.115  apt  1.4.8  base-files  9.9 deb9u6  \
library/debian      1.0    1.0  1.0    1.0         1.0         1.0  
```

or skipping specific containers:


```python
df = apt.export_vectors(skip_tags=['library/debian'])
df.head()
                              adduser  3.115  3.116ubuntu1  apt  1.4.8  1.6.6  \
library/ubuntu                    1.0    NaN           1.0  1.0    NaN    1.0   
singularityhub/sregistry-cli      1.0    1.0           NaN  1.0    1.0    NaN
```

Or using a regular expression to filter the tags (useful for collection names,
such as finding all containers in the "library" namespace):


```python
df = apt.export_vectors(regexp_tags="^library")
df.head()
                adduser  3.115  3.116ubuntu1  apt  1.4.8  1.6.6  base-files  \
library/debian      1.0    1.0           NaN  1.0    1.0    NaN         1.0   
library/ubuntu      1.0    NaN           1.0  1.0    NaN    1.0         1.0   
```
