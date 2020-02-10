---
id: uvap_example_analysis
title: Example Analysis Results
hide_title: true
---

# Example Analysis Results

## Introduction

This document provides an example for the analysis results
you can create with UVAP.
You can check the syntax and contents of the resulting Kafka® topics even without
installing a camera.
Developers working on their own applications can start testing them on these topics,
in parallel with setting up their own UVAP instance to produce similar results.

Two video streams were recorded and analyzed and the following results are provided:

- head detection
- 3D head pose
- age
- gender
- facial feature vectors
- people tracking
- pass detection

In addition, anonymization for one stream and skeleton key points for the other are also provided.

We have packed these results into two Docker images.

For the notations used in this document, see [Typographic Conventions].

## Requirements

### System

To have a Kafka instance and the UVAP Kafka topics in it, the
following system requirements must be met:
- Operating system: Ubuntu Linux 18.04 LTS
- A unix account that can gain root privileges with `sudo`
- Free disk space for Docker images: ~2.3 GiB
- Free disk space for Docker volumes: ~1 GiB

### Docker

We use a containerized solution provided by Docker.

1. Install the following packages:
   
   ```
   $ sudo apt install curl adduser software-properties-common jq
   ```
   
1. Add Docker source to the apt repositories

   ```
   $ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
     sudo apt-key add -
   $ sudo add-apt-repository "deb [arch=amd64] \
     https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
   $ sudo apt-get install docker-ce
   ```
   
1. Add your unix user to the Docker unix group  
   Replace `[USER]` with your logged in user name:
   
   ```
   $ sudo adduser [USER] docker
   ```
   
1. Log out from the graphical environment (or TTY) and log in again to make
   the previous step take effect.

### Permissions

If you completed the [Installation Guide], you should
already have access to the `ultinous/kafka_demo` DockerHub repository and you
can skip this section to continue with the [Starting Docker Containers].

#### Requesting Access to the DockerHub Repository  

DockerHub access:

1. Create a Docker account on
   <a href="https://hub.docker.com/" target="_blank">Docker Hub</a>.

   > **Attention!**  
   The password of the Docker account is stored on the computer in a plain-text
   format, so it is recommended to choose a strong auto-generated password that
   is not used anywhere else.
   
1. Log in to your Docker account

   ```
   $ docker login
   ```

1. Send an email to support@ultinous.com with the following details:

   - Subject of email: `UVAP - Requesting access to ultinous/kafka_demo DockerHub repository`
   - The DockerHub account ID, created previously

## Starting Docker Containers

All the Docker images needed can be pulled from the Ultinous DockerHub
repositories, so no extra Docker credentials are needed.
Create and start the necessary Docker containers from these Docker images with the following shell commands:

1. Create a separate internal Docker network:

    ```
    $ docker network create uvap
    ```
	
1. Create the Docker container with the data of Zookeeper:

    ```
    $ docker create --name=zookeeper-data \
      ultinous/kafka_demo:zookeeper_latest :
    ```
	
1. Start / restart a Zookeeper container:

    ```
    $ docker rm -f zookeeper # Not necessary if not running
    $ docker run --net=uvap -d \
      --name=zookeeper -e ZOOKEEPER_CLIENT_PORT=2181 \
      --volumes-from zookeeper-data confluentinc/cp-zookeeper:4.1.0
    ```
	
1. Increase the retention time of the topics (i.e. infinite):

    ```
    $ for topic in $(docker exec zookeeper kafka-topics --list \
      --zookeeper zookeeper:2181) ; do docker exec zookeeper \
      kafka-configs --zookeeper zookeeper:2181 --alter --entity-type \
      topics --entity-name ${topic} --add-config \
      retention.ms=-1 ; done
    ```
	
1. Create the Docker container with the data of Kafka:

    ```
    $ docker create --name=kafka-data ultinous/kafka_demo:kafka_latest :
    ```
	
1. Start / restart a Kafka container:

    ```
    $ docker rm -f kafka # Not necessary if not running
    $ docker run --net=uvap -d -p 9092:9092 --name=kafka \
      --volumes-from kafka-data \
      -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 \
      -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092 \
      -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
      -e ZOOKEEPER_CLIENT_PORT=2181 confluentinc/cp-kafka:4.1.0
    ```
	
1. Remove the data containers, since those are not necessary anymore:

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
   
## Listing Analysis Result Topics

After the necessary Docker containers are created and started, the Kafka topics included in this example can be listed.

### List Topics

```
$ docker exec kafka kafka-topics --list --zookeeper zookeeper:2181
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

### List Messages from a Topic  

Example of message listing:

```
$ docker exec kafka kafka-console-consumer \
  --bootstrap-server kafka:9092 \
  --topic uvapdemo.cam.117.fvecs.FeatureVectorRecord.json \
  --from-beginning
```

## Cleaning Up

When they are no longer needed, the Kafka topics can be removed with the following commands:

```
$ docker container inspect --format '{{json .Mounts}}' kafka zookeeper \
  | jq --raw-output '.[].Name' > /tmp/kafka_volumes_list.txt
$ docker container stop kafka zookeeper
$ docker container rm kafka zookeeper
$ for volume in $(cat /tmp/kafka_volumes_list.txt); do docker volume \
  rm ${volume}; done
$ rm /tmp/kafka_volumes_list.txt
```

[Typographic Conventions]: ../help/uvap_notations.md
[Installation Guide]: ../install/uvap_install_setup.md
[Starting Docker Containers]: #starting-docker-containers
