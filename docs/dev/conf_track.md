---
id: conf_track
title: Configuring Tracker
hide_title: true
---

# Configuring Tracker

This microservice is not GPU related. **Tracker** processes the record from
a source topic and writes the result to its target topic. **Tracker** can run in
_batch mode_, therefore; the microservice stops after processing the last source
record.

## Environment Variables

* `KAFKA_TRACKER_MS_PROPERTY_FILE_PATHS`: property file list

## Properties

For an example of **Tracker** properties,
see [Tracker Template Properties].

### ultinous.service.kafka.tracker.source.broker.list

| Property         | `ultinous.service.kafka.tracker.source.broker.list`    |
| ---------------- | ------------------------------------------------------ |
| Description      | Broker list of the source.                             |
| Required         | Required                                               |
| Value Type       | `string`                                               |

### ultinous.service.kafka.tracker.source.consumer.group

| Property         | `ultinous.service.kafka.tracker.source.consumer.group` |
| ---------------- | ------------------------------------------------------ |
| Description      | Source consumer group.                                 |
| Required         | Optional                                               |
| Value Type       | `string`                                               |
| Default Value    | `default.consumer`                                     |

### ultinous.service.kafka.tracker.source.topic

| Property         | `ultinous.service.kafka.tracker.source.topic`          |
| ---------------- | ------------------------------------------------------ |
| Description      | Source topic name (see [Topic Naming Convention]).     |
| Required         | Required                                               |
| Value Type       | `string`                                               |

### ultinous.service.kafka.tracker.source.username

| Property         | `ultinous.service.kafka.tracker.source.username`       |
| ---------------- | ------------------------------------------------------ |
| Description      | SASL authentication username of the source.            |
| Required         | Required if source SASL authentication is enabled.     |
| Value Type       | `string`                                               |

### ultinous.service.kafka.tracker.source.password

| Property         | `ultinous.service.kafka.tracker.source.password`       |
| ---------------- | ------------------------------------------------------ |
| Description      | SASL authentication password of the source.            |
| Required         | Required if source username is set.                    |
| Value Type       | `string`                                               |

### ultinous.service.kafka.tracker.source.startTS

| Property         | `ultinous.service.kafka.tracker.source.startTS`        |
| ---------------- | ------------------------------------------------------ |
| Description      | Starting time of source processing.                    |
| Required         | Optional                                               |
| Value Type       | **N/A**                                                |
| Default Value    | `0`                                                    |
| Available values | <ul><li><code>0</code>: start from the first record.</li><li><code>NOW</code>: start from the current timestamp.</li><li>ISO-8601 (millisecond and time zone are optional): start from a specific timestamp.</br>Example: <code>2019-04-08 10:10:24.123 +01:00</code></li></ul> |

### ultinous.service.kafka.tracker.source.endTS

| Property         | `ultinous.service.kafka.tracker.source.endTS`          |
| ---------------- | ------------------------------------------------------ |
| Description      | Ending time of source processing.                      |
| Required         | Optional                                               |
| Value Type       | **N/A**                                                |
| Default Value    | `NEVER`                                                |
| Available values | <ul><li><code>NEVER</code>: the microservice will not stop after the last record has been processed, will wait for new input records.</li><li><code>END</code>: the microservice stops after processing the last source record.</li><li>ISO-8601 (millisecond and time zone are optional): end at a specific timestamp.</br>Example: <code>2019-04-08 10:10:24.123 +01:00</li></ul> |

### ultinous.service.kafka.tracker.target.broker.list

| Property         | `ultinous.service.kafka.tracker.target.broker.list`    |
| ---------------- | ------------------------------------------------------ |
| Description      | Broker list of the target.                             |
| Required         | Required                                               |
| Value Type       | `string`                                               |

### ultinous.service.kafka.tracker.target.topic

| Property         | `ultinous.service.kafka.tracker.target.topic`          |
| ---------------- | ------------------------------------------------------ |
| Description      | Target topic name (see [Topic Naming Convention]).     |
| Required         | Required                                               |
| Value Type       | `string`                                               |

#### ultinous.service.kafka.tracker.target.username

| Property         | `ultinous.service.kafka.tracker.target.username`       |
| ---------------- | ------------------------------------------------------ |
| Description      | SASL authentication username of the target.            |
| Required         | Required if target SASL authentication is enables.     |
| Value Type       | `string`                                               |

### ultinous.service.kafka.tracker.target.password

| Property         | `ultinous.service.kafka.tracker.target.password`       |
| ---------------- | ------------------------------------------------------ |
| Description      | SASL authentication password of the target.            |
| Required         | Required if target username is set.                    |
| Value Type       | `string`                                               |

### ultinous.service.kafka.tracker.target.handling

| Property         | `ultinous.service.kafka.tracker.target.handling`       |
| ---------------- | ------------------------------------------------------ |
| Description      | The target's topic handling option.                    |
| Required         | **N/A**                                                |
| Value Type       | **N/A**                                                |
| Default Value    | `CHECK_TS`                                             |
| Available values | <ul><li><code>REPLACE</code>: Delete target topic.</li><li><code>CHECK_TS</code>: Raise error if topic exists with more recent <b>latest timestamp</b>.</li><li><code>SKIP_TS</code>: Skip events up to the latest timestamp in target topic.</li></ul> |

### ultinous.service.kafka.tracker.config

| Property         | `ultinous.service.kafka.tracker.config`                |
| ---------------- | ------------------------------------------------------ |
| Description      | Tracking configuration file path.</br>The `TrackingConfigRecord` definition should be in JSON format as defined in the [Kafka configuration proto]. |
| Required         | Required                                               |
| Value Type       | `string`                                               |

### ultinous.service.kafka.tracker.monitoring.port

| Property         | `ultinous.service.kafka.tracker.monitoring.port`       |
| ---------------- | ------------------------------------------------------ |
| Description      | Monitoring server port.                                |
| Required         | Required                                               |
| Value Type       | `uint16`                                               |

### ultinous.service.kafka.tracker.monitoring.threads

| Property         | `ultinous.service.kafka.tracker.monitoring.threads`    |
| ---------------- | ------------------------------------------------------ |
| Description      | Monitoring server thread pool size.                    |
| Required         | **N/A**                                                |
| Value Type       | `uint16`                                               |
| Default Value    | `1`                                                    |

## Record Schemas

The schema definition of `ObjectDetectionRecord` and `TrackChangeRecord` can be
found in the [Kafka data proto].

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
  },
  "headers": "[
    ('type', b'TrackChange'),
    ('format', b'json')
  ]"
},
```

 <a name="empty_detection_key"></a>
 > **Empty Detection Key**  
 > The `detection_key` is empty if there is no "real" detection, and the
 > change is a prediction of the next track position (or an end of a track).  
 > This means that there is no reference to any video frames or to any detections
 > in another Kafka topic, but these records are necessary for processing the whole
 > "lifecycle" of a track.

## Feature Demo

For the tracker feature demo, see [Tracker Demo].

[Tracker Demo]: ../demo/demo_track.md
[Kafka configuration proto]: ../../proto_files/ultinous/proto/common/kafka_config.proto
[Kafka data proto]: ../../proto_files/ultinous/proto/common/kafka_data.proto
[Topic Naming Convention]: uvap_data_model.md#topic-naming-convention
[Tracker Template Properties]: ../../templates/uvap_kafka_tracker_base_TEMPLATE.properties
