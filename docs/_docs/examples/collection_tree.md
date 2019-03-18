---
title: Create a Collection Tree
category: Examples
order: 3
---

We've recently added a new kind of tree, the collection tree! With a collection 
tree, each node is a container, and we build the tree based on FROM statements
in Dockerfiles (the bases). Since the image manifests don't give hints about FROM,
we must build this from Dockerfiles, OR from a URI and it's from URI (meaning
we can collect pairs of parents and children).

## Creating a Collection Tree

The default collection tree will follow the Docker Hub hierarchy, where
the root node (scratch) is limited to children that start with "library."
This means you can do this:

```python
from containertree import CollectionTree

# Initialize a collection tree
tree = CollectionTree()

# library/ubuntu is a child of scratch
tree.update('scratch', 'library/ubuntu')

# tree.root.children
# [MultiNode<library/ubuntu>]
```

but you can't do this - the child "continuumio/miniconda3" since it's parent
isn't in the library, and it's already in the tree, it won't be added.

```python
tree.update('singularityhub/sregistry-cli', 'continuumio/miniconda3')

# tree.root.children is still only library/ubuntu
# [MultiNode<library/ubuntu>]
```

But if you don't want to limit your first level of your tree to library, you can
disable it entirely like this:

```python
tree = CollectionTree(first_level='')
```

Now try adding a non library node and it's child - you will see it added to the
tree!

```python
tree.update('singularityhub/sregistry-cli', 'continuumio/miniconda3')

tree.root.children
# [MultiNode<continuumio/miniconda3>]

tree.root.children[0].children
# {'latest': [MultiNode<singularityhub/sregistry-cli>]}
```

You can also change the first level to be something else:

```python
tree = CollectionTree(first_level='smeagle')
```

## Adding to the Collection Tree

Let's make a collection tree and add some nodes.

```python
from containertree import CollectionTree

# Initialize a collection tree
tree = CollectionTree()
tree.update('continuumio/miniconda3', 'library/debian')
tree.update('singularityhub/containertree', 'continuumio/miniconda3')
tree.update('singularityhub/singularity-cli', 'continuumio/miniconda3')

# tree.root.children
# [MultiNode<library/debian>]

# tree.root.children[0].children
{'latest': [MultiNode<continuumio/miniconda3>]}

# tree.root.children[0].children['latest'][0].children
{'latest': [MultiNode<singularityhub/containertree>,
            MultiNode<singularityhub/singularity-cli>]}
```

In the above, we see that the first level (off of the root node scratch) is a list.
After that, the children of a node is a dictionary, with the key being the tag
for the container, and the value item is the list of children for that particular 
tag. Now let's see what happens when we add a a different tag:

```python
tree.update('continuumio/miniconda3:1.0', 'library/debian')

tree.find('continuumio/miniconda3').children
{'1.0': [],
 'latest': [MultiNode<singularityhub/containertree>,
            MultiNode<singularityhub/singularity-cli>]}
```

The empty list means that the tag is added to the tree, but doesn't have any 
children yet. If we add a child:

```python
tree.update('childof/miniconda3','continuumio/miniconda3:1.0')

tree.find('continuumio/miniconda3').children
{'1.0': [MultiNode<childof/miniconda3>],
 'latest': [MultiNode<singularityhub/containertree>,
  MultiNode<singularityhub/singularity-cli>]}
```

We can also do this from a Dockerfile - the FROM statement will be read. In
the below example, the file "Dockerfile" exists in the present working directory:

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
            # uri                     # from uri
tree.update('continuumio/miniconda3', 'library/python')
```

We now see the new child library/python in the parent node, this is the "from" container
in the update operation:

```python
tree.root.children
[MultiNode<library/debian>, MultiNode<library/python>]
```

Note that continuumio/miniconda3 is removed from "library/debian", where it was
previously:

```python
tree.root.children[0].children

# library/debian:latest doesn't have any children
# {'latest': []}
```

The container is moved to it's new parent, library/python:

```python
tree.root.children[1].children
# {'latest': [MultiNode<continuumio/miniconda3>]}
```

And we can confirm that the tags and their children are all still present:

```python
tree.root.children[1].children['latest'][0].children
{'1.0': [MultiNode<childof/miniconda3>],
 'latest': [MultiNode<singularityhub/containertree>,
  MultiNode<singularityhub/singularity-cli>]}
```

Why does this happen? You simply cannot have a container that is represented
twice on the tree. Containers have one parent (the FROM statement) and
it's okay to get it wrong and move the child, but it's not okay
to represent the child twice.


## Listing Collection Nodes

We can iterate over all the nodes:

```python
for node in tree:
    print(node)

MultiNode<library/debian>
MultiNode<continuumio/miniconda3>
MultiNode<singularityhub/containertree>
MultiNode<singularityhub/singularity-cli>
```

## Find an Exact Node

We can get an exact node with "find" so we don't need to write weird for loops:

```python
tree.find('singularityhub/containertree')
# MultiNode<singularityhub/containertree>
```

## Search

or search for a string with "search"

```python
tree.search('hub')
[MultiNode<singularityhub/containertree>,
 MultiNode<singularityhub/singularity-cli>]
```

## Remove

To remove a node, you should reference it by it's name. If the node is found, it
will be returned by the function in case you want to use it for something else.

```python
tree.remove('continuumio/miniconda3')
# MultiNode<continuumio/miniconda3>
```

If you want to remove a particular tag (and not the others) you can specify it:

```python
tree.remove('continuumio/miniconda3', tag='1.0')
MultiNode<continuumio/miniconda3>
```

The function will still return the entire node, but the tag will be removed.
