FROM continuumio/miniconda3

RUN apt-get update && apt-get install -y git && \
    git clone -b add/collection-tree-export https://www.github.com/singularityhub/container-tree.git && \
    cd container-tree && \
    python setup.py install && \
    cd examples/collection_tree && \
    python generate_filesystem.py
