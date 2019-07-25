# Example Analysis Results

## Table of contents
1. [Introduction](#introduction)
1. [Requirements](#requirements)
1. [Starting docker containers](#dockerContainers)
1. [Listing analysis result topics](#listTopics)
1. [Cleaning up](#removeData)

<a name="introduction"></a>
## Introduction
The purpose of this document is to provide an example for the analysis results you can create with UVAP.
You can check the syntax and contents of the resulting Kafka topics even without installing your camera.
If you are developing your own application, you can start testing it on these topics, in parallel with setting up your own UVAP instance to produce similar results. 

We have recorded and analysed two video streams and provide the results for
- head detection
- 3D head pose
- age
- gender
- facial feature vectors
- people tracking
- pass detection

In addition, for one of the streams, we also provide
- anonymization

For the other stream, we provide
- skeleton key points
     
We have packed the result into the docker images (zookeeper-data, kakfa-data).

For the notations used in this document, see [Notations](notations.md). 

<a name="requirements"></a>
## Requirements

### System
In order to have a Kafka instance and have the UVAP Kafka topics in it, the following system requirements are have to be met:
- Operating system: Ubuntu Linux 18.04 LTS.
- Free disk space for Docker images: ~2.3 GiB
- Free disk space for Docker volumes: ~1 GiB

### Docker
We use containerized solution provided by Docker.

1. Install curl to be able to download files from command line
   ```
   $ sudo apt install curl
   ```
1. Add docker source to the apt repositories
   ```
   $ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
   $ sudo add-apt-repository "deb [arch=amd64] \
     https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
   $ sudo apt-get install docker-ce
   ```
1. Add your unix user to the docker unix group  
   The `[USER]` should be replaced with your name of logged in user:
   ```
   $ sudo adduser [USER] docker
   ```
1. Reboot the node to use the previous step will take effect (and log in with `[USER]` user).

### Permissions

If you completed the [Installation Guide](installation_guide.md), you should already have access 
to the `ultinous/kafka_demo` DockerHub repository and you can skip this section to continue with the [next step](#dockerContainers).

#### Requesting access to the DockerHub repository  

DockerHub access:
- On https://hub.docker.com/ please create an account for yourself. :exclamation: Warning :exclamation: The password of a docker account will be stored on your computer in a plain-text format, so please use an auto-generated password, which you are using nowhere else.
- Log in to your docker account
   ```
   $ docker login
   ```
Please send the following information to `support@ultinous.com`:
- Subject of email: UVAP - Requesting access to `ultinous/kafka_demo` DockerHub repository
- Your docker hub account ID, which you have created in the previous step

<a name="dockerContainers"></a>
## Starting Docker containers
All the Docker images needed can be pulled from our DockerHub repositories, so no extra Docker credentials are needed. 
The necessary Docker containers from these Docker images can be created and started with the following shell commands:

1. Edit your /etc/hosts file: add zookeeper and kafka as names for 127.0.0.1.
    ```
    $ echo -e -n "\n127.0.0.1 kafka zookeeper\n" | sudo tee -a /etc/hosts
    ```
1. Create a separate internal network for the docker-containerized environment
    ```
    $ docker network create uvap
    ```
1. Create the docker container with data for the Zookeeper:
    ```
    $ docker create --name=zookeeper-data ultinous/kafka_demo:zookeeper_latest :
    ```
1. Start / restart a Zookeeper container
    ```
    $ docker rm -f zookeeper # Not necessary if not running
    $ docker run --net=uvap -d \
    --name=zookeeper -e ZOOKEEPER_CLIENT_PORT=2181 \
    --volumes-from zookeeper-data confluentinc/cp-zookeeper:4.1.0
    ```
1. Set retention of historical data
    ```
    $ for i in $(docker exec zookeeper kafka-topics --list --zookeeper zookeeper:2181) ; do docker exec  zookeeper kafka-configs --zookeeper zookeeper:2181 --alter --entity-type topics --entity-name ${i} --add-config retention.ms=259200000000 ; done
    ```
1. Create the docker container with recorded topics for the Kafka:
    ```
    $ docker create --name=kafka-data ultinous/kafka_demo:kafka_latest :
    ```
1. Start / restart a Kafka container
    ```
    $ docker rm -f kafka # Not necessary if not running
    $ docker run --net=uvap -d -p 9092:9092 --name=kafka \
    --volumes-from kafka-data \
    -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 \
    -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092 \
    -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
    -e ZOOKEEPER_CLIENT_PORT=2181 confluentinc/cp-kafka:4.1.0
    ```
1. Remove volumes
    ```
    $ docker rm zookeeper-data kafka-data
    ```
1. Check if the containers are still running:
   ```
   $ docker container inspect --format '{{.State.Status}}' kafka zookeeper
   ```
   Expected output:
   ```
   running
   running
   ```
<a name="listTopics"></a>
## Listing analysis result topics
Now you can list the Kafka topics included in this example.

#### List topics
```
$ docker exec -it kafka /bin/bash -c 'kafka-topics --list --zookeeper zookeeper:2181'
```
Expected output:
```
__confluent.support.metrics
__consumer_offsets
uvapdemo.cam.117.ages.AgesRecord.json
uvapdemo.cam.117.dets.ObjectDetectionRecord.json
uvapdemo.cam.117.frameinfo.FrameInfoRecord.json
uvapdemo.cam.117.fvecs.FeatureVectorRecord.json
uvapdemo.cam.117.genders.GendersRecord.json
uvapdemo.cam.117.lowres.Image.jpg
uvapdemo.cam.117.passes.PassDetectionRecord.json
uvapdemo.cam.117.poses.HeadPose3DRecord.json
uvapdemo.cam.117.tracks.TrackRecord.json
uvapdemo.cam.118.ages.AgesRecord.json
uvapdemo.cam.118.dets.ObjectDetectionRecord.json
uvapdemo.cam.118.frameinfo.FrameInfoRecord.json
uvapdemo.cam.118.fvecs.FeatureVectorRecord.json
uvapdemo.cam.118.genders.GendersRecord.json
uvapdemo.cam.118.lowres.Image.jpg
uvapdemo.cam.118.lowres_anonymized.Image.jpg
uvapdemo.cam.118.passes.PassDetectionRecord.json
uvapdemo.cam.118.poses.HeadPose3DRecord.json
uvapdemo.cam.118.skeletons.SkeletonRecord.json
uvapdemo.cam.118.tracks.TrackRecord.json
```
#### List messages from a topic  
Install "kafkacat", if it is not exist on your server:
```
$ sudo apt-get install kafkacat
```
Example of message listing:
```
$ kafkacat -C -b kafka:9092 -t uvapdemo.cam.117.fvecs.FeatureVectorRecord.json -o0
```
<a name="removeData"></a>
## Cleaning up
When you finished the work with these Kafka topics, you can remove them with the following coommands:
```
$ docker rm -f zookeeper
$ docker rm -f kafka
$ docker volume prune zookeeper-data kafka-data
```
