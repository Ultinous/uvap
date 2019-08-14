
# UVAP Developer's Guide
## Table of contents
1. [Overview](#overview)
1. [Architecture](#architecture)
1. [Data model](#dataModel)
1. [Microservices](#microservices)
1. [Tutorial](#tutorial)
1. [Extending UVAP](#extendingUVAP)

<a name="overview"></a>
# [Overview](../Readme.md#overview)

<a name="architecture"></a>
# Architecture

UVAP implements a **dataflow programming model** where the data is processed by multiple simple processors (potentially running on different hosts) connected by channels. This model is widely used in the video processing domain for example in [ffmpeg](https://ffmpeg.org) or [gstreamer](https://gstreamer.freedesktop.org). UVAP uses [Apache Kafka](https://kafka.apache.org) for data channels and [Docker](https://www.docker.com) to run the processors. These technologies provides a generic and flexible framework to build stream processing applications.

The **microservice** term is used in the rest of the document for processors. The main use case of UVAP is real-time video analysis where all processors run continuously processing potentially never ending data. A microservice can take zero or more kafka topics as input and produce zero or more kafka topics as output. In kafka terminology they are consumers, producers or stream processors. Microservices are packaged and run as docker containers. Microservices typically process data in real-time, however it is possible to run them on historical data.

The data channels between microservices are **Kafka topics**. Head of the topics are kept in persistent storage for configurable time or size. For example the user can configure to keep the last two weeks of video data and keep all object detentions for a year.

![](uvap_architecture.gif)
*Figure 1. Data flow architecture of UVAP. Rectangles are data channels, ellipses are processing units.*
>**Note:** Node labels in this figure are not technical names. Actual topic names can be listed with 
UVAP [helper scripts](../quick_start_guide.md#helperScripts).


[Multi graph runner (MGR)](microservices/mgr/mgr.md) takes the video streams and runs all deep learning based image 
processing models (eg.: head detection, face recognition). [MGR](microservices/mgr/mgr.md) outputs only lightweight 
data such as head detection streams or face recognition feature vectors. **It is very important the uncompressed video 
data never transfered over kafka, all low level image processing is done inside [MGR](microservices/mgr/mgr.md).** 
Kafka is only used to exchange lightweight data.

[Kafka Tracker microservice](microservices/tracker.md) uses *Head Detections* kafka topic produced by 
[MGR](microservices/mgr/mgr.md) and produces *Track Changes* topic. A track is a sequence of head detections of an 
individual on a video stream from the first detection to the disappearance. Besides the path of movement, a track can 
help to calculate how long an individual stayed in an area of interest.

[Kafka Pass Detection microservice](microservices/kafka_pass_detection.md) uses *Track Changes* 
kafka topic produced by [Kafka Tracker microservice](microservices/tracker.md) and produces *Pass Detections* topic. 
If one or more directed polylines (pass lines) are specified in the microservice's configuration, 
the service detects and produces records whenever a track intersects a pass line. Pass Detection helps to
detect whenever an individual enters or leaves an area of interest.
<a name="dataModel"></a>
# Data model
As shown in *Figure 1.* the microservices are connected via kafka topics. This section provides information about the schema and format of these topics.

**The data model of UVAP is normalized.** Every topic contains one piece of information, **if the user needs information from multiple topics the topics have to be joined**.

<a name="topicNamingConvention"></a>
## Topic naming convention

Kafka topics cannot be structured to hierarchical folders so UVAP package a lot of information into the topic name to help the users. Topic names follow a simple naming convention:
```
<domain>.cam.<stream_id>.<data_name>.<schema>.<serialization_format>
```

### Example

```
demo.cam.117.dets.ObjectDetectionRecord.json
```

This topic is produced by MGR, `dets` here refers to the MGR data node. `ObjectDetectionRecord` refers to the schema of the data, it is described in the [data model](../../proto_files/ultinous/proto/common/kafka_data.proto).


`json` describes the serialization format. Currently only json is supported for structured data. It is recommended to turn lz4 compression on in the kafka broker to spare storage and bandwidth as uncompressed json can be prohibitive.

## Topic schemas

As mentioned above the data model is **normalized**. The schema of all the structured topics are described [here](../../proto_files/ultinous/proto/common/kafka_data.proto) with comments embedded for explanation. The schema of the value part of the kafka records are defined in proto messages ending with ```Record```. The comment before the definition describes the key as well.

####Example

```
// Detection record.
// One instance of this record is generated for each detected head/face on each frame.
//
// time: timestamp of the input video frame
// key: time + "_" + sequential index within frame
message ObjectDetectionRecord
{
  ObjectType type = 1;            // Object type
  Rect bounding_box = 2;          // Rectangular box containing the object (eg.: head/face)
  float detection_confidence = 3; // Detection confidence between 0 and 1
  bool end_of_frame = 4;          // When true, all other fields of the record are invalid.
}
```
This is a dump of json detection topic with this schema:

```
$ kafkacat -C -b localhost -t demo.dets.ObjectDetectionRecord.json -o-1 -f "%k,%s\n"
1561981650053,{"type":"PERSON_HEAD","detection_confidence":0,"end_of_frame":true}
1561981650303_0,{"type":"PERSON_HEAD","bounding_box":{"x":1009,"y":388,"width":44,"height":52},"detection_confidence":0.978241444,"end_of_frame":false}
1561981650303_1,{"type":"PERSON_HEAD","bounding_box":{"x":1235,"y":434,"width":68,"height":80},"detection_confidence":0.924045682,"end_of_frame":false}
1561981650303,{"type":"PERSON_HEAD","detection_confidence":0,"end_of_frame":true}
1561981650553_0,{"type":"PERSON_HEAD","bounding_box":{"x":1009,"y":388,"width":44,"height":52},"detection_confidence":0.978059471,"end_of_frame":false}
1561981650553_1,{"type":"PERSON_HEAD","bounding_box":{"x":1236,"y":435,"width":67,"height":79},"detection_confidence":0.928204656,"end_of_frame":false}
1561981650553,{"type":"PERSON_HEAD","detection_confidence":0,"end_of_frame":true}
1561981650803,{"type":"PERSON_HEAD","detection_confidence":0,"end_of_frame":true}
1561981651003,{"type":"PERSON_HEAD","detection_confidence":0,"end_of_frame":true}
```
### Technical progress records

Note that in the detection topic example there are timestamps (eg.:`1561981650803`) with no detections, only a record with `end_of_frame` set to `true`. Different topics have different technical progress record properties eg. records produced by the [Kafka Tracker microservice](microservices/tracker.md) contain `end_of_track` property.   
In general all microservices emit progress (or heartbeat) records to make joining these topics easier in real-time.
 Therefore when processing detections, if the `end_of_frame` is *true*, the microservice can emit all the information for the particular frame.


### Cross references

Records in topics produced by a [microservice](#microservices) often contain references to other topics' records. A chain of references ensures the possibility to link useful data with each other, for example demographic data with tracks.   


#### Example

The **detection_key** property of 
[this TrackChangeRecord](microservices/tracker.md#trackChangeRecord) produced by [Kafka Tracker microservice](microservices/tracker.md) refers to an 
[ObjectDetectionRecord](../../proto_files/ultinous/proto/common/kafka_data.proto) **key** 
and an [AgeRecord](../../proto_files/ultinous/proto/common/kafka_data.proto) **key** 
in two other topics produced by [MGR](microservices/mgr/mgr.md). 

> Note: **key** in [TrackChangeRecord](microservices/tracker.md#trackChangeRecord) 
is usually not equal to its **detection_key**, 
for its **key** refers to the detection of the *first* record of the track. ([Learn more...](microservices/tracker.md#trackChangeRecord))

This simple example is only a sneak peek of UVAP's capabilities. For example with [Kafka Pass Detection microservice](microservices/kafka_pass_detection.md) even more information can
be received about a [TrackChangeRecord](microservices/tracker.md#trackChangeRecord) (which can be associated with [AgeRecord](../../proto_files/ultinous/proto/common/kafka_data.proto)s).

## Join
As the data model is normalized it is common to read and join multiple topics. Joining kafka topics is solved in the java kafka streams API. We also provide a [python implementation](../../demo_applications/utils/kafka/time_ordered_generator_with_timeout.py) as part of the package, see the demo applications for more details.

<a name="microservices"></a>
# Microservices

## [Multi graph runner (MGR)](microservices/mgr/mgr.md)

## [Kafka Tracker](microservices/tracker.md)

## [Kafka Pass Detection](microservices/kafka_pass_detection.md)

Future versions of UVAP will contain many more microservices such as reidentification.

<a name="tutorial"></a>
# Tutorial
Comming soon...

<a name="extendingUVAP"></a>
# Extending UVAP
## Environment for Python Developers
Our demos run in the docker because this solution is quick and easy. For more information please visit [Quick start guide](quick_start_guide.md).  
The developers require a local environment to solve real world problems instead of starting a few pre-written demos.
In this chapter you will find:
- The same installation package like in the **uvap_demo_applications** docker container, and
- How to install a useful editor for python programming language.

### Requirements
- Ubuntu 18.04 Bionic Beaver
- Privileged access to your Ubuntu System as root or via sudo command is required.

### Python3.6
If you would like to create the same environment like **uvap_demo_applications** docker container need to run the following group of commands:
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
Simplest and recommended way to install PyCharm on Ubuntu 18.04 is by use of snaps package manager. The following linux command will install PyCharm community edition on Ubuntu 18.04 Bionic Beaver:

```
$ sudo snap install pycharm-community --classic
pycharm-community 2019.1.3 from jetbrains✓ installed
```
#### Start PyCharm
You can start PyCharm from command line by executing the following linux command:
```
$ pycharm-community
```
