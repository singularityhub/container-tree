# Collection Tree

This folder contains (script) examples for creating a collection tree, along
with the pickled collection trees generated from the dockerfiles listings in this
same folder.

### 1. Generate Collection Tree

 - [dockerfile-pairs.pkl](dockerfile-pairs.pkl) is the saved pickle file of pairs of child and parent containers derived from the [2017 Dinosaur Dataset](https://www.github.com/vsoch/dockerfiles). The data was saved to my filesystem so I keep the pairs here for the record and to be able to rebuild the tree.
 - [generate.py](generate.py) uses the pairs to generate a collection tree.
 - [container-collection-tree-final.pkl](container-collection-tree-final.pkl) is the collection tree


### 2. Generate Collection Tree Filesystem

...in a container! Here will we export the collection tree as paths, and write them to a filesystem in a container.
We do this by way of loading the tree during container build, and then generating the paths from those
loaded.

 - [Dockerfile](Dockerfile): is the Dockerfile to build the filesystem using:
 - [generate_filesystem.py](generate_filesystem.py): loads the tree and creates the subfolders in the container


You can build the container:

```bash
docker build -t vanessa/collection-tree-fs .
```

And then shell inside to see the filesystem tree:

```bash
$ docker run -it vanessa/collection-tree-fs
(base) root@c1e3d68bac93:/scratch# tree
.
└── library
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
(base) root@c1e3d68bac93:/scratch# 
```
