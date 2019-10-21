---
id: conf_reid
title: Configuring Basic Reidentifier
hide_title: true
---

# Configuring Basic Reidentifier

This microservice is not GPU related. It can be run in batch mode, therefore the
microservice stops after processing the last source record.

## Environment Variables

* `KAFKA_REID_MS_PROPERTY_FILE_PATHS`: property files path list.

## Properties

>**Note:**  
Setting `.data` and `.file` properties are exclusive to each other, meaning
setting both `ultinous.service.kafka.reid.config.data` and
`ultinous.service.kafka.reid.config.file` results an error.

### ultinous.service.kafka.reid.auth.defs.data

| Property      | `ultinous.service.kafka.reid.auth.defs.data`    |
| ------------- | ------------------------------------------------------ |
| Description   | Authentication definition data in one-liner JSON format corresponding to the definitions described in [Superconfig Authentication Definitions].  |
| Required      | Optional                                               |

### ultinous.service.kafka.reid.auth.defs.file
  
| Property      | `ultinous.service.kafka.reid.auth.defs.file`    |
| ------------- | ------------------------------------------------------ |
| Description   | Authentication definition file path. Content of the file should be in JSON format described described in [Superconfig Authentication Definitions]. |
| Required      | Optional                                               |


### ultinous.service.kafka.reid.ms.config.data

| Property      | `ultinous.service.kafka.reid.ms.config.data`    |
| ------------- | ------------------------------------------------------ |
| Description   | **Basic Reidentifier** microservice configuration of source and target topics in one-liner JSON format corresponding to the definitions described in [Superconfig Topic Definitions]. |
| Required      | Required                                               |
| Notes         | Required if no other reidentification configuration is set.<br> One configuration fits all. |

### ultinous.service.kafka.reid.ms.config.file
	
| Property      | `ultinous.service.kafka.reid.ms.config.file`    |
| ------------- | ------------------------------------------------------ |
| Description   | **Basic Reidentifier** microservice configuration file path. Content must be in one-liner JSON format described in [Superconfig Topic Definitions].  |
| Required      | Required                                               |
| Notes         | Required if no other reidentification configuration is set.<br> One configuration fits all. |

### ultinous.service.kafka.reid.config.data

| Property      | `ultinous.service.kafka.reid.config.data`    |
| ------------- | ------------------------------------------------------ |
| Description   | **Basic Reidentifier** configurations of input streams defined in JSON format. |
| Required      | Optional                                               |
| Notes         | Should only be set if the `ReidMSConfig` contains no `config_data` global reidentification configuration. |

### ultinous.service.kafka.reid.config.file
  
| Property      | `ultinous.service.kafka.reid.config.file`   |
| ------------- | ------------------------------------------------------ |
| Description   | **Basic Reidentifier** configuration file path. File content must be in one-liner JSON format same as described at `ultinous.service.kafka.reid.config.data` above. |
| Required      | Optional                                               |
| Notes         | Should only be set if the `ReidMSConfig` contains no `config_data` global reidentification configuration. |

### ultinous.service.kafka.reid.monitoring.port

| Property      | `ultinous.service.kafka.reid.monitoring.port`    |
| ------------- | ------------------------------------------------------ |
| Description   | Monitoring server port.                             |
| Required      | Required                                               |
| Value Type    | `uint16`                                               |

### ultinous.service.kafka.reid.monitoring.threads

| Property      | `ultinous.service.kafka.reid.monitoring.threads`    |
| ------------- | ------------------------------------------------------ |
| Description   | Monitoring server thread pool size.                     |
| Required      | Required                                               |
| Value Type    | `uint16`                                               |  


<a name="reidRecord"></a>
## Record Schemas

Configuration records are separated into the following three values:

* `ReidMSConfig` specified in [Kafka superconfiguration proto]
* `ReidConfigRecord` specified in [Kafka configuration proto]
* `ReidRecord` specified in [Kafka data proto]

### Example of a ReidMSConfig from Kafka
```
{
  "source_options":
  {
    "start":"START_DATETIME",
    "start_date_time": "2019-05-31T10:30:00.000 +02:00"
    "end":"END_NEVER"
  },
  "sources":
  [
    {
      "broker_list":"demoserver:9092",
      "name":"cam.entrance.FeatureVectorRecord.json"
    },
    {
      "broker_list":"demoserver:9092",
      "name":"cam.exit.FeatureVectorRecord.json"
    }
  ],
  "target_options":
  {
    "handling":"REPLACE"
  },
  "target":
  {
    "broker_list":"localhost:9092",
    "name":"sample.ReidRecord.json"
  }
}
```

In this example, the sources are set to be read from the given date and never
stop reading them. Two feature vector sources are defined with broker list and
name. The target stream is being replaced.

### Example of a ReidConfigRecord from Kafka
```
{
  "inputs":
  [
    {
      "stream_id": "entranceCamera",
      "fv_field": "features",
      "to_be_ignored_field": "end_of_frame",
      "do_reg": true,
      "reid_min_score": 0.9,
      "reid_max_count": 1,
      "reg_method": "SIMPLE_AVERAGE",
      "reg_max_score": 0.7,
      "reg_retention_period": 86400000
    },
    {
      "stream_id": "exitCamera",
      "fv_field": "features",
      "to_be_ignored_field": "end_of_frame",
      "do_reid":true
    }
  ]
}
```

The `inputs` field has to contain exactly as many records as many input streams
are defined in `ReidMSConfig` (the i<sup>th</sup> input stream is assigned
to the i<sup>th</sup> input config record).
See the table below for the field descriptions:

