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
