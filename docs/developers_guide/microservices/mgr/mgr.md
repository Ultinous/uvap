# Multi Graph Runner (MGR)

## Introduction

UVAP high level data flow model (dockerized microservices communicating over kafka topics) is very flexible model but it has limitations. Two microservices cannot exchange uncompressed high resolution video frames simply because of physical limitations of the IO and network systems. MGR implements another data flow model to overcome these limitations.

this problem with the following main properties:
 - MGR is one OS process using one GPU, so all the process node are in the same process.
 - MGR's process nodes are executed synchronized in deppendency order, no queues are necessary, process nodes can exchange data by reference.



Multi Graph Runner is a microservice that takes one or more video streams as input and run deep learning models and other image processing algorithms on them. The processing steps are configurable and specified as a data flow graph.

## Data flow graph

MGR implements a data flow programming model. The MGR's data flow is a directed [bipartite graph](https://en.wikipedia.org/wiki/Bipartite_graph) consisting of data and process nodes. This model is very similar to the UVAP dataflow, one could ask why two data flow models are needed? UVAP uses kafka topics for data exchange but it has certain limitations. If we want to exchange large uncompressed video frames between processing nodes it needs a very high throughput channel.

MGR process nodes are in the same os process


There are significant differences:
- Execution model:
- Data channels: UVAP uses kafka topics for data exchange while MGR data is in process (more precisely in GPU memory) so data


![](graph_examples/simple_graph.gif)

[detection example](graph_examples/det.prototxt)

### Execution model

In the following sections we describe the available data and process nodes.
Formal definition of these these are available in [this proto file](../../../../../proto_files/ultinous/proto/dataflow/dataflow.proto). Some of these will be deprecated, they are not included in this document.

### Data nodes

- FRAME: frame in a video stream.
- DETECTIONS: object detections (eg.: head detections)
- FEATURE_VECTORS
- HEAD_POSE_3DS
- GENDERS
- AGES

### Process nodes

- DISPLAY
- ROI
- OBJ_DETECTOR
- OBJ_FILTER
- DRAW_RECTS
- RESIZE
- ROTATE
- HEAD_POSE_CALC
- HEAD_POSE_FILTER
- FACE_FEATURE_CALC
- FACE_DEMOGRAPHY_CALC
- FULL_BODY_CROP_BOC_CALC
- FULL_BODY_FEATURE_CALC

## Configuration

The processing steps are configurable and specified as a data flow graph. The data flow is written in prototxt format. Prototxt is a textual representation of [protobuf messages](https://developers.google.com/protocol-buffers).

## Deployment

To run MGR the server must have an nvidia GPU (1060 or better). MGR is dockerized and must be run with nvidia-docker. If the server has more GPUs a separate MGR instance should run on each GPU for optimal performance.

## Runtime performance
