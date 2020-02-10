---
id: conf_reid
title: Configuring Reidentifier
hide_title: true
---

# Configuring Reidentifier

This microservice is not GPU related. It can be run in batch mode, therefore the
microservice stops after processing the last source record.

## Environment Variables

* `KAFKA_REID_MS_PROPERTY_FILE_PATHS`: property files path list.

## Properties

>**Attention!**  
Setting `.data` and `.file` properties are exclusive to each other, meaning
setting both `ultinous.service.kafka.reid.config.data` and
`ultinous.service.kafka.reid.config.file` results in an error.

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
| Description   | **Reidentifier** microservice configuration of source and target topics in one-liner JSON format corresponding to the definitions described in [Superconfig Topic Definitions]. |
| Required      | Required                                               |
| Notes         | Required if no other reidentification configuration is set.<br> One configuration fits all. |

### ultinous.service.kafka.reid.ms.config.file
	
| Property      | `ultinous.service.kafka.reid.ms.config.file`    |
| ------------- | ------------------------------------------------------ |
| Description   | **Reidentifier** microservice configuration file path. Content must be in one-liner JSON format described in [Superconfig Topic Definitions].  |
| Required      | Required                                               |
| Notes         | Required if no other reidentification configuration is set.<br> One configuration fits all. |

### ultinous.service.kafka.reid.config.data

| Property      | `ultinous.service.kafka.reid.config.data`    |
| ------------- | ------------------------------------------------------ |
| Description   | **Reidentifier** configurations of input streams defined in JSON format. |
| Required      | Optional                                               |
| Notes         | Should only be set if the `ReidMSConfig` contains no `config_data` global reidentification configuration. |

### ultinous.service.kafka.reid.config.file
  
| Property      | `ultinous.service.kafka.reid.config.file`   |
| ------------- | ------------------------------------------------------ |
| Description   | **Reidentifier** configuration file path. File content must be in one-liner JSON format same as described at `ultinous.service.kafka.reid.config.data` above. |
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
      "name":"staff.FeatureVectorRecord.json",
      "auth_ref":"srcAuth"
    }
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
"config_data":
  {
   "clustering_config": {
     "method": "USE_LAST"
   },
   "input_stream_configs": [  
      {
       "stream_id": "person",
       "fv_field_selector": {
         "feature_vector_path": "features"
       },
       "person_stream_config": 
        {
         "cluster_retention_period_ms": 3600000
        }
     }
     {
       "stream_id": "entranceCamera",
       "fv_field_selector": {
         "fv_cluster_path": "reg_event.cluster"
       },
       "camera_stream_config": {
         "reg_stream_config": {
           "reg_threshold": 0.9,
           "cluster_retention_period_ms": 3600000
         }
       }
     },
     {
       "stream_id": "exitCamera",
       "fv_field_selector": {
         "fv_cluster_path": "reg_event.cluster"
       },
       "camera_stream_config": {
         "reid_stream_config": {
           "min_similarity": 0.8,
           "max_num_matches": 1
         }
       }
     }
   ]
  }
