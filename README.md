# Container Tree

[![DOI](https://zenodo.org/badge/134179762.svg)](https://zenodo.org/badge/latestdoi/134179762)
[![DOI](http://joss.theoj.org/papers/10.21105/joss.01418/status.svg)](https://doi.org/10.21105/joss.01418)
[![CircleCI](https://circleci.com/gh/singularityhub/container-tree.svg?style=svg)](https://circleci.com/gh/singularityhub/container-tree)

This is a library that demonstrates different methods to build container trees. 
Across different kinds of trees, we generate a [Trie](https://en.wikipedia.org/wiki/Trie) 
to represent a file or container hierarchy. We can either generate 
[trees](https://singularityhub.github.io/container-tree/examples/files_tree/demo/), 
or [comparison matrices](https://singularityhub.github.io/container-tree/examples/heatmap/demo/) 
using them! Learn more by reading the documentation, or follow links to related tools below.

  - [Documentation](https://singularityhub.github.io/container-tree/)
  - [Getting Started](https://singularityhub.github.io/container-tree/getting-started/)
  - [Visualizations](#visualizations)
  - [Github Actions](#github-actions): deploy a container tree alongside your container recipes

If you want to jump in, check out how to create a [Container File Tree](https://singularityhub.github.io/container-tree/pages/demo/tree/) as shown [here](https://vsoch.github.io/containertree).

# Visualizations

These are under development! Here are some quick examples:

![examples/heatmap/heatmap.png](examples/heatmap/heatmap.png)

 - [General Tree](https://singularityhub.github.io/container-tree/pages/demo/tree/)
 - [Files Tree](https://singularityhub.github.io/container-tree/pages/demo/files_tree/)
 - [Shub Tree](https://singularityhub.github.io/container-tree/pages/demo/shub_tree/)
 - [Heatmap](https://singularityhub.github.io/container-tree/pages/demo/heatmap/)


# Github Actions

If you want to deploy a container tree to Github pages alongside your Dockerfile,
meaning that you can add and update a visualization on every change to your
repository, see [vsoch/containertree](https://www.github.com/vsoch/containertree)
and the tree it deploys [here](https://vsoch.github.io/containertree). The
[Dockerfile](docker/Dockerfile) in the subfolder here is the driver to 
do the extraction. To read a writeup of the work, see 
[this post](https://vsoch.github.io/2019/github-deploy/).


The examples and their generation are provided in each of the subfolders of the [examples](examples) directory.
