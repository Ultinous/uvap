---
id: uvap_extend
title: Extending UVAP
hide_title: true
---

# Extending UVAP

## Environment for Python Developers

UVAP demos run in a quick and easy-to-use Docker environment.
For more information, see [Environment].

Developers are required to have a local environment to solve real-world
problems instead of starting a few prewritten demos. This section describes
the following:

* Installation package of the `uvap_demo_applications` Docker container.
* Installation of a useful editor for Python programming language.

### Requirements

The following are required:

* Ubuntu 18.04 Bionic Beaver
* Privileged access to the Ubuntu System as root or through `sudo` command

### Python3.6

To create a similar environment as the `uvap_demo_applications` Docker
container, execute the following group of commands:

```
sudo apt-get update \
&& sudo apt-get -y install \
    kafkacat \
    python3 \
    python3-pip \
    python3-setuptools \
    mc \
    vim \
    screen \
    libsm6 \
    libxext6 \
    libxrender-dev \
&& sudo apt-get clean \
&& pip3 install \
    confluent-kafka \
    numpy \
    scipy \
    pandas \
    protobuf \
    flask \
    WSGIserver \
    sklearn \
    jsons \
    xlrd \
    opencv-python \
    gevent \
    sortedcontainers
```

### PyCharm

#### Install PyCharm using Snaps

The simplest and recommended way of installing PyCharm on Ubuntu 18.04 is to use
a snaps package manager. The following Linux command installs
**PyCharm Community** on Ubuntu 18.04 Bionic Beaver:

```
$ sudo snap install pycharm-community --classic
pycharm-community 2019.2.4 from jetbrains✓ installed
```

#### Start PyCharm

To start PyCharm from command line:

```
$ pycharm-community
```

[Environment]: ../demo/demo_overview.md#environment
