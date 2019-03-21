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
