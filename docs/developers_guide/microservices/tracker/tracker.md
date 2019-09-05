# Kafka Tracker microservice

## Table of contents
1. [Introduction](#introduction)
1. [Configuration](#configuration)
1. [Record schemas](#trackChangeRecord)
1. [Quick Start Guide](#quickStartGuide)

## Introduction
Kafka Tracker microservice builds routes based on the result of head detection. If a head detection is close enough 
to a former head detection then they form a track. Each following head detections close enough extend this track with new entries. 
Geometric and temporal distance thresholds can be configured.

## Configuration
This microservice is **not GPU related**. The Tracker processes the record from a source topic and writes the result to its target 
topic. The Tracker can run in *batch mode* therefore the microservice stops after processing the last source record.

### Environment variables
`KAFKA_TRACKER_MS_PROPERTY_FILE_PATHS`: property file list

### Properties
- `ultinous.service.kafka.tracker.source.broker.list`: The broker list of the source.
  - Required 
  - Value type: `string`
- `ultinous.service.kafka.tracker.source.consumer.group`: The source consumer group.
  - Optional. Default: `default.consumer`
  - Value type: `string`
- `ultinous.service.kafka.tracker.source.topic`: The [source topic name](../../developers_guide.md#topicNamingConvention).
  - Required 
  - Value type: `string`
- `ultinous.service.kafka.tracker.source.username`: The SASL authentication username of the source.
  - Required if source's SASL authentication is enabled. 
  - Value type: `string`
- `ultinous.service.kafka.tracker.source.password`: The SASL authentication password of the source.
  - Required if source's username is set.
  - Value type: `string`
- `ultinous.service.kafka.tracker.source.startTS`: The starting time of processing the source.
  - Default: `0`
  - Available values:
    - `0`: start from the first record 
    - `NOW`: start from the current timestamp
    - ISO-8601 (opt. millisec and tz): start from a specific timestamp
      - Example: `2019-04-08 10:10:24.123 +01:00`
- `ultinous.service.kafka.tracker.source.endTS`: The ending time of processing the source.
  - Default: `NEVER`
  - Available values:
    - `NEVER`: the microservice will not stop after the last record has been processed, will wait for new input records.
    - `END`: the microservice stops after processing the last source record
    - ISO-8601 (opt. millisec and tz): end at a specific timestamp
      - Example: `2019-04-08 10:10:24.123 +01:00`
- `ultinous.service.kafka.tracker.target.broker.list`: Target's broker list.
  - Required
  - Value type: `string`
- `ultinous.service.kafka.tracker.target.topic`: [Target topic name](../../developers_guide.md#topicNamingConvention).
  - Required
  - Value type: `string`
- `ultinous.service.kafka.tracker.target.username`: The SASL authentication username of the target
  - Required if target's SASL authentication is enables.
  - Value type: `string`
- `ultinous.service.kafka.tracker.target.password`: The SASL authentication password of the target.
  - Required if target's username is set.
  - Value type: `string`
- `ultinous.service.kafka.tracker.target.handling`: The target's topic handling option.
  - Default: `CHECK_TS`
  - Available values:
    - `REPLACE`: Delete target topic.
    - `CHECK_TS`: Raise error if topic exists with more recent *latest timestamp*.
    - `SKIP_TS`: Skip events up to the latest timestamp in target topic.
- `ultinous.service.kafka.tracker.config`: Tracking configuration file path. The `TrackingConfigRecord` definition should be in JSON format as defined in [this proto3 message](../../../../proto_files/ultinous/proto/common/kafka_config.proto).
  - Required 
  - Value type: `string`
- `ultinous.service.kafka.tracker.monitoring.port`: Monitoring server port
  - Required 
  - Value type: `uint16`
- `ultinous.service.kafka.tracker.monitoring.threads`: Monitoring server thread pool size
  - Default: `1`
  - Value type: `uint16`

Template properties file can be found [here](../../../../templates/uvap_kafka_tracker_base_TEMPLATE.properties).

<a name="trackChangeRecord"></a>
## Record schemas
The schema definition of `ObjectDetectionRecord` and `TrackChangeRecord` can be found [here](../../../../proto_files/ultinous/proto/common/kafka_data.proto).

Example of a `TrackChangeRecord` from Kafka:
```
{
  "timestamp": 1558509708748,
  "key": "1558509707748_0",
  "value": {
    "end_of_track": false,
    "detection_key": "1558509708748_0",
    "point": {
      "x": 1487,
      "y": 503
    }
  }
}
```
<a name="emptyDetectionKey"></a>
**Note**:
Sometimes the detection_key field is empty. In this case there is no "real" detection and the change is a prediction of the next track position (or an end of a track). 
This means that there is *no reference* to any video frames or to any detections in another Kafka topic, but these records are necessary for processing the whole "lifecycle" of a track.

<a name="quickStartGuide"></a>
## [Quick Start Guide](../../quick_start_guide.md)