```

The `clustering_config` field contains information of clustering configuration.
Here, `method` defines the clustering method. The only valid entry is
`USE_LAST`, which means that if an observed feature vector is recognized to
belong to a previously stored cluster, its representative feature vector is
replaced by the new observation.

The `input_stream_configs` field has to contain the exact same amount of records
as the number of input streams defined in `ReidMSConfig` (the i<sup>th</sup>
input stream is assigned to the i<sup>th</sup> configuration record).
See the table below for the field descriptions:

| Input                         | Description |
| ----------------------------- | ----------- |
| `stream_id`                   | An arbitrary but application-unique name for the input stream. This is later referenced in the results. |
| `fv_field_selector`           | Selects a feature vector or cluster field in the input record. See `feature_vector_path` and `fv_cluster_path` child parameters. |
| `feature_vector_path`         | Child parameter of `fv_field_selector`. Specifies the path to a field of type `FeatureVector` within the input record. |
| `fv_cluster_path`             | Child parameter of `fv_field_selector`. Specifies the path to a field of type `FVCluster` within the input record. |
| `camera_stream_config`        | Indicates that the input is a camera stream. |
| `reg_stream_config`           | Child parameter of `camera_stream_config`. Indicates that the stream is used for registration.|
| `reg_threshold`               | Child parameter of `reg_stream_config`. If the similarity between the input feature vector and any stored cluster is less than this value, a new cluster is registered. Otherwise, the cluster with the highest similarity score is updated. <br>Must be in the `[0.0..1.0]` interval, default is `0.0`. The value `1.0` means that every feature vector is stored.|
| `cluster_retention_period_ms` | Child parameter of `reg_stream_config`. Time interval in milliseconds; clusters stored for longer time than this period are deleted from the registration database. `0` means nothing is deleted.<br>Default is `0`.|
| `reid_stream_config`          | Child parameter of `camera_stream_config`. Indicates that the stream is used for reidentification.|
| `min_similarity`              | Child parameter of `reid_stream_config`. Similarity value. If the similarity score (see `score` under [`ReidRecord`]) between the input and a stored cluster reaches this value, a reidentification event takes place. <br> Must be in the `[0.0..1.0]` interval, default is `0.0`. <br> Match count can still be limited, see `max_num_matches`. |
| `max_num_matches`             | Child parameter of `reid_stream_config`. Defines the maximum number of the returned matching clusters (with a score above `min_similarity`). <br>Must be positive.|

>**Note:**  
If the input is a cluster topic, `fv_field_selector` must contain `fv_cluster_path`
instead of `feature_vector_path`.

In this example, the `exitCamera` stream has a minimum
reidentification score of `0.8` set by `min_similarity`,
which means the result produced from this
stream contains hits that have at least this score value.

The `max_num_matches` is set to `1`, meaning one
reidentification result is produced from this stream at the most. This means that
the stream corresponds to the final reidentification result with its most
similar feature vector (if the similarity score reaches `0.8`).

The `reg_threshold` of `entranceCamera` stream is set to `0.9`. This means that
— from this stream — only those feature vectors are stored that reach the similarity
score of `0.9`.

The `cluster_retention_period_ms` of the example stream is 1 hour in milliseconds.
That means that a newly stored cluster is forgotten after one hour. The
retention period is counted from the last update of a cluster — either it
is a newly set or an updated one.

### Examples of a ReidRecord from Kafka

`ReidRecord` can have the following events indicated by the `type` field:

* `REG_EVENT`: the event is a registration or a cluster update
* `REID_EVENT`: the event is a reidentification
* `DELETE_EVENT`: the event is a cluster removal
* `END_OF_INPUT_RECORD`: the input is processed and there are no more messages:
   
   ```
   {"type":"END_OF_INPUT_RECORD"}
   ```

#### Registration ReidRecord Example

```
{"type":"REG_EVENT",
 "reg_event":
  {
    "cluster_id":
      {
        "first_detection_time":"1571138183912",
        "first_detection_key":"1571138183912_0",
        "first_detection_stream_id":"entranceCamera"
      },
    "cluster":
      {
        "representative_fv":
          {
            "model_id":"face_rec_v6",
            "feature":[-0.884964168,-0.394254386, ... ,0.100110188,0.529844344],
            "type":"PERSON_FACE"
          },
        "num_observations":1
        "is_realized":true
      },
    "input_stream_id":"entranceCamera",
  }
}
```


This example shows a `reg_event` event, which refers to one of the following
cases:

* The recognized feature vector or cluster is not found in the database, so a
  new cluster is created.

* The recognized feature vector or cluster is found in the database,
  so an already stored cluster is updated.

The record shows the same information in both cases.


The `input_stream_id` field of event shows that the feature vector comes from
the source which has the ID `entranceCamera`.

The `cluster_id` field contains the time, key and stream information of the
detection.

The `cluster` field contains information about the stored cluster.

The `representative_fv` field is a representation of all feature vectors in
this cluster. It is not necessarily equal to any input feature vector.

`num_observations` shows the number of input feature vectors belonging
to this cluster.

`is_realized` shows if a cluster is ready to be used for further processing
(see `ClusterRealizationConfig` in the [Kafka configuration proto].)
If it has the value `false`, outputs are only saved to keep track of input
keys and their clusters.

#### Reidentification ReidRecord Example

```
{"type":"REID_EVENT",
 "reid_event":
  {
    "match_list":
      [
        {
          "id":
            {
              "first_detection_time":"1571138183912",
              "first_detection_key":"1571138183912_0",
              "first_detection_stream_id":"entranceCamera"
            },
          "score":0.988238931
        }
      ],
    "input_stream_id":"exitCamera"
  }
}
```

This example shows a `reid_event` event, meaning that the recognized feature
vector is similar to a stored cluster, so it is reidentified.

The `match_list` field contains a list of the stored culsters
that are similar to the input feature vector. The `id` field contains the time,
key, and stream information of the first detection of a feature vector belonging
to the matching cluster; while `score` measures the similarity between the input
feature vector and the matching cluster (`0.0 ≤ score ≤ 1.0`). The higher the
score, the greater the similarity.

The `input_stream_id` of the event shows that the feature vector comes from
the source which has the ID `exitCamera`.

#### Deletion ReidRecord Example

```
{"type":"DELETE_EVENT",
  "delete_event":
    {
      "deleted_cluster":
        {
          "first_detection_time":"1571138183912",
          "first_detection_key":"1571138183912_0",
          "first_detection_stream_id":"entranceCamera"
        }
      }
}
```

This example shows a `delete_event` event, meaning that a cluster is deleted
because its retention period expired. For information on cluster retention
period, see `cluster_retention_period` in [`ReidConfigRecord`].

The `deleted_cluster` field contains the first detection time, key and stream
information of the deleted cluster.

## Person Stream Configuration

The person stream can be used to add, update, or delete clusters in the internal
database of the Reidentifier.

The Reidentifier reads the Person Stream if `person_stream_config` is specified
in the `input_stream_configs`, see the [Kafka configuration proto]. The topic
settings of person streams may differ from those of camera streams, see 
`ReidMSConfig` in the [Kafka superconfiguration proto].

In the person stream, the `key` of the individual records can be changed to any
desired string (for example the name of the person or a unique ID). In addition
to the key, the record must contain a payload that has a feature vector or cluster field.

### Managing the Person Stream  
  
To modify a feature vector cluster in the internal reidentification database, add a
record to the person stream where the key is the key of the cluster to be modified
and the payload contains the new feature vector.

To delete a feature vector from the person stream, add a record to the person
stream where the key is the key of the cluster to be deleted and the payload is
empty.

### Example Person Stream Record:

```
{
  "key": "employee_1",
  "payload": {
    "features": {
      "model_id": "face_rec_v6",
      "feature": [-0.974957268,-0.414262786, ... ,0.200180188,0.489824344],
      "type": "PERSON_FACE"
    },
    "end_of_frame": false
  }
}
```

In this example the unique key is `"employee_1"` and the corresponding payload is the
1024 byte long feature vector contained in `feature: [-0.974957268,-0.414262786, ... ,0.200180188,0.489824344]`.


## Feature Demo

For the reidentification feature demos, see
[Single-Camera Reidentification Demo with Pre-clustering] and 
[Reidentification Demo with Person Names].


[Single-Camera Reidentification Demo with Pre-clustering]: ../demo/demo_reid_1.md#reidentification-demo-with-one-camera
[Kafka superconfiguration proto]: ../../proto_files/ultinous/proto/common/kafka_superconfig.proto
[Kafka configuration proto]: ../../proto_files/ultinous/proto/common/kafka_config.proto
[Kafka data proto]: ../../proto_files/ultinous/proto/common/kafka_data.proto
[`ReidRecord`]: #reidentification-reidrecord-example
[`ReidConfigRecord`]: #example-of-a-reidconfigrecord-from-kafka
[Superconfig Authentication Definitions]: conf_superconfig.md#authentication-definition
[Superconfig Topic Definitions]: conf_superconfig.md#topic-definitions  
[Reidentification Demo with Person Names]: ../demo/demo_reid_with_name.md
