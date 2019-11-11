---
id: conf_passdet
title: Configuring Pass Detector
hide_title: true
---

# Configuring Pass Detector


This microservice is not GPU related. **Pass Detector** processes the record
from a source topic and writes the result to its target topic. **Pass Detector**
can run in _batch mode_, therefore the microservice stops after processing the
last source record.

## Environment Variables

* `KAFKA_PASSDET_MS_PROPERTY_FILE_PATHS`: property file list

## Properties

For an example of Pass Detector properties,
see [Pass Detector Template Properties].

### ultinous.service.kafka.passdet.source.broker.list

| Property         | `ultinous.service.kafka.passdet.source.broker.list`    |
| ---------------- | ------------------------------------------------------ |
| Description      | Broker list of the source.                             |
| Required         | Required                                               |
| Value Type       | `string`                                               |

### ultinous.service.kafka.passdet.source.consumer.group

| Property         | `ultinous.service.kafka.passdet.source.consumer.group` |
| ---------------- | ------------------------------------------------------ |
| Description      | Source consumer group.                                 |
| Required         | Optional                                               |
| Value Type       | `string`                                               |
| Default Value    | `default.consumer`                                     |

### ultinous.service.kafka.passdet.source.topic

| Property         | `ultinous.service.kafka.passdet.source.topic`          |
| ---------------- | ------------------------------------------------------ |
| Description      | Source topic name (see [Topic Naming Convention]).     |
| Required         | Required                                               |
| Value Type       | `string`                                               |

### ultinous.service.kafka.passdet.source.username

| Property         | `ultinous.service.kafka.passdet.source.username`       |
| ---------------- | ------------------------------------------------------ |
| Description      | SASL authentication username of the source.            |
| Required         | Required if source SASL authentication is enabled.     |
| Value Type       | `string`                                               |

### ultinous.service.kafka.passdet.source.password

| Property         | `ultinous.service.kafka.passdet.source.password`       |
| ---------------- | ------------------------------------------------------ |
| Description      | SASL authentication password of the source.            |
| Required         | Required if source username is set.                    |
| Value Type       | `string`                                               |

### ultinous.service.kafka.passdet.source.startTS

| Property         | `ultinous.service.kafka.passdet.source.startTS`        |
| ---------------- | ------------------------------------------------------ |
| Description      | Starting time of source processing.                    |
| Required         | Optional                                               |
| Value Type       | **N/A**                                                |
| Default Value    | `0`                                                    |
| Available values | <ul><li><code>0</code>: start from the first record.</li><li><code>NOW</code>: start from the current timestamp.</li><li>ISO-8601 (millisecond and time zone are optional): start from a specific timestamp.</br>Example: <code>2019-04-08 10:10:24.123 +01:00</code></li></ul> |

### ultinous.service.kafka.passdet.source.endTS

| Property         | `ultinous.service.kafka.passdet.source.endTS`          |
| ---------------- | ------------------------------------------------------ |
| Description      | Ending time of source processing.                      |
| Required         | Optional                                               |
| Value Type       | **N/A**                                                |
| Default Value    | `NEVER`                                                |
| Available values | <ul><li><code>NEVER</code>: the microservice will not stop after the last record has been processed, will wait for new input records.</li><li><code>END</code>: the microservice stops after processing the last source record.</li><li>ISO-8601 (millisecond and time zone are optional): end at a specific timestamp.</br>Example: <code>2019-04-08 10:10:24.123 +01:00</li></ul> |

### ultinous.service.kafka.passdet.target.broker.list

| Property         | `ultinous.service.kafka.passdet.target.broker.list`    |
| ---------------- | ------------------------------------------------------ |
| Description      | Broker list of the target.                             |
| Required         | Required                                               |
| Value Type       | `string`                                               |

### ultinous.service.kafka.passdet.target.topic

| Property         | `ultinous.service.kafka.passdet.target.topic`          |
| ---------------- | ------------------------------------------------------ |
| Description      | Target topic name (see [Topic Naming Convention]).     |
| Required         | Required                                               |
| Value Type       | `string`                                               |

### ultinous.service.kafka.passdet.target.username

| Property         | `ultinous.service.kafka.passdet.target.username`       |
| ---------------- | ------------------------------------------------------ |
| Description      | SASL authentication username of the target.            |
| Required         | Required if target SASL authentication is enables.     |
| Value Type       | `string`                                               |

### ultinous.service.kafka.passdet.target.password

| Property         | `ultinous.service.kafka.passdet.target.password`       |
| ---------------- | ------------------------------------------------------ |
| Description      | SASL authentication password of the target.            |
| Required         | Required if target username is set.                    |
| Value Type       | `string`                                               |

### ultinous.service.kafka.passdet.target.handling

| Property         | `ultinous.service.kafka.passdet.target.handling`       |
| ---------------- | ------------------------------------------------------ |
| Description      | The target's topic handling option.                    |
| Required         | **N/A**                                                |
| Value Type       | **N/A**                                                |
| Default Value    | `CHECK_TS`                                             |
| Available values | <ul><li><code>REPLACE</code>: Delete target topic.</li><li><code>CHECK_TS</code>: Raise error if topic exists with more recent <b>latest timestamp</b>.</li><li><code>SKIP_TS</code>: Skip events up to the latest timestamp in target topic.</li></ul> |

