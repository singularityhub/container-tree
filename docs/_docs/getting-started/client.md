---
title: Container Tree Client
category: Getting Started
order: 3
---

Container Tree can be used locally, or with Docker. Both are described below.


# Local

Container Tree provides a command line executable to quickly generate
a container tree. After you [install](https://singularityhub.github.io/container-tree/install/local/)
containertree, you can see the client with the command line executable "containertree":

```bash
$ containertree

ContainerTree v0.0.43
usage: containertree [-h] [--debug] [--quiet] [--version]
                     {templates,generate} ...

ContainerTrees in Python

optional arguments:
  -h, --help            show this help message and exit
  --debug               use verbose logging to debug.
  --quiet               suppress additional output.
  --version             print version and exit.

actions:
  actions for ContainerTree Python

  {templates,generate}  containertree actions
    templates           View available tree templates
    generate            Generate a container tree.
```

## Version

You can see the version installed:

```bash
$ containertree --version
0.0.43
```

## Generate a Container Tree for a Docker URI

To run this command locally, you should have [container-diff](https://github.com/GoogleContainerTools/container-diff)
installed. If you don't want to do this, see the [docker](#docker) container
client instructions below.

```bash
$ containertree generate vanessa/salad
DEBUG ContainerTree<17629>
DEBUG Webroot: /tmp/containertree-447sjt_d
DEBUG Exporting data for d3 visualization
```

The default will generate the tree, and show you the output folder. You can
go there and start a temporary server to see your tree:

```bash
$ cd /tmp/containertree-447sjt_d
$ ls
data.json  index.html
$ python -m http.server 9999
Serving HTTP on 0.0.0.0 port 9999 (http://0.0.0.0:9999/) ...
```

![https://vsoch.github.io/assets/images/posts/container-tree/containertree.png](https://vsoch.github.io/assets/images/posts/container-tree/containertree.png)

You can also just add `--view` to have the web server created for you:

```bash
$ containertree generate vanessa/salad --view
DEBUG ContainerTree<17629>
DEBUG Webroot: /tmp/containertree-pn4kwnkb
DEBUG Exporting data for d3 visualization
Serving at localhost:9779
```

Then you would open your browser to [http://localhost:9779](http://localhost:9779).

## Output to Console

If you simply want to print the data.json and index.html to the terminal, you can do that too:

```bash
$ containertree generate vanessa/salad --print index.html
$ containertree generate vanessa/salad --print data.json
...
'color': '#7F007F', 'key': 'run', 'name': 'run', 'tags': [], 'attrs': {'label': 'run', 'name': '/var/run', 'size': 4, 'leaf': True, 'tags': [], 'counter': 1}, 'children': [], 'size': 4}, {'color': '#FF0000', 'key': 'spool', 'name': 'spool', 'tags': [], 'attrs': {'label': 'spool', 'name': '/var/spool', 'size': 13, 'leaf': True, 'tags': [], 'counter': 3}, 'children': [{'color': '#FF7F00', 'key': 'cron', 'name': 'cron', 'tags': [], 'attrs': {'label': 'cron', 'name': '/var/spool/cron', 'size': 13, 'leaf': True, 'tags': [], 'counter': 2}, 'children': [{'color': '#00FFFF', 'key': 'crontabs', 'name': 'crontabs', 'tags': [], 'attrs': {'label': 'crontabs', 'name': '/var/spool/cron/crontabs', 'size': -1, 'leaf': True, 'tags': [], 'counter': 1}, 'children': [], 'size': -1}], 'size': 13}], 'size': 13}, {'color': '#0560D0', 'key': 'tmp', 'name': 'tmp', 'tags': [], 'attrs': {'label': 'tmp', 'name': '/var/tmp', 'size': 0, 'leaf': True, 'tags': [], 'counter': 1}, 'children': [], 'size': 0}], 'size': 17}], 'size': 0}
```

The idea is that you could pipe this into a file:

```bash
$ containertree generate vanessa/salad --print data.json > data.json
$ containertree generate vanessa/salad --print index.html > index.html
```

## List Templates

Most of the templtes provided take the same data.json structure and render
some form of tree (so if you want to contribute a template, it's easy to
start with this structure!  To see templates available:


```bash
$ containertree templates

Templates:

treemap
similarity_scatter
heatmap
tree
heatmap-large
files_tree
container_tree
shub_tree
```

## Specify a Different Template

And then you can specify a different template to use for your tree (note
that the defaule is files_tree, shown above).

```bash
$ containertree generate vanessa/salad --template tree
```

# Docker

You can also "install" containertree [with Docker](https://singularityhub.github.io/container-tree/install/docker/).

## Quick Demo

Generate an example file tree using the [containertree](https://cloud.docker.com/u/singularityhub/repository/docker/singularityhub/container-tree) Docker container.

```bash
$ docker run -it -p 9779:9779 singularityhub/container-tree demo
Selecting container from https://singularityhub.github.io/api/files...
Generating files tree!
ContainerTree<56386>
Webroot: /tmp/tmpizxgn5jk
Exporting data for d3 visualization
Serving at localhost:9779
```

Then open up your browser to [http://localhost:9779](http://localhost:9779).
The container is randomly selected from the Singularity Hub (static) API.

## Generate Tree from Docker URI

You can generate just static files. Notice that we are telling the container
to generate output in /data inside the container, which is mapped to 
an output folder we just created.

```bash
mkdir -p output
$ docker run -v $PWD/output:/data -it -p 9779:9779 singularityhub/container-tree generate vanessa/salad --output /data
```

Then you can see your output files, a data.json and index.html:

```bash
$ tree output
output/
├── data.json
└── index.html
```

You can start a temporary server to view the files:

```bash
cd output
python -m http.server 9999
# open localhost:9999
```

## Tree Templates

The templates provided are each web (html) files that expect a data.json tree.
To see available templates:

```bash
$ docker run singularityhub/container-tree templates
Templates:

collection_tree
treemap
similarity_scatter
heatmap
tree
heatmap-large
files_tree
container_tree
shub_tree
```

And then you can specify a template name with the `--template` argument to the
generate command. The default is a files tree.

If you have any questions or issues, please [open an issue]({{ site.repo }}/issues).
