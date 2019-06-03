# Overview

## What is it?

Ultinous Video Analysis Platform (UVAP) is a set of software services that can be composed and extended in a flexible way to build scaleable, distributed **video processing applications** in multiple domains such as **retail**, **security** or **elderly care**. UVAP can be easily extended with custom components.

## Video analysis capabilities

UVAP provides a rich set of **deep learning based advanced video analysis** models. These models are industry leading in accuracy along with efficient processing. The available core models are:

- head/face detection
- 3D head pose
- face recognition, re-identification
- full body re-identification
- age
- gender
- human body pose
- tracking
- pass detection, counting

##  Example use cases

TODO: list example use cases that has been implemented with UVAP


# Architecture

UVAP implements a **dataflow programming model** where the data is processed by multiple simple processors (potentially running on different hosts) connected by channels. This model is widely used in the video processing domain for example in [ffmpeg](https://ffmpeg.org) or [gstreamer](https://gstreamer.freedesktop.org). UVAP uses [Apache Kafka](https://kafka.apache.org) for data channels and [Docker](https://www.docker.com) to run the processors. These technologies provides a generic and flexible framework to build stream processing applications.

However

but it has certain limitations. If we want to exchange large uncompressed video frames between processing nodes it needs a very high throughput channel.



TODO: explain two dataflow, mgr

The **microservice** term is used in the rest of the document for processors. The main use case of UVAP is real-time video analysis where all processors run continuously processing potentially never ending data. A microservice can take zero or more kafka topics as input and produce zero or more kafka topics as output. In kafka terminology they are consumers, producers or stream processors. Microservices are packaged and run as docker containers. Microservices typically process data in real-time, however it is possible to run them on historical data.

The data channels between microservices are **Kafka topics**. Head of the topics are kept in persistent storage for configurable time or size. For example the user can configure to keep the last two weeks of video data and keep all object detentions for a year.

![](uvap_architecture.gif)
*Fugire 1. Data flow architecture of UVAP. Rectangles are data channels, ellipses are processing units.*

# Data model
TODO:
- normalized
- topic naming
- storage formats (json, jpeg, etc)
- about keys
- examples
- reference to proto

[formal data model def](../../../../../proto_files/ultinous/proto/common/kafka_data.proto)

# Microservices

## - [Multi graph runner (MGR)](microservices/mgr/mgr.md)
## - [Tracker](microservices/mgr/tracker.md)
## - [Pass detector](microservices/mgr/passdet.md)

# Examples

# Extending UVAP

# Tutorial
