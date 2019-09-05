# Basic Reidentification

## Table of contents
1. [Introduction](#introduction)
1. [About basic reidentification](#about)
1. [Configuration](#configuration)
1. [Record schemas](#reidRecord)

## Introduction
The Basic Reidentification microservice processes feature vectors and finds re-appearances.

A processed feature vector can be either unknown for the system (in this case it is **registered**), or can already be registered (in this case it is **reidentified**). Each input topic can be used for registering, reidentification or both. The microservice can handle multiple input topics and produces results into one output topic. Role of input topics, reidentification parameters, registration parameters and topic consuming parameters can be configured.

<a name="about"></a>
## About basic reidentification
For each individual, the produced feature vectors correlate, even when changing the distance, head pose, etc. For each pair of feature vectors, a similarity score is produced. This score falls between 0.0 and 1.0; the higher score means, it is more likely that the two feature vectors are representing the same individual. *Basic Reidentification* is recognizing this correlation between feature vectors based on similarity scores.

The microservice does basically two things:
* Registers the new feature vectors coming from registration streams. Feature vectors coming from reidentification-only streams are never stored.
* Tries to reidentify feature vectors coming from reidentification streams. This is proceeded by producing the score with each stored feature vector; the result is controlled by configuration parameters.

## Configuration
This microservice is **not GPU related**. It can be run in batch mode therefore the microservice stops after processing the last source record.

### Environment variables
`KAFKA_REID_MS_PROPERTY_FILE_PATHS`: property files path list.

### Properties
Setting `.data` and `.file` properties are **exclusive** to each other (e.g.: setting both `ultinous.service.kafka.reid.config.data` and `ultinous.service.kafka.reid.config.file` will result an error).
- `ultinous.service.kafka.reid.auth.defs.data`: Authentication definition data in one-liner JSON format corresponding to the definitions at [Authentication definitions](../proto_files/superconfig.md#authDefs).
  - Optional
- `ultinous.service.kafka.reid.auth.defs.file`: Authentication definition file path. Content of the file should be in JSON format described at [Authentication definitions](../proto_files/superconfig.md#authDefs).
  - Optional
- `ultinous.service.kafka.reid.ms.config.data`: Basic Reidentification microservice configuration of source and target topics in one-liner JSON format corresponding to the definitions described at [Superconfig topic definitions](../proto_files/superconfig.md#topicDefs).  
  - **Required** if `ultinous.service.kafka.reid.ms.config.file` is not set.  
  - config_data: Optional `ReidConfigRecord` global reidentification configuration setting in one-liner JSON format.
    - Required if no other Reidentification Configuration is set.  
    - One config fits all.
- `ultinous.service.kafka.reid.ms.config.file`: Basic Reidentification microservice configuration file path. Content must be in one-liner JSON format described at [Superconfig topic definitions](../proto_files/superconfig.md#topicDefs).  
  - **Required** if `ultinous.service.kafka.reid.ms.config.data` is not set.  
  - config_data: Optional `ReidConfigRecord` global reidentification configuration setting in JSON format.
    - Required if no other Basic Reidentification Configuration is set.  
    - One config fits all.
- `ultinous.service.kafka.reid.config.data`: Basic Reidentification configs of input streams defined in JSON format. 
  - Optional. **Should only be set** if the `ReidMSConfig` contains no `config_data` global reidentification configuration.
- `ultinous.service.kafka.reid.config.file`: Basic Reidentification configuration file path. File content must be in one-liner JSON format same as described at `ultinous.service.kafka.reid.config.data` above.  
  - Optional. **Should only be set** if the `ReidMSConfig` contains no `config_data` global reidentification configuration.  
- `ultinous.service.kafka.reid.monitoring.port`: Monitoring server port.
  - Required 
  - Value type: `uint16`
- `ultinous.service.kafka.reid.monitoring.threads`: Monitoring server thread pool size.
  - Required 
  - Value type: `uint16`

<a name="reidRecord"></a>
## Record schemas
Configuration records have been separated into the microservice's **superconfig** (see [ReidMSConfig](../../../../proto_files/ultinous/proto/common/kafka_superconfig.proto)) and the basic reidentification algorithm's **config** (see [ReidConfigRecord](../../../../proto_files/ultinous/proto/common/kafka_config.proto)). The result is a [ReidRecord](../../../../proto_files/ultinous/proto/common/kafka_data.proto).

### An example of a `ReidMSConfig` from Kafka
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
The sources were set to be read from the given date and never stop reading them. Two feature vector sources are defined with broker list and name; the target stream is being replaced.

### An example of a `ReidConfigRecord` from Kafka:
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
The `inputs` field has to contain exactly as many records as many input streams are defined in the `ReidMSConfig` (the i<sup>th</sup> input stream is assigned to the i<sup>th</sup> input config record). The fields' description is as follows:
* `stream_id`: An arbitrary but application-unique name for the input stream. This is later referenced in the results. 
* `fv_field`: The *name* of a `FeatureVectorRecord` type field in the input topic's schema. This field refers to the actual feature vector data.
* `is_active_field`: Optional. The *name* of a boolean type field in the input topic's schema. If set and the field is present in the actual message, the message is not processed if this field has "false" value. This is useful if you want to "turn off" a feature vector in your manually maintained list.  
* `to_be_ignored_field`: Optional. The *name* of a boolean type field in the input topic's schema. If set and the field is present in the actual message, the message is not processed if this field has "true" value. This is necessary because not every [FeatureVectorRecord](../../../../proto_files/ultinous/proto/common/kafka_data.proto) message contains the `features` field, sometimes (for technical reasons) it only contains the `end_of_frame` field which in this case is then set to true.
* `do_reid`: If true, the stream will be used for reidentification. Default is false.  
* `do_reg`: If true, the stream will be used for registration. Default is false.
* `reid_min_score`: Must be set if and only if `do_reg` is true. A score that reaches or exceeds this value is necessary to result a reidentification event, however, match count may still be limited. Must be in the [0.0..1.0] interval, default is 0.0.
* `reid_max_count`: Must be set if and only if `do_reg` is true. Defines the maximum number of the returned matching feature vectors (those which result a score good enough) per registration stream. The actual reidentification result might be as long as the sum of these values defined in the registration streams. Must be positive, but the default is 0.
* `reg_method`: Must not be "NONE"  if and only if `do_reg` is true. Defines what happens to the already registered featurevector of an individual if a new featurevector is recognized (can be either updated to the new one or contribute to a weighted average).
* `reg_max_score`: Must be set if and only if `do_reg` is true. A new feature vector will be registered if there isn't any stored feature vector with which the score reaches or exceeds this value, otherwise the feature vector with which the highest the score is will be updated. Must be in the [0.0..1.0] interval, default is 0.0. The value 1.0 is an exception because in this case each featurevector will be stored.
* `reg_retention_period`: Time interval in milliseconds. Must be set if and only if `do_reg` is true. Feature vectors that have been stored for longer time than this period will be deleted from the registration database. 0 means nothing will ever be deleted. Default is 0.

In the above mentioned case the "entranceCamera" stream has a minimum reidentification score of 0.9 which means the result that is produced from this stream will contain hits that have at least this score value. Other streams may define other minimums. The `reid_max_count` is set to 1 which means at most one reidentification result is produced from this stream. This means that this stream corresponds to the final reidentification result with its most similar feature vector (if the similarity score reaches 0.9).

Also the "entranceCamera" stream's `reg_max_score` is set to 0.7 which means only those new feature vectors are stored which come from this stream and there does not exist a stored feature vector with which the similarity score reaches 0.7.

Note that [0..`reg_max_score`) does not contain its upper boundary but [`reid_min_score`..1\] does contain its lower boundary. This means these two values can be the same (in this case a featurevector will certainly be stored or reidentified). If `reid_min_score` is greater than `reg_max_score` then there exists an interval of scores that is too similar to be remembered but not yet too similar to be recognized.

The `reg_retention_period` of the example stream is 24 hours in milliseconds. That means a new feature vector that is stored will be forgotten after a day.

### Examples of a `ReidRecord` from Kafka:
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
The first record's type is *REG* which means the event-trigger feature vector was not found in the database but now it became stored. The event describes that the feature vector came from the source which has the id "entranceCamera"; the particular feature vector's unique key is 1564038630680_1. The `reg_refs` field contains the added/updated featurevector's key and stream id with a score of 0. In case of an update, the original key is preserved so it can be used as a key for identifying individuals.

The second record's type is *REID* which means that the event-trigger feature vector is similar to an already stored one. The event describes that the event-trigger feature vector came from the "exitCamera" stream with some unique id. The `reg_refs` field now contains a list of the remembered feature vectors that are similar to the event-trigger feature vector. Note that the key is one of the earlier registered feature vector's key. Score measures the similarity between the two feature vectors (0.0 <= score <= 1.0).

## [Quick Start Guide](../../../quick_start_guide.md#reidentification)
