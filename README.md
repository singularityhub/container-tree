# Container Tree

This is a library that demonstrates using the [Container API](https://singularityhub.github.io/api/) served by the Singularity Hub robots! Specifically, we can use the API
to grab lists of container files on Singularity Hub, and then using the
[ContainerTree](containertree/tree.py) classes, generate a [Trie](https://en.wikipedia.org/wiki/Trie) to represent the file hierarchy.

## ContainerTree
The `ContainerTree` class is a generic class that expects the input data to be json, 
either from a file or a http address. The json should have a list of dictionaries, each dictionary representing a complete filepath (e.g., `/etc/ssl`). The key "Name" is required
in the dictionary to identify the file. If you want to create a subclass, you can
define any additional parsing needed for your input under a function called `_load`.
It should check that `self.data` is not None, and if not, expect it to be
loaded json from the input. You can continue parsing it and save again the final
result to `self.data`. See `ContainerDiffTree` for an example.


## ContainerDiffTree
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

We are only interested in the list under "Analysis."


## Example
This example is also provided in [example.py](example.py)

```python
from containertree import ContainerDiffTree
import requests

# Path to database of container-api 
database = "https://singularityhub.github.io/api/files"
containers = requests.get(database).json()
entry = containers[0]  

# Google Container Diff Structure
tree = ContainerDiffTree(entry['url'])

# To find a node based on path
tree.find('/etc/ssl')
# Node<ssl>

# Trace a path, returning all nodes
tree.trace('/etc/ssl')
# [Node<etc>, Node<ssl>]
```

