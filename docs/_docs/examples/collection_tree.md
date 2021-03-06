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

You'll also notice that the update function returns a boolean (True) to indicate
that the container was added and/or created. What if we try to add a child that doesn't have
a parent in the library, and the parent isn't already part of some subtree?

```python
tree.update('singularityhub/sregistry-cli', 'continuumio/miniconda3')

# False
# tree.root.children is still only library/ubuntu
# [MultiNode<library/ubuntu>]
```

False is returned because we didn't add the container. But if you don't want to limit your 
first level of your tree to library, you can disable it entirely like this:

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
tag. We can actually do a trace much easier:


```python
tree.trace('continuumio/miniconda3')
[Node<scratch>, MultiNode<library/debian>, MultiNode<continuumio/miniconda3>]
```

Now let's see what happens when we add a a different tag:

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
MultiNode<library/python>
MultiNode<continuumio/miniconda3>
MultiNode<singularityhub/containertree>
MultiNode<singularityhub/singularity-cli>
MultiNode<childof/miniconda3>
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

## Collection Tree Filesystems

The goal of the container tree filesystem is to write the tree into files and
folders, and then use standard linux tools to make inferences. Cool! 
Let's start by creating a simple tree:

```python
from containertree import CollectionTree

# Initialize a collection tree
tree = CollectionTree()
tree.update('continuumio/miniconda3', 'library/debian')
tree.update('singularityhub/containertree', 'continuumio/miniconda3')
tree.update('singularityhub/singularity-cli', 'continuumio/miniconda3')
tree.update('continuumio/miniconda3:1.0', 'library/debian')
tree.update('childof/miniconda3','continuumio/miniconda3:1.0')
tree.update('continuumio/miniconda3', 'library/python')
```

We can use an iterator to go over the nodes:

```python
for node in tree:
    print(node)

MultiNode<library/debian>
MultiNode<library/python>
MultiNode<continuumio/miniconda3>
MultiNode<singularityhub/containertree>
MultiNode<singularityhub/singularity-cli>
MultiNode<childof/miniconda3>
```

We can also return the nodes to a list:

```python
nodes = tree.get_nodes()
```

If we are creating a container collection filesystem (meaning representing
each collection as a full path, with tags as folders starting with . (or
another character of your choice):

```python
for path in tree.paths():
    print(path)

/scratch
/scratch/library/debian
/scratch/library/python
/scratch/library/python/.latest/continuumio/miniconda3
/scratch/library/python/.latest/continuumio/miniconda3/.latest/singularityhub/containertree
/scratch/library/python/.latest/continuumio/miniconda3/.latest/singularityhub/singularity-cli
/scratch/library/python/.latest/continuumio/miniconda3/.1.0/childof/miniconda3
```

A folder that represents a tag is prefixed with ".". You can change this to be something
else:

```python
for path in tree.paths(tag_prefix="TAG_"):
    print(path)

/scratch
/scratch/library/debian
/scratch/library/python
/scratch/library/python/TAG_latest/continuumio/miniconda3
/scratch/library/python/TAG_latest/continuumio/miniconda3/TAG_latest/singularityhub/containertree
/scratch/library/python/TAG_latest/continuumio/miniconda3/TAG_latest/singularityhub/singularity-cli
/scratch/library/python/TAG_latest/continuumio/miniconda3/TAG_1.0/childof/miniconda3
```

You can ask for only leaf nodes (if you were doing `mkdir -p` this is all you would
need)

```python
for path in tree.paths(leaves_only=True):
    print(path)

/scratch/library/python/.latest/continuumio/miniconda3/.latest/singularityhub/containertree
/scratch/library/python/.latest/continuumio/miniconda3/.latest/singularityhub/singularity-cli
/scratch/library/python/.latest/continuumio/miniconda3/.1.0/childof/miniconda3
```

You can also just get the list:

```python
paths = tree.get_paths()
```

For a more advanced example, see the [collection_tree](https://github.com/singularityhub/container-tree/tree/master/examples/collection_tree)
folder, where we use these functions to build a collection tree (filesystem) in a container,
and then search over it. Here we will show using the container provided for that example to add attributes
directly to the folders in the filesystem.


### Collection Tree Filesystem Metadata

We have provided a [collection tree filesystem](http://hub.docker.com/r/vanessa/collection-tree-fs) in a container for you to explore and interact with.
See the link in the previous section to see how it was built. To shell into the container directly:

```bash
$ docker run -it vanessa/collection-tree-fs
```

The working directory is scratch, the root of the filesystem tree (this
is a smaller example of what you will see):

```bash
(base) root@c1e3d68bac93:/scratch# tree
.
└── library
    ├── debian
    │   └── tag-latest
    │       └── vanessa
    │           └── pancakes
    └── python
        └── tag-latest
            └── continuumio
                └── miniconda3
                    ├── tag-1.0
                    │   └── childof
                    │       └── miniconda3
                    └── tag-latest
                        └── singularityhub
                            ├── containertree
                            └── singularity-cli

12 directories, 0 files
```

### 3. Interaction and Metadata

Now we can have fun! Search for a tag of interest, across all collections.

```bash
$ find . -name tag-latest
./library/debian/tag-latest
./library/python/tag-latest
./library/python/tag-latest/continuumio/miniconda3/tag-latest
```
 
Find the singularityhub collection

```bash
$ find . -name singularityhub
./library/python/tag-latest/continuumio/miniconda3/tag-latest/singularityhub
```

What about metadata? using filesystem [xattrs](https://en.wikipedia.org/wiki/Extended_file_attributes#Linux)
we've already added a count at each node, meaning the number of times the container was added as a
parent or a child. This was done in Python, but you can see this information with xattr on
the filesystem:


```bash
# List attributes for the library/debian folder (a count for that collection)
(base) root@f379adcb3cb7:/scratch# attr -l library/debian/
Attribute "count" has a 3 byte value for library/debian/

# Get the count
(base) root@f379adcb3cb7:/scratch# attr -g count library/debian/
Attribute "count" has a 3 byte value for library/debian/
3
```

If you wanted, you could easily set another attribute, some metadata of interest for the collection:

```bash
(base) root@38ecc937efda:/scratch# attr -s maintainer -V vanessasaur library/debian/
Attribute "maintainer" set to a 11 byte value for library/debian:
vanessasaur
```

The "V" means the value, and "-s" means set, so we use the general form `attr -s <key> -V <value> <path>`.
Now list all attributes:

```bash
(base) root@38ecc937efda:/scratch# attr -l library/debian/
Attribute "count" has a 3 byte value for library/debian/
Attribute "maintainer" has a 11 byte value for library/debian/
```

And get the actual values:

```bash
(base) root@38ecc937efda:/scratch# attr -g maintainer library/debian/
Attribute "maintainer" had a 11 byte value for library/debian/:
vanessasaur
```

How awesomely wicked cool is this! We can put metadata with out files.
