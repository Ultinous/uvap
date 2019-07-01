# Overview

## What is UVAP?

Ultinous Video Analysis Platform (UVAP) is a set of software services that can be composed and extended in a flexible way to build scaleable, distributed **video processing applications** in multiple domains such as **retail**, **security** or **elderly care**.

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

UVAP has been used to solve real world problems in different domains. Some examples:

- Queue management system for retail stores. Customers are counted at the doors and in the queuing area in real-time. A prediction model can tell if there will be a queue in the next few minutes and staff is alerted before it happens.

- Fall detection in elderly care homes. The system uses two 3D calibrated cameras per room and runs human body pose estimation. Based on the body pose fallen body pose can be recognized. An alert is sent to the staff in real-time. Staff personals can look at the alert, validate the images and decide to take action.

- Measure waiting time on Airports. Face recognition is applied at the entrance and exit points in real-time to measure actual waiting time. Prediction is applied and displayed to customers entering the queue.

- Recognize unsafe escalator usage. Based on head detection, tracking and full body pose different unsafe situations are recognized such as: wrong direction, leaning out, crowd.

# Architecture

UVAP implements a **dataflow programming model** where the data is processed by multiple simple processors (potentially running on different hosts) connected by channels. This model is widely used in the video processing domain for example in [ffmpeg](https://ffmpeg.org) or [gstreamer](https://gstreamer.freedesktop.org). UVAP uses [Apache Kafka](https://kafka.apache.org) for data channels and [Docker](https://www.docker.com) to run the processors. These technologies provides a generic and flexible framework to build stream processing applications.

The **microservice** term is used in the rest of the document for processors. The main use case of UVAP is real-time video analysis where all processors run continuously processing potentially never ending data. A microservice can take zero or more kafka topics as input and produce zero or more kafka topics as output. In kafka terminology they are consumers, producers or stream processors. Microservices are packaged and run as docker containers. Microservices typically process data in real-time, however it is possible to run them on historical data.

The data channels between microservices are **Kafka topics**. Head of the topics are kept in persistent storage for configurable time or size. For example the user can configure to keep the last two weeks of video data and keep all object detentions for a year.

![](uvap_architecture.gif)
*Fugire 1. Data flow architecture of UVAP. Rectangles are data channels, ellipses are processing units.*

[Multi graph runner (MGR)](microservices/mgr/mgr.md) takes the video streams and runs all deep learning based image processing models (eg.: head detection, face recognition). [MGR](microservices/mgr/mgr.md) outputs only lightweight data such as head detection streams or face recognition feature vectors. **It is very important the uncompressed video data never transfered over kafka, all low level image processing is done inside [MGR](microservices/mgr/mgr.md).** Kafka is only used to exchange lightweight data.

# Data model
As shown in *Figure 1.* the microservices are connected via kafka topics. This section provides information about the schema and format of these topics.

Normalized model. Use keys to join. TODO: describe in detail
End of frames, heartbeats.

## Topic naming convention

TODO: describe formal convention

Example:
```
demo.cam.1.skeletons.SkeletonRecord.json
```

## Topic formats

json, jpeg

TODO: describe in detail

## Topic schemas

[formal data model def](../../../../../proto_files/ultinous/proto/common/kafka_data.proto)

# Microservices

## [Multi graph runner (MGR)](microservices/mgr/mgr.md)

Future versions of UVAP will contain many more microservices such as tracking and reidentification.

# Tutorial

# Extending UVAP
