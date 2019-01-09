FROM golang:1.11.3-stretch
MAINTAINER vsochat@stanford.edu

# docker build -f docker/Dockerfile -t singularityhub/container-tree .

ENV DEBIAN_FRONTEND noninteractive
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

LABEL "com.github.actions.name"="container-tree GitHub Action"
LABEL "com.github.actions.description"="use Container-Tree in Github Actions Workflows"
LABEL "com.github.actions.icon"="eye"
LABEL "com.github.actions.color"="green"

LABEL "repository"="https://www.github.com/singularityhub/container-tree"
LABEL "homepage"="https://www.github.com/singularityhub/container-tree"
LABEL "maintainer"="@vsoch"

RUN apt-get update && \
    apt-get -y install vim jq aria2 nginx python3 python3-dev \
    automake git locales && \
    wget https://bootstrap.pypa.io/get-pip.py && \
    python3 get-pip.py && \
    pip install setuptools

# Install Container-Diff
RUN go get github.com/GoogleContainerTools/container-diff && \
    cd ${GOPATH}/src/github.com/GoogleContainerTools/container-diff && \
    go get && \
    make && \
    go install && \
    mkdir -p /code && \
    apt-get autoremove && \
    mkdir -p /root/.docker && \
    echo {} > /root/.docker/config.json

# Clean up
RUN apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN mkdir -p /code
ADD . /code
WORKDIR /code
RUN python3 setup.py install && \
    chmod u+x /code/docker/entrypoint.sh

EXPOSE 9779

ENTRYPOINT ["/code/docker/entrypoint.sh"]
