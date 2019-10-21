---
id: uvap_install_setup
title: Setting Up UVAP
hide_title: true
---

# Setting Up UVAP

This instruction page is intended to guide through the initial installation
of UVAP. This procedure has to be executed only once. For upgrade instructions,
see [Upgrading UVAP].

All shell commands in the UVAP Documentation have to run successfully.
Always check the return value of an issued command (`echo $?`). If a
command fails (returns a non-zero return value), do not proceed.
Instead, examine the error message printed by the issued command, and
make any steps necessary for the command to succeed. Ask for help via
email (sent to `support@ultinous.com`), if for any reason you can not
deal with the problem on your own.

## Prerequisite

Before starting the installation, ensure that the hardware and software requirements are met according to [System Requirements].

## Creating UVAP User

Before installing the components of UVAP, create a user named `ultinous`,
and add it to the `sudo` group. To do so:

1. Create `ultinous` user:

   ```
   $ sudo adduser ultinous
   ```
   
1. Add the user to the `sudo` group:

   ```
   $ sudo adduser ultinous sudo
   ```
   
1. Change user on graphical environment (log out, then log in with `ultinous`
   user).

## Downloading Helper Scripts

To make the download and configuration of UVAP related data files easier,
clone the UVAP repository and fetch the provided helper scripts:

```
$ cd ~
$ git clone https://github.com/Ultinous/uvap.git uvap
$ export UVAP_HOME=~/uvap
$ echo "export UVAP_HOME=${UVAP_HOME}" >> "${HOME}/.bashrc"
```

Check the `README.md` file for a brief overview of this repository.

## Installing NVIDIA Video Driver

UVAP requires a specific GPU driver installed to run properly. To install
NVIDIA video driver:

1. Add the `graphics-drivers/ppa` repository to the APT:

   ```
   $ sudo add-apt-repository ppa:graphics-drivers/ppa
   $ sudo apt update
   ```
   
1. Install NVIDIA video driver:

   ```
   $ sudo apt install nvidia-driver-410
   ```
   
1. Reboot the node to use the new driver (and log in with `ultinous` user).


## Adding Docker Environment

UVAP uses a containerized solution provided by Docker. This also has to be
extended with an NVIDIA driver related add-on.

1. Add Docker source to the APT repositories:
   
   ```
   $ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
     sudo apt-key add -
   $ sudo add-apt-repository "deb [arch=amd64] \
     https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
   $ sudo apt-get install docker-ce
   ```
   
1. Add the `ultinous` user to `docker` UNIX group:
   
   ```
   $ sudo adduser ultinous docker
   ```

1. Log out from the graphical environment and log in again, so the previous step will take effect.

1. On the server machine, enable `nvidia-persistenced` to prevent the sleep
   state of the GPU:

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

1. Install NVIDIA Docker:

   ```
   $ curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | \
     sudo apt-key add -
   $ distribution=$(. /etc/os-release; echo ${ID}${VERSION_ID})
   $ curl -s -L https://nvidia.github.io/nvidia-docker/${distribution}/nvidia-docker.list \
     | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
   $ sudo apt-get update
   $ sudo apt-get install nvidia-docker2
   $ sudo systemctl restart docker
   ```

1. Test the Docker environment:

   ```
   $ nvidia-docker run --rm nvidia/cuda:10.0-runtime-ubuntu18.04 \
     nvidia-smi --query-gpu="gpu_name" --format="csv,noheader"
   ```

   You should see the list of the names of the GPU devices, for example: 

   ```
   GeForce GTX 1050 Ti
   GeForce GTX 1060 Ti
   ```

1. After the NVIDIA testing, the `nvidia/cuda` docker image is unnecessary.
   Remove the Docker Image:
   
   ```
   $ docker image rm nvidia/cuda:10.0-runtime-ubuntu18.04
   ```

## Starting Kafka

UVAP provides several sample streams over Kafka where the integrator can
connect to and implement some custom solutions based on the streams coming out.
The way how Kafka is started is just an example, which can be easily and quickly
carried out. The developer guide covers the necessary steps to permanently
install and configure a Kafka environment that is suitable for production use
cases. The following steps should be performed in a single boot up period of the
node. After a reboot, start over each step.

1. Edit `/etc/hosts` file: add `zookeeper` as name for `127.0.0.1`:

   ```
   $ echo -e -n "\n127.0.0.1 zookeeper\n" | sudo tee -a /etc/hosts
   ```

1. Create a separate internal Docker network:

   ```
   $ docker network create uvap
   ```
   
   Later, for each Docker container created in this network, Docker automatically
   creates a DNS name (resolvable inside this network). The created DNS name is
   the name of the Docker container, and has the address of the Docker container.

1. Start or restart a Zookeeper container:

   ```
   $ docker rm -f zookeeper # Not necessary if not running
   $ docker run --net=uvap -d --name=zookeeper \
     -e ZOOKEEPER_CLIENT_PORT=2181 confluentinc/cp-zookeeper:4.1.0
   ```
   
1. Start / restart a Kafka container: 

   ```
   $ docker rm -f kafka # Not necessary if not running
   $ docker run --net=uvap -d -p 9092:9092 --name=kafka \
     -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 \
     -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092 \
     -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
     -e KAFKA_MESSAGE_MAX_BYTES=10485760 \
     -e ZOOKEEPER_CLIENT_PORT=2181 confluentinc/cp-kafka:4.1.0
   ```

1. Wait 30 seconds then check if the containers are still running:

   ```
   $ docker container inspect --format '{{.State.Status}}' kafka zookeeper
   ```
   
   Expected output:
   
   ```
   running
   running
   ```
   
1. Test Kafka configuration:

   1. Create a Kafka topic:

      ```
      $ docker exec kafka kafka-topics --create \
        --zookeeper zookeeper:2181 --replication-factor 1 --partitions 1 \
        --topic test
      ```

      Expected output:  

      ```
      Created topic "test".
      ```

   1. Test the stream:

      ```
      $ docker exec kafka /bin/bash -c \
        'RND="${RANDOM}${RANDOM}${RANDOM}"; echo $RND | \
        kafka-console-producer --broker-list localhost:9092 --topic test \
        > /dev/null && kafka-console-consumer --bootstrap-server \
        localhost:9092 --topic test --from-beginning --timeout-ms 1000 \
        2> /dev/null | grep -Fq $RND; if [ $? -eq 0 ]; then echo OK; \
        else echo ERROR; fi'
      ```

      It is expected to print `OK`. Running it the first time can also print a
	  warning which is not a problem and can be ignored.

## Installing UVAP

The following script collects all Docker images for UVAP.

Run the install script:

   ```
   $ "${UVAP_HOME}/scripts/install.sh"
   ```

## Additional Tools

There are some useful utilities which can be handy during the testing.

### Installing VLC

**VLC** is a video playback application to test live stream or playback a
pre-recorded file.

To install VLC:

   ```
   $ sudo apt-get install vlc
   ```

### Installing ffmpeg

**ffmpeg** is a command line tool which can convert between different video formats
and codecs.

To install ffmpeg:

   ```
   $ sudo apt-get install ffmpeg
   ```

[License Key]: uvap_install_license.md
[System Requirements]: uvap_install_sysreq.md
[Upgrading UVAP]: ../upgrade/uvap_upgrade.md
