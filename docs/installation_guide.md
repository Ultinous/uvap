# Ultinous Video Analytics Platform (UVAP) Installation Guide
## Table of contents
1. [Introduction](#introduction)
1. [Hardware requirements](#hardware_req)
   1. [Camera](#camera)
   1. [Server](#sever)
1. [Software requirements](#software_req)
   1. [Create New user for UVAP](#newUser)
   1. [Download Helper Script](#downloadHelperScripts)
   1. [Install NVIDIA video driver](#NVIDIA_driver)
   1. [Install Docker](#installDocker)
   1. [Additional tools](#additionalTools)
   1. [Starting Zookeeper and Kafka](#startZookeeperAndKafka)
1. [Private access](#privateAccess)
   1. [Collecting information for Licensing](#collectingInformationForLicensing)
   1. [Acquiring the private resources](#acquiringThePrivateResources)
1. [Install UVAP](#installUVAP)


<a name="introduction"></a>
## Introduction
This document describes the minimum hardware and software requirements to install the UVAP (Ultinous Video Analytics Platform) in a demo environment. This is a standalone installation without need to access anything remotely. However the installation requires internet access and access to some Ultinous repositories.

<a name="hardware_req"></a>
## Hardware requirements
The following table includes all the minimum necessary hardware requirements to be able to use the UVAP. The following configurations defines 3 different levels of performance which could be used for the testing.  
You can choose if you would like to test with a USB or an IP camera, but you could also use a pre-recorded video stream from a file.  
The test node can be even a laptop which contains the necessary components, like a strong gamer laptop with the necessary processor and GPU.

<a name="camera"></a>
### Camera

| Camera type | Example |
| - | - |
| USB Camera | Logitech BRIO |
| IP Camera  | Hikvision IP camera with HD resolution |

<a name="server"></a>
### Server

#### Small node

| Part | Spec |
| - | - |
| CPU | Intel i5-6500 3200MHz |
| RAM | 8GB |
| Video card | NVIDIA GeForce GTX1060 |
| Disk | 500GB |

#### Medium node

| Part  | Spec |
| - | - |
| CPU | Intel Xeon E5-1650 3.6GHz |
| RAM | 16GB |
| Video card | NVIDIA GeForce GTX1080 |
| Disk | 500GB |

<a name="software_req"></a>
## Software requirements

The UVAP runs on Ubuntu Linux 18.04 LTS. The desktop edition is recommended, as it could be necessary to be able to play back videos or display pictures for checking the source stream or the results.  
Virtualization systems that don't support GPU devices (e.g. Windows Subsystem for Linux (WSL), VmWare, VirtualBox, etc...) are not suitable for running the components of this guide.  
To install Ubuntu Linux 18.04 LTS on the node follow the installation tutorial: https://tutorials.ubuntu.com/tutorial/tutorial-install-ubuntu-desktop  
The following components should be pre-installed to be able to install the UVAP on the node.

<a name="newUser"></a>
### Create New user for UVAP

1. Create a user called ultinous
   ```
   $ sudo adduser ultinous
   ```
1. Add your user to the sudo group
   ```
   $ sudo adduser ultinous sudo
   ```
1. Change user on graphical environment (log out and log in with ‘ultinous’ user)

<a name="downloadHelperScripts"></a>
### Download helper scripts

You have to download a few helper scripts which makes it easier to download and configure the UVAP related data files.
```
$ sudo apt install git
$ cd ~
$ git clone https://github.com/Ultinous/uvap.git uvap
```
You may check the README.md file for a brief overview of this repository.

<a name="NVIDIA_driver"></a>
### Install NVIDIA video driver

The UVAP requires a specific GPU driver installed to run properly.
1. Add the graphics-drivers/ppa repository to the apt:
   ```
   $ sudo add-apt-repository ppa:graphics-drivers/ppa
   $ sudo apt update
   ```
1. Install the NVIDIA video driver
   ```
   $ sudo apt install nvidia-driver-410
   ```
1. Reboot the node to use the new driver (and log in with _ultinous_ user)

<a name="installDocker"></a>
### Docker
The UVAP uses a containerized solution provided by Docker. This also has to be extended with an NVIDIA driver related add-on.

1. Install curl to be able to download files from command line
   ```
   $ sudo apt install curl
   ```
1. Add docker source to the apt repositories
   ```
   $ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
   $ sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
   $ sudo apt-get install docker-ce
   ```
1. Add your unix user to the docker unix group
   ```
   $ sudo adduser ultinous docker
   ```
1. Reboot the node to use the previous step will take effect (and log in with _ultinous_ user).
1. Enable nvidia-persistenced to prevent the sleep state of the GPU (only on Server machine)
   ```
   $ cd /etc/systemd/system/
   $ sudo mkdir nvidia-persistenced.service.d
   $ cd nvidia-persistenced.service.d/
   $ cat | sudo tee override.conf <<EOF
   [Service]
   ExecStart=
   ExecStart=/usr/bin/nvidia-persistenced --user nvidia-persistenced --verbose
   EOF
   $ sudo systemctl daemon-reload
   $ sudo systemctl restart nvidia-persistenced.service
   ```
1. Install NVIDIA docker
   ```
   $ curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   $ distribution=$(. /etc/os-release; echo $ID$VERSION_ID)
   $ curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
   $ sudo apt-get update
   $ sudo apt-get install nvidia-docker2
   $ sudo systemctl restart docker
   ```
1. Test the docker environment
   ```
   $ nvidia-docker run --rm nvidia/cuda:10.0-runtime-ubuntu18.04 nvidia-smi
   ```
   You should see a similar output like the following:
   ```
   +-----------------------------------------------------------------------------+
   | NVIDIA-SMI 410.104      Driver Version: 410.104      CUDA Version: 10.0     |
   |-------------------------------+----------------------+----------------------+
   | GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
   | Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
   |===============================+======================+======================|
   |   0  GeForce GTX 106...  On   | 00000000:01:00.0 Off |                  N/A |
   | N/A   47C    P8     5W /  N/A |    250MiB /  6078MiB |      6%      Default |
   +-------------------------------+----------------------+----------------------+

   +-----------------------------------------------------------------------------+
   | Processes:                                                       GPU Memory |
   |  GPU       PID   Type   Process name                             Usage      |
   |=============================================================================|
   +-----------------------------------------------------------------------------+
   ```

<a name="additionalTools"></a>
### Additional tools

There are some useful utilities which can be handy during the testing
1. Vlc  
   Video playback application to test live stream or playback a pre-recorded file
   ```
   $ sudo apt-get install vlc
   ```
1. ffmpeg  
   A command line tool which can convert between different video formats and codecs
   ```
   $ sudo apt-get install ffmpeg
   ```
1. kafkacat  
   This command line tool can be used to dump kafka streams
   ```
   $ sudo apt-get install kafkacat
   ```

<a name="startZookeeperAndKafka"></a>
### Starting Zookeeper and Kafka

The UVAP provides several sample streams over Kafka where the integrator can connect to and implement some custom solutions based on the streams coming out.  
The way how Kafka is started is just an example, which can be easily and quickly carried out. The developer guide covers the necessary steps to permanently install and configure a Kafka environment that is suitable for production use cases.  
The following steps should be performed in a single boot up period of the node. After a reboot each step should be stared all over.

1. Edit your /etc/hosts file
   ```
   $ sudo sed -i 's/^127.0.0.1.*/127.0.0.1\tlocalhost zookeeper kafka/' /etc/hosts
   ```
1. Create a separate internal network for the docker-containerized environment
   ```
   $ docker network create uvap
   ```
1. Start a Zookeeper container
   ```
   $ docker rm -f zookeeper
   $ docker run --net=uvap -d --name=zookeeper -e ZOOKEEPER_CLIENT_PORT=2181 confluentinc/cp-zookeeper:4.1.0
   ```
1. Start a Kafka container
   ```
   $ docker rm -f kafka
   $ docker run --net=uvap -d -p 9092:9092 --name=kafka -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092 -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 -e ZOOKEEPER_CLIENT_PORT=2181 confluentinc/cp-kafka:4.1.0
   ```
1. Wait for 30 seconds, then check if the containers are still running:
   ```
   $ docker container inspect --format '{{.State.Status}}' kafka zookeeper
   running
   running
   ```
1. Test your kafka configuration
   1. Create a kafka topic
      ```
      $ docker exec -it kafka /bin/bash -c 'kafka-topics --create --zookeeper zookeeper:2181 --replication-factor 1 --partitions 1 --topic test'
      ```
      It should display:  
      Created topic "test".
   1. Test the stream
      ```
      $ docker exec -it kafka /bin/bash -c 'RND="${RANDOM}${RANDOM}${RANDOM}"; echo $RND | kafka-console-producer --broker-list localhost:9092 --topic test > /dev/null && kafka-console-consumer --bootstrap-server localhost:9092 --topic test --from-beginning --timeout-ms 1000 2> /dev/null | grep -Fq $RND; if [ $? -eq 0 ]; then echo OK; else echo ERROR; fi'
      ```
      It should print “OK”

<a name="privateAccess"></a>
## Private access
The components of UVAP have been protected against illegal access, so in order to be able to use all the components, some information is required to be collected and to be used to have necessary access granted.

<a name="collectingInformationForLicensing"></a>
### Collecting information for licensing

1. Collect the HW information for licence generation
   ```
   $ mkdir -p /tmp/uvap && nvidia-docker run --rm -u $(id -u) ultinous/licence_data_collector > /tmp/uvap/data.txt
   ```
1. The file `/tmp/uvap/data.txt` will be needed in a later step to proceed with the installation, so please, save it to an appropriate place.
1. On https://hub.docker.com/ please create an account for yourself. This will be required to have access to the docker images of UVAP.  
   :exclamation: **Warning** :exclamation: The password of a docker account will be stored on your computer in a plain-text format, so please use an auto-generated password, which you are using nowhere else.
1. Log in to your docker account
   ```
   $ docker login
   ```

<a name="acquiringThePrivateResources"></a>
### Acquiring the private resources

1. Please, send the following information to `support@ultinous.com`:
   1. Subject of email: `UVAP - Acquiring the private resource`
   1. Your docker hub account ID, which you have created in the previous step
   1. Your HW information, which can be found in the file `/tmp/uvap/data.txt`
1. Based on the above information you will receive:
   1. The licence
   1. Access to the docker repository `ultinous/uvap`
   1. A download URL for AI resources (valid for only 24 hours)
1. The licence is provided within 2 files:  
   E.g.: license.txt:
   ```
   Product Name    = UVAP
   GPU             = aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee
   Expiration Date = 2018-01-01
   Customer        = Demo User
   ```
   licence.key:
   ```
   --- No human readable key data ---
   ```
   Without license files you can continue the installation process until the UVAP usage.
1. Pull the following docker image
   ```
   $ docker pull ultinous/uvap:mgr_latest
   ```
1. Download the AI resources  
   In the following command, please substitute `[DOWNLOAD_URL]` with the download URL received from `support@ultinous.com`
   ```
   $ mkdir -p ~/uvap/models
   $ cd ~/uvap/models
   $ wget -q -O - "[DOWNLOAD_URL]" | tar xzf -
   ```
1. The above steps are not meant to be having yet a working environment, these only intended to quickly check that you have been granted access to all the resources you need

<a name="installUVAP"></a>
### Install UVAP
The following script collects all docker images for UVAP.
Run the install script:
```
$ ~/uvap/scripts/install.sh
```
