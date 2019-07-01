# Kafka Tracker

## Introduction
TODO: create a description here!


## Configuration
This microservice is not GPU related.
input: ObjectDetectionRecord
output: TrackChangeRecord

### Environment variables
```
KAFKA_TRACKER_MS_PROPERTY_FILE_PATHS=tracker.properties
KAFKA_TRACKER_MS_PROPERTY_PREFIX=com.ultinous.ms.tracker
```
### Properties
```
com.ultinous.ms.tracker.source.broker.list required [string] - Source's broker list
com.ultinous.ms.tracker.source.consumer.group (default.consumer) [string] - Source consumer group.
com.ultinous.ms.tracker.source.topic required [string] - Source topic name.
com.ultinous.ms.tracker.source.username [string] - Source's SASL authentication username. Enables SASL authentication.
com.ultinous.ms.tracker.source.password [string] - Source's SASL authentication password. Required if username is set.
com.ultinous.ms.tracker.source.startTS [string] - Source's starting. "0" (begin), "NOW" or ISO-8601 (opt. millisec and tz), default is 0. Example: 2019-04-08 10:10:24.123 +01:00
com.ultinous.ms.tracker.source.endTS [string] - Source's ending. "NEVER" or ISO-8601 (opt. millisec), default is "NEVER". Example: 2019-04-09 22:22:24.1234 +01:00
com.ultinous.ms.tracker.target.broker.list required [string] - Target's broker list.
com.ultinous.ms.tracker.target.topic required [string] - Target topic name.
com.ultinous.ms.tracker.target.username [string] - Target's SASL authentication username. Enables SASL authentication.
com.ultinous.ms.tracker.target.password [string] - Target's SASL authentication password. Required if username is set.
com.ultinous.ms.tracker.target.handling [string] - Target's topic handling option. Valid values are: REPLACE | CHECK_TS | SKIP_TS. Default is CHECK_TS.
com.ultinous.ms.tracker.config [string] - Tracking configuration in JSON format defined by proto3 message TrackingConfig.
com.ultinous.ms.tracker.monitoring.port required [uint16] - Monitoring server port, example: 50052
com.ultinous.ms.tracker.monitoring.threads (1) [uint16] - Monitoring server thread pool size{code}
```
### Tracking configuration
```
message TrackingConfig
{
  // confidence threshold to filter tracks
  // value can be between 0.0f and 1.0f
  // default: 0.0f, means no filtering
  float detection_threshold = 1;
}
```
Example:
```
com.ultinous.ms.tracker.config={ "detection_threshold": 0.7 }
```
### Track Change Record
(from [this proto file](../../../../../proto_files/ultinous/proto/common/kafka_common.proto))

```
message TrackChangeRecord{
  message TimedPoint{int64 time = 1; // Java timestamp
    int32 x = 2;
    int32 y = 3;
    int32 z = 4;
  }
  int64 start_time = 1; // Java timestampbool
  end_of_track = 2; // No more data for this track. Ignore all other data in this record.
  string detection_key = 3; // Empty means there is no detection_key
  TimedPoint point = 5; // Members of message type are always optional.
}
```
Exemple from Kafka
```
{
  "timestamp": 1558509708748,
  "key": "1558509707748_0",
  "value": {
    "end_of_track": false,
    "detectionKey": "1558509708748_0",
    "time": "1558509708748",
    "point": {
      "x": 1487,
      "y": 503
    }
  },
  "headers": "[
    ('type', b'TrackChange'),
    ('format', b'json')
  ]"
},
```
