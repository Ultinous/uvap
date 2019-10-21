---
id: uvap_install_sysreq
title: System Requirements
hide_title: true
---

# System Requirements

This document describes the minimum hardware and software requirements to install the UVAP in 
a demo environment. This is a standalone installation without need to
access anything remotely. However the installation requires internet access and access to some
Ultinous repositories.

## Hardware Requirements

The following table includes all the minimum necessary hardware requirements to
be able to use UVAP. The following configurations defines three different levels
of performance which can be used for testing. Tests can be run with a USB or IP
camera, as well as with a pre-recorded video stream.  
The test node can even be a laptop that contains the necessary components, like
a high-performance laptop with the required processor and GPU.

### Camera

| Camera Type | Example                                |
| ----------- | -------------------------------------- |
| USB Camera  | Logitech BRIO                          |
| IP Camera   | Hikvision IP camera with HD resolution |

### Server

#### Small Node

| Part       | Spec                                      |
| ---------- | ----------------------------------------- |
| CPU        | Intel i5-6500 3200MHz                     |
| RAM        | 8GB                                       |
| Video card | NVIDIA GeForce GTX1060 with 6G GPU memory |
| Storage    | 500GB                                     |

#### Medium Node

| Part       | Spec                      |
| ---------- | ------------------------- |
| CPU        | Intel Xeon E5-1650 3.6GHz |
| RAM        | 16GB                      |
| Video card | NVIDIA GeForce GTX1080    |
| Storage    | 500GB                     |

## Software Requirements

UVAP runs on Ubuntu Linux 18.04 LTS. The desktop edition is recommended, as
it could be necessary to be able to play back videos or display pictures for
checking the source stream or the results. Virtualization systems that do not
support GPU devices (for example, Windows Subsystem for Linux (WSL), VMware or
VirtualBox) are not suitable for running the components described in the
documentaion. To install Ubuntu Linux 18.04 LTS on the node, follow the
<a href="https://tutorials.ubuntu.com/tutorial/tutorial-install-ubuntu-desktop" target="_blank">Ubuntu installation tutorial</a>.

Bash is the preferred shell program when executing shell commands of the UVAP Documentation. 
You may use another shell of your choice but in that case adjustments in the 
shell commands may need to be made in some cases.

### Notations

For the notations used in this document, see [Typographic Conventions].

## Required Packages

Some Ubuntu (Debian) packages are required to be installed in order to steps of
UVAP guides work.  
Install these packages with the following command:

```
$ sudo apt install coreutils adduser git curl wget jq tar \
    software-properties-common gettext-base v4l-utils
```

Make sure, that _bash_ is installed with a version number at least 4.0 with
the following command:

```
$ dpkg-query --show bash
```

Expected output showing that _bash_ is installed with version _4.4.18-2ubuntu1.2_:

```
bash	4.4.18-2ubuntu1.2
```

[Typographic Conventions]: ../help/uvap_notations.md
