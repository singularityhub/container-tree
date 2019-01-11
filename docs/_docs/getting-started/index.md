---
title: Why Container Tree?
category: Getting Started
permalink: /getting-started/index.html
order: 1
---

Container Tree implements data structures and methods for visualization,
comparison, and analysis using one or more 
[linux containers](https://en.wikipedia.org/wiki/Linux_containers).
It can help you not only to see inside a container, but to implement
tools for searching, comparing, and better understanding one or more
containers.

## What is a container tree?

In the context of containers, a container tree will map the file system of
a container into a tree structure. This means that each node represents
a file path, and holds with it metadata like counts and tags. And yes! This
means that for a single Container Tree, you can map multiple containers to it,
and have the nodes tagged with the containers that are represented there.
For example, we might have this node:

```
Node
  name: /usr/local/bin
  count: 2
  tags: ["ubuntu", "centos"]
```

This would say that there are two containers mapped to the tree, ubuntu and
centos, and both of them have the path /usr/local/bin. We can then calculate
similarity metrics by walking the tree and comparing containers defined at each
node. Intuitively, the root node of the tree is the root of a filesystem /.

## What is a container package tree?

In the case that we want to organize our tree based on packages and versions,
we can use the container package tree. Specifically, we are interested in 
pip (python) and apt (debian/ubuntu). Each node of this tree represents one
level of a package, and to the node we map containers that have the package
at that level. For example, we might have these levels for the pip tree:

```
Pip
   ___ requests
               ___ requests == 2.0
               ___ requests == 2.1
               ___ requests == 2.2
               ...
```

Each node above is a particular version of requests, and we map containers to it
that have that version. Here is the node for requests == 2.2:

```
Node:
  name: requests == 2.2
  count: 2
  tags ["ubuntu", "centos"]
```

This means that we can very easily compare containers by doing a single walk
of the tree. It also means that we can identify the last common ancestor
for any given package to determine similarity. For example, if two containers
had different versions of requests, they would be similar up to the level
of the Node for just "requests."

## What is a collection tree?

If you want to move up one level and think about container inheritance (meaning
the FROM statement in the Dockerfile recipes) you might be interested in a
Collection tree. In a collection tree, each Node represents a container base,
and the count is the number of times we find it for some container set that 
we have parsed. For this kind of tree, the root node is the scratch base image.


> Where do I go next?

You can learn about:

 - Different [classes]({{ site.url }}{{ site.baseurl }}/getting-started/classes/) of container trees.
 - Using the [client]({{ site.url }}{{ site.baseurl }}/getting-started/classes/) to quickly generate trees.
 - A [writeup](https://vsoch.github.io/2018/container-tree/) in 2018 when the library started development.

## Licenses

This code is licensed under the Affero GPL, version 3.0 or later [LICENSE](LICENSE).
The SIF Header format is licesed by [Sylabs](https://github.com/sylabs/sif/blob/master/pkg/sif/sif.go).
