---
title: Export Package Data
category: Examples
order: 5
---

Why is tagging of container trees useful? If we store information at each node about the containers
that have the packages, we can parse the tree to extract data or calculate
similarity. Let's start with showing how to export package data. If you
use this feature, you will additionally need the pandas module installed.
Here are a few ways to install pandas:

```bash
pip install pandas
pip install containertree[analysis]
apt-get install -y python3-pandas
```

We would likely want to do some kind of analysis over container packages, and the
first step would be to extract a data frame. Here is how to do that. First,
create your tree and add some containers to it.

```python
from containertree.tree import ContainerAptTree

# Initilize a tree with packages from a container, add others
apt = ContainerAptTree('singularityhub/sregistry-cli', tag='singularityhub/sregistry-cli')
apt.update('library/debian', tag='library/debian')
apt.update('library/ubuntu', tag='library/ubuntu')
```

Here is how to export a pandas data frame with the packages:

```python
df = apt.export_vectors()
df.head()
                              adduser  apt  autoconf  automake  autotools-dev  \
singularityhub/sregistry-cli      1.0  1.0       1.0       1.0            1.0   
library/ubuntu                    1.0  1.0       NaN       NaN            NaN   
library/debian                    1.0  1.0       NaN       NaN            NaN  
```

The rows represent the containers, and the columns the packages. A value of
NaN indicates the package isn't installed in the container, and 1.0 indicates
that it is. Here is how to fill in 0 for the NaN values, if you prefer.

```python
df = df.fillna(0)
```

You can optionally subset to a particular set of tags, either including
only a specific set:

```python
df = apt.export_vectors(include_tags=['library/debian'])
df.head()
                adduser  apt  base-files  base-passwd  bash  bsdutils  \
library/debian      1.0  1.0         1.0          1.0   1.0       1.0   
```

or skipping specific containers:


```python
df = apt.export_vectors(skip_tags=['library/debian'])
df.head()
                              adduser  apt  autoconf  automake  autotools-dev  \
singularityhub/sregistry-cli      1.0  1.0       1.0       1.0            1.0   
library/ubuntu                    1.0  1.0       NaN       NaN            NaN 
```

Or using a regular expression to filter the tags (useful for collection names,
such as finding all containers in the "library" namespace):

```python
df = apt.export_vectors(regexp_tags="^library")
df.head()
                adduser  apt  base-files  base-passwd  bash  bsdutils  bzip2  \
library/ubuntu      1.0  1.0         1.0          1.0   1.0       1.0    1.0   
library/debian      1.0  1.0         1.0          1.0   1.0       1.0    NaN 
```

If you want more detail for your features, you can specify to include package
versions:

```python
df = apt.export_vectors(include_versions=True)
df.head()
                             adduser-v3.115  adduser-v3.116ubuntu1  \
library/debian                           1.0                    NaN   
singularityhub/sregistry-cli             1.0                    NaN   
library/ubuntu                           NaN                    1.0   
```

The same can be done for Pip (python) Package trees:

```python
from containertree import ContainerPipTree
pip = ContainerPipTree('singularityhub/container-tree', tag='singularityhub/container-tree')

pip.export_vectors()
                               configobj  mercurial  pip  setuptools  six  \
singularityhub/container-tree        1.0        1.0  1.0         1.0  1.0   

                               wheel  
singularityhub/container-tree    1.0
```

And with versions!

```python
pip.export_vectors(include_versions=True)
                               configobj-v5.0.6  mercurial-v4.0  pip-v18.1  \
singularityhub/container-tree               1.0             1.0        1.0   

                               setuptools-v40.6.3  six-v1.10.0  wheel-v0.32.3  
singularityhub/container-tree                 1.0          1.0            1.0  
```
