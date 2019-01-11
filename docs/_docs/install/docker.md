---
title: Container Tree in Docker
category: Installation
order: 2
---

To use the Docker container, you should first ensure that you have
 [installed Docker](https://www.docker.com/get-started) on your computer.

For the container we will use, we currently provide a container hosted 
at [singularityhub/container-tree](http://hub.docker.com/r/singularityhub/container-tree) that you can use to 
quickly use the python module without any installation of other dependencies
or compiling on your host. 

When you are ready, try running {{ site.title }} using it. This first command will
shell you inside the container to use python interactively:

```bash
$ docker run {{ site.docker }}

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

It might also be desired to shell into the container (bash)

```bash
$ docker run -it --entrypoint bash {{ site.docker }} 
bash-4.4#
```

This is the Docker container that drives Github Actions to generate container
trees for your Github pages. See the [example](https://www.github.com/vsoch/containertree). 
