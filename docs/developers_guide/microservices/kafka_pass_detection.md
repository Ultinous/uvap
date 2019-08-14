# Kafka Pass Detection microservice

## Table of contents
1. [Introduction](#introduction)
1. [Configuration](#configuration)
1. [Record schemas](#passDetectionRecord)
1. [Quick Start Guide](#quickStartGuide)

## Introduction
Kafka Pass Detection microservice uses Track Changes kafka topic produced by [Kafka Tracker microservice](tracker.md) 
and produces Pass Detections topic. One or more directed polylines (pass lines) should be specified in the microservice's
configuration and this service detects and produces records whenever a track intersects a pass line. Pass Detection helps 
to detect whenever an individual enters or leaves an area of interest.

## Configuration
This microservice is **not GPU related**. Kafka Pass Detection microservice processes the record from a source topic and writes the result to its target 
topic. TODO The Tracker can run in *batch mode* therefore the microservice stops after processing the last source record.

### Environment variables
`KAFKA_PASSDET_MS_PROPERTY_FILE_PATHS`: property file list

### Properties
- `ultinous.service.kafka.passdet.source.broker.list`: The broker list of the source.
  - Required 
  - Value type: `string`
- `ultinous.service.kafka.passdet.source.consumer.group`: The source consumer group.
  - Optional. Default: `default.consumer`
  - Value type: `string`
- `ultinous.service.kafka.passdet.source.topic`: The [source topic name](../../developers_guide/developers_guide.md#topicNamingConvention).
  - Required 
  - Value type: `string`
- `ultinous.service.kafka.passdet.source.username`: The SASL authentication username of the source.
  - Required if source's SASL authentication is enabled. 
  - Value type: `string`
- `ultinous.service.kafka.passdet.source.password`: The SASL authentication password of the source.
  - Required if source's username is set.
  - Value type: `string`
- `ultinous.service.kafka.passdet.source.startTS`: The starting time of processing the source.
  - Default: `0`
  - Available values:
    - `0`: start from the first record 
    - `NOW`: start from the current timestamp
    - ISO-8601 (opt. millisec and tz): start from a specific timestamp
      - Example: `2019-04-08 10:10:24.123 +01:00`
- `ultinous.service.kafka.passdet.source.endTS`: The ending time of processing the source.
  - Default: `NEVER`
  - Available values:
    - `NEVER`: the microservice will not stop after the last record has been processed, will wait for new input records.
    - `END`: the microservice stops after processing the last source record
    - ISO-8601 (opt. millisec and tz): end at a specific timestamp
      - Example: `2019-04-08 10:10:24.123 +01:00`
- `ultinous.service.kafka.passdet.target.broker.list`: Target's broker list.
  - Required
  - Value type: `string`
- `ultinous.service.kafka.passdet.target.topic`: [Target topic name](../../developers_guide/developers_guide.md#topicNamingConvention).
  - Required
  - Value type: `string`
- `ultinous.service.kafka.passdet.target.username`: The SASL authentication username of the target
  - Required if target's SASL authentication is enables.
  - Value type: `string`
- `ultinous.service.kafka.passdet.target.password`: The SASL authentication password of the target.
  - Required if target's username is set.
  - Value type: `string`
- `ultinous.service.kafka.passdet.target.handling`: The target's topic handling option.
  - Default: `CHECK_TS`
  - Available values:
    - `REPLACE`: Delete target topic.
    - `CHECK_TS`: Raise error if topic exists with more recent *latest timestamp*.
    - `SKIP_TS`: Skip events up to the latest timestamp in target topic.
- `ultinous.service.kafka.passdet.config`: Pass Detection configuration file path. The `PassDetConfigRecord` definition 
should be in JSON format as defined in [this proto3 message](../../../proto_files/ultinous/proto/common/kafka_config.proto).
  - Required 
  - Value type: `string`
  - Example:
   ```json
    {
      "passLines": [
        {
          "id": "pass_1",
          "poly": [
            {"x": 100, "y": 500},
            {"x": 1870, "y": 500}
          ]
        },
        {
          "id": "pass_2",
          "poly": [
            {"x": 960, "y": 980},
            {"x": 1000, "y": 560},
            {"x": 960, "y": 100}
          ]
        }
      ]
    }
   ```
- `ultinous.service.kafka.passdet.monitoring.port`: Monitoring server port
  - Required 
  - Value type: `uint16`
- `ultinous.service.kafka.passdet.monitoring.threads`: Monitoring server thread pool size
  - Default: `1`
  - Value type: `uint16`

Template properties file can be found [here](../../../templates/uvap_kafka_passdet_TEMPLATE.properties).

<a name="passDetectionRecord"></a>
## Record schemas
The schema definition of `TrackChangeRecord` and `PassDetectionRecord` can be found [here](../../../proto_files/ultinous/proto/common/kafka_data.proto).

Example of a `PassDetectionRecord` from Kafka:
```
{
  "timestamp": 1564493689341,
  "key": "pass_01",
  "value": {
    "pass_id":"pass_01",
    "cross_dir":"RL",
    "section_idx":0,
    "cross_point":{
      "x":511,
      "y":500
     },
     "track_key":"1564493689041_50187",
     "is_extrapolated":false,
     "end_of_track_passes":false
   }
}
```
**Note**:
The key is empty:
- when the record is only a heartbeat message
- or when the record is an end-of-track signal
- or if the record is a [Pass Confirmation](#passConfirmation). 

<a name="passConfirmation"></a>
> **Pass Confirmation**: the indication of a "real" pass event.
Sometimes a *[TrackChangeRecord](tracker.md#trackChangeRecord)* which triggers a Pass Detection is not derived from a 
"real" detection, but the track change is only a [prediction of the next track position]((tracker.md#emptyDetectionKey)). 
In this case the **key** of the *[PassDetectionRecord](#passDetectionRecord)* is the crossed pass line's id 
(defined in [`ultinous.service.kafka.passdet.config`](#configuration)). After the prediction the track usually continues 
with a "real" detection. This occurrence is a *Pass Confirmation*. In this case a new *[PassDetectionRecord](#passDetectionRecord)*
 is inserted to the *target* topic with an **empty *key*** but with the appropriate **non empty *pass_id***.  

<a name="quickStartGuide"></a>
## [Quick Start Guide](../../quick_start_guide.md)
