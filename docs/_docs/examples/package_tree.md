---
title: Create a Container Package Tree
category: Examples
order: 4
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

Next, you probably should read about how to [export package data]({{ site.baseurl }}/examples/export_data/)