| Input | Description |
|--|--|
| `stream_id`           | An arbitrary but application-unique name for the input stream. This is later referenced in the results. |
| `fv_field`            | The _name_ of a `FeatureVectorRecord` type field in the input topic schema. This field refers to the actual feature vector data.|
| `is_active_field`     | Optional. The _name_ of a boolean type field in the input topic schema. If set and the field is present in the actual message, the message is not processed if the field has the value `false`. <br>Useful for "turning off" a feature vector in a manually maintained list.  |
| `to_be_ignored_field` | Optional. The _name_ of a boolean type field in the input topic schema. If set and the field is present in the actual message, the message is not processed if the field has the value `true`.<br>This is necessary because not every `FeatureVectorRecord` message (see [Kafka data proto]) contains the `features` field. For technical reasons, sometimes it only contains the `end_of_frame` field which, in this case, is then set to `true`.|
| `do_reid`             | If set to `true`, the stream is used for reidentification. Default is `false`.|
| `do_reg`              | If set to `true`, the stream is used for registration. Default is `false`.|
| `reid_min_score`      | Must be set if and only if `do_reg` is set to `true`. A score that reaches or exceeds this value is necessary to result a reidentification event, however, match count can still be limited. <br> Must be in the `[0.0..1.0]` interval, default is `0.0`.|
| `reid_max_count`      | Must be set if and only if `do_reg` is set to `true`. Defines the maximum number of the returned matching feature vectors (those which result a score good enough) per registration stream. The actual reidentification result can be as long as the sum of these values defined in the registration streams.<br>Must be positive or `0`, default is `0`.|
| `reg_method`          | Must not be set to `NONE` if and only if `do_reg` is set to `true`.<br>Defines what happens to the already registered feature vector of an individual if a new feature vector is recognized (can be either updated to the new one or contribute to a weighted average).|
| `reg_max_score`       | Must be set if and only if `do_reg` is set to `true`. A new feature vector is registered if there is no feature vector stored with a score reaching or exceeding this value, otherwise the feature vector with the highest the score is updated.<br>Must be in the `[0.0..1.0]` interval, default is `0.0`. The value `1.0` is an exception because in this case, every feature vector is stored.|
| `reg_retention_period`| Time interval in milliseconds. Must be set if and only if `do_reg` is set to `true`. Feature vectors stored for longer time than this period are deleted from the registration database. `0` means nothing is deleted.<br>Default is `0`.|

In this exameple, the `"entranceCamera"` stream has a minimum
reidentification score of `0.9`, which means the result produced from this
stream contains hits that have at least this score value. Other streams may
define other minimums. The `reid_max_count` is set to `1`, meaning one
reidentification result is produced from this stream at the most. This means that
the stream corresponds to the final reidentification result with its most
similar feature vector (if the similarity score reaches `0.9`).

Also, the `"entranceCamera"` stream `reg_max_score` is set to `0.7`, meaning
only those new feature vectors are stored, which come from this stream and there
does not exist a stored feature vector with the similarity score reaching `0.7`.

>**Note:**  
`[0..reg_max_score]` does not contain its upper boundary but `[reid_min_score..1]`
does contain its lower boundary. These two values can be the same
(in which case a feature vector is certainly stored or reidentified). If
`reid_min_score` is greater than `reg_max_score`, there is an interval
of scores that are too similar to be remembered but not too similar to be recognized.

The `reg_retention_period` of the example stream is 24 hours in milliseconds.
That means that a newly stored feature vector is forgotten after a day.

### Examples of a ReidRecord from Kafka

An example of a `ReidRecord` from Kafka:

```
{
  "type":"REG",
  "event":
  {
    "stream_id":"entranceCamera",
    "key":"1564038630680_1"
  },
  "reg_refs":
  [
    {
      "subject":
      {
        "stream_id":"entranceCamera",
        "key":"1564038630680_1"
      },
      "score":0
    }
  ]
}
{
  "type":"REID",
  "event":
  {
    "stream_id":"exitCamera",
    "key":"1564038631000_1"
  },
  "reg_refs":
  [
    {
      "subject":
      {
        "stream_id":"entranceCamera",
        "key":"1564038630680_1"
      },
      "score":0.970905602
    }
  ]
}
```

In this example, there are two records.

The first record `type` is set to `REG`, which means that the event-trigger
feature vector is not found in the database but became stored. The event
describes that the feature vector comes from the source which has the ID
`entranceCamera`. The unique key of the particular feature vector is
`1564038630680_1`. The `reg_refs` field contains the added or updated
feature vector key and stream ID with a score of `0`. In case of an update,
the original key is preserved so it can be used as a key for identifying
individuals.

The second record `type` is set to `REID`, which means that the event-trigger
feature vector is similar to an already stored one. The event describes that the
event-trigger feature vector comes from the `exitCamera` stream with a unique
ID. The `reg_refs` field contains a list of the remembered feature vectors
that are similar to the event-trigger feature vector. The key is one of the
earlier registered feature vector keys. `score` measures the similarity
between the two feature vectors (`0.0 ≤ score ≤ 1.0`).

## Feature Demo

For the basic reidentification feature demos, see
[Basic Reidentification with One Camera] and
[Basic Reidentification with Two Cameras].


[Basic Reidentification with One Camera]: ../demo/demo_reid_1.md#basic-reidentification-demo-with-one-camera
[Basic Reidentification with Two Cameras]: ../demo/demo_reid_2.md#basic-reidentification-demo-with-two-cameras
[Kafka superconfiguration proto]: ../../proto_files/ultinous/proto/common/kafka_superconfig.proto
[Kafka configuration proto]: ../../proto_files/ultinous/proto/common/kafka_config.proto
[Kafka data proto]: ../../proto_files/ultinous/proto/common/kafka_data.proto
[Superconfig Authentication Definitions]: conf_superconfig.md#authentication-definition
[Superconfig Topic Definitions]: conf_superconfig.md#topic-definitions
