FROM continuumio/miniconda3
MAINTAINER vsochat@stanford.edu

# docker build -t vanessa/container-tree .

ENV DEBIAN_FRONTEND noninteractive
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

RUN apt-get update 
RUN apt-get -y install vim jq aria2 nginx

ENV PATH /opt/conda/bin:$PATH

# Install containertree
RUN /opt/conda/bin/pip install --upgrade pip && \
    /opt/conda/bin/pip install containertree

# Clean up
RUN apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Generate the base tree to store!
RUN mkdir -p /code
ADD . /code
WORKDIR /code
RUN /opt/conda/bin/python /code/examples/summary_tree/generate.py /code/database.pkl

EXPOSE 9779
ENTRYPOINT ["/opt/conda/bin/python", "/code/examples/summary_tree/run.py"]