<a name="ultinous.service.kafka.passdet.config"></a>
### ultinous.service.kafka.passdet.config

| Property         | `ultinous.service.kafka.passdet.config`                |
| ---------------- | ------------------------------------------------------ |
| Description      | **Pass Detector** configuration file path.</br>The `PassDetConfigRecord` definition should be in JSON format as defined in the [Kafka configuration proto]. |
| Required         | Required                                               |
| Value Type       | `string`                                               |

Example:

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

>**Stream Configurator**  
UVAP provides an easy-to-use tool for pass line management called
**Stream Configurator**. For further information, see
[Stream Configurator User Interface].

### ultinous.service.kafka.passdet.monitoring.port

| Property         | `ultinous.service.kafka.passdet.monitoring.port`       |
| ---------------- | ------------------------------------------------------ |
| Description      | Monitoring server port.                                |
| Required         | Required                                               |
| Value Type       | `uint16`                                               |

### ultinous.service.kafka.passdet.monitoring.threads

| Property         | `ultinous.service.kafka.passdet.monitoring.threads`    |
| ---------------- | ------------------------------------------------------ |
| Description      | Monitoring server thread pool size.                    |
| Required         | **N/A**                                                |
| Value Type       | `uint16`                                               |
| Default Value    | `1`                                                    |

## Record Schemas

The schema definition of `TrackChangeRecord` and `PassDetectionRecord` can be
found in the [Kafka data proto].

Example of a `PassDetectionRecord` from Kafka:

```
PASS_CANDIDATE:
{
  "timestamp": 1564493689341,
  "key": "pass_01",
  "value": {
    "type": "PASS_CANDIDATE",
    "pass_candidate": {
      "pass": {
        "id": {
          "track_key": "1564493689041_50187",
          "serial": 0
        },
        "pass_line_id": "pass_01",
        "cross_dir": "RL",
        "section_idx": 0,
        "cross_point": {
          "x": 511,
          "y": 500
        }
      },
      "is_extrapolated": false
    }
  },
  "headers": "[('format', b'json'), ('type', b'PassDetectionRecord')]"
}
PASS_REALIZED:
{
  "timestamp": 1564493689341,
  "key": null,
  "value": {
    "type": "PASS_REALIZED",
    "pass_realized": {
      "pass_event_ref": {
        "track_key": "1564493689041_50187",
        "serial": 0
      }
    }
  },
  "headers": "[('format', b'json'), ('type', b'PassDetectionRecord')]"
},
HEARTBEAT:
{
  "timestamp": 1564493689341,
  "key": null,
  "value": {
    "type": "HEARTBEAT"
  },
  "headers": "[('format', b'json'), ('type', b'PassDetectionRecord')]"
}
END_OF_TRACK:
{
  "timestamp": 1564493689341,
  "key": null,
  "value": {
    "type": "END_OF_TRACK",
    "end_of_track": {
      "track_key": "1564493689041_50187"
    }
  },
  "headers": "[('format', b'json'), ('type', b'PassDetectionRecord')]"
}
```
 >**Note**:  
 >The `key` is empty in the following cases:
 >* The record is only a heartbeat message.
 >* The record is an end-of-track signal.
 >* The record is a **Pass Realization** (see below).

<a name="pass_detection_example"></a>
![Dataflow Architecture of UVAP](../assets/pass_detection_example.png)  
***Pass Detection Example***

<a name="pass_realization"></a>
> **Pass Realization**  
Sometimes a `TrackChangeRecord`, which
triggers a Pass Detection is not derived from a "real" detection, but the track
change is only a prediction of the next track position. In this case, the
`is_extrapolated` field of the `PassDetectionRecord` is true. After the
prediction the track usually continues with a "real" detection. 
In this case a new `PassDetectionRecord` is inserted to the target topic with an
empty key but with the appropriate non empty `track_key`.

See the [Kafka data proto].

## Feature Demo

For the pass detection feature demo, see [Pass Detection Demo].



[Kafka configuration proto]: ../../proto_files/ultinous/proto/common/kafka_config.proto
[Kafka data proto]: ../../proto_files/ultinous/proto/common/kafka_data.proto
[PassDetectionRecord]: #record-schemas
[Pass Confirmation]: #pass_confirmation
[Pass Detection Demo]: ../demo/demo_pass_det.md
[Pass Detector Template Properties]: ../../templates/uvap_kafka_passdet_base_TEMPLATE.properties
[prediction of the next track position]: conf_track.md#empty_detection_key
[Stream Configurator User Interface]: sc_descr.md#stream-configurator-user-interface
[Topic Naming Convention]: uvap_data_model.md#topic-naming-convention
[Tracker]: conf_track.md
[ultinous.service.kafka.passdet.config]: #ultinous.service.kafka.passdet.config
