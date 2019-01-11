---
title: Classes
category: Getting Started
order: 2
---

There are several classes under the 
[tree](https://github.com/singularityhub/container-tree/tree/master/containertree/tree) 
module that you might be interested
in using. Before reading usage for any particular class, it's good to get
an understanding of the one you might need in these sections. If you 
are a user, start with reading about [Classes](#classes) below. If you are a 
developer, you might be more interested in the [Abstract classes](#abstract-classes).


## Classes

The set of classes below are likely what you want to import and use in Python.

### ContainerFileTree

The Container File Tree will create a tree that describes one or more containers,
where each node is a folder in the path. See the [tutorial]({{ site.url }}{{ site.baseurl }}/examples/files_tree/)
for a walk through and example nodes.

### Container Package Trees

Container Package Trees include `ContainerPipTree` and `ContainerAptTree`
and generally describe trees where the nodes
represent packages and versions. These trees can also be mapped with one
or more containers, and are an ideal data structure to store a representation
of packages across containers. From the container Apt or Pip tree you can easily 
compare containers based on packages within, or export a feature matrix
with containers (rows) by packages (columns).

 - [ContainerPackageTrees tutorial]({{ site.url }}{{ site.baseurl }}/examples/package_tree/)


### CollectionTree

A container Collection Tree represents nodes as container namespaces, and each
node contains a dictionary of the possible tags for the general namespace.
These trees are ideal for representing relationships between large sets of containers,
and can also be used to calculate comparisons via distances in the tree.

 - [CollectionTree tutorial]({{ site.url }}{{ site.baseurl }}/examples/collection_tree/)


## Abstract Classes

If you are a developer, you might be interested to read about the Abstract
classes that underly the different kinds of container trees. The base of all
classes is the `ContainerTreeBase`, and the base of packages that use Google's
[Container-Diff](https://www.github.com/GoogleContainerTools/container-diff/)

### ContainerTree

The `ContainerTree` class is a subclass of `ContainerTreeBase` that expects
to build a file system tree to describe one or more containers. The json input
should have a list of dictionaries, each dictionary representing a complete 
filepath (e.g., `/etc/ssl`). The key "Name" is required in the dictionary to 
identify the file. This class might be suited for you if you have a custom

### ContainerTreeBase

The `ContainerTreeBase` class is a base class that can read in general lists,
json, http, or other input data. The function to generate the tree, `_make_tree`,
is not defined and must be implemented by the subclass. 
If you want to create a subclass, you can define any additional parsing needed 
for your input under a function called `_load`. It should check that `self.data` 
is not None, and if not, expect it to be loaded json from the input. 
You can continue parsing it and save again the final result to `self.data`. 
See `ContainerDiffTree` for an example.

### ContainerDiffTree

This is a subclass of `ContainerTree`, specifically with an added `_load` function
to additionally parse the data loaded by the base ContainerTree class to support 
the data structure exported by container diff, which is a list with the expected
structure under "Analysis". For example:

```bash
[ {
  'Analysis': [
   ...
      {'Name': '/etc/ssl/certs/93bc0acc.0', 'Size': 1204},
      {'Name': '/etc/ssl/certs/9479c8c3.0', 'Size': 1017},
   ...],
  'AnalyzeType': 'File',
  'Image': '/tmp/tmp.qXbcpKCWxg/c2f46186d20ce41a1e1cad7b362ad9f6a5b679cd6535e865c4170cc93f4501a4.tar'}]
```

We are only interested in the list under "Analysis," and the kind of analysis
might be File, Apt, or Pip. It's unlikely that you'll instantiate a ContainerDiffTree,
but you might instantiate a ContainerFileTree or ContainerPipTree.
