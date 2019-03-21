FROM continuumio/miniconda3

# docker build -t vanessa/collection-tree-fs .
# docker push vanessa/collection-tree-fs

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get install -y git \
                       tree \
                       gcc && \
    git clone -b add/collection-tree-export https://www.github.com/singularityhub/container-tree.git && \
    cd container-tree && \
    python setup.py install && \
    cd examples/collection_tree && \
    mv container-collection-tree-library-only.pkl /tree.pkl && \
    python generate_filesystem.py

WORKDIR /scratch
