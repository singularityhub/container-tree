---
title: Create a Collection Tree
category: Examples
order: 3
---

We've recently added a new kind of tree, the collection tree! With a collection 
tree, each node is a container, and we build the tree based on FROM statements
in Dockerfiles (the bases). Since the image manifets don't give hints about FROM,
we must build this from Dockerfiles, OR from a URI and it's from URI (meaning
we can collect pairs of parents and children).

```python
from containertree import CollectionTree

# Initialize a collection tree
tree = CollectionTree()
tree.update('singularityhub/containertree', 'continuumio/miniconda3')

# tree.root.children
# [MultiNode<continuumio/miniconda3>]

tree.update('singularityhub/sregistry-cli', 'continuumio/miniconda3')
```

We've just added a second child to the parent `continuumio/miniconda3` (with
implied tag "latest")

```python
# tree.root.children[0].children

{'latest': [ MultiNode<singularityhub/containertree>,
             MultiNode<singularityhub/sregistry-cli> ] }
```

Now let's try updating with the same namespace container, but a different tag:

```python
tree.update('singularityhub/containertree', 'continuumio/miniconda3:1.0')

{'1.0': [MultiNode<singularityhub/containertree>],
 'latest': [MultiNode<singularityhub/sregistry-cli>]}
```

Since a container with a specific unique resource identifier can only have
one parent, this represents moving the node in the tree. The new parent tag is
1.0. 

The two tags are still under the same namespace, (continuumio/miniconda3), and 
organized by the tag. Thus, when you do find for a container, you can return the 
entire node with all tags:

```python
tree.find('continuumio/miniconda3')
MultiNode<continuumio/miniconda3>
```

We can also do this from a Dockerfile

```
# The parent is the same continuumio/miniconda3
tree.update('vanessa/salad', "Dockerfile")

tree.find('continuumio/miniconda3').children
{'1.0': [MultiNode<singularityhub/containertree>],
 'latest': [MultiNode<singularityhub/sregistry-cli>, MultiNode<vanessa/salad>]}
```

Now let's say we add the actual parent of continuumio/miniconda3 (it's not scratch),
but let's pretend it's the library/python base image.

```python
tree.update('continuumio/miniconda3', 'library/python')
```

We now see the new child in the parent node

```python
tree.root.children
[MultiNode<continuumio/miniconda3>, MultiNode<library/python>]
```

and node that continuumio/miniconda3 is still represented, but for a different
tag (not latest):

```python
tree.root.children[0].children
{'1.0': [MultiNode<singularityhub/containertree>]}
```

And the "latest" tag, previously under scratch, is now under library/python:

```python
tree.root.children[1].children
{'latest': [MultiNode<continuumio/miniconda3>]}
```

and it's inherited the previous children.

```python
tree.root.children[1].children['latest'][0].children
{'latest': [MultiNode<singularityhub/sregistry-cli>, MultiNode<vanessa/salad>]}
```
