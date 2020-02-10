---
id: conf_cluster
title: Configuring Feature Vector Clustering
hide_title: true
---

# Configuring Feature Vector Clustering

This microservice is not GPU related. It can be run in batch mode. Depending on the configuration
the microservice either stops after processing the last record or keeps running and waits for more 
records.  
The general part of the configuration defines if _Cluster Merging_, _Cluster Realization_ or both are used.

## Environment Variables

* `KAFKA_FVC_MS_PROPERTY_FILE_PATHS`: property files path list.

## Properties

### ultinous.service.kafka.feature.vector.clustering.auth.defs.data

| Property      | `ultinous.service.kafka.feature.vector.clustering.auth.defs.data`     |
| ------------- | --------------------------------------------------------------------- |
| Description   | Authentication definition data in JSON format corresponding to the definitions described in [Superconfig Authentication Definitions]. |
| Required      | Optional                                                              |

### ultinous.service.kafka.feature.vector.clustering.auth.defs.file

| Property      | `ultinous.service.kafka.feature.vector.clustering.auth.defs.file`     |
| ------------- | --------------------------------------------------------------------- |
| Description   | Authentication definition file path in JSON format corresponding to the definitions described in [Superconfig Authentication Definitions]. |
| Required      | Optional                                                              |

### ultinous.service.kafka.feature.vector.clustering.ms.config.data

| Property      | `ultinous.service.kafka.feature.vector.clustering.ms.config.data`     |
| ------------- | --------------------------------------------------------------------- |
| Description   | **Feature Vector Clustering** microservice configuration in JSON format corresponding to the definitions described in [Superconfig Topic Definitions]. |
| Required      | Required                                                              |

### ultinous.service.kafka.feature.vector.clustering.ms.config.file

| Property      | `ultinous.service.kafka.feature.vector.clustering.ms.config.file`     |
| ------------- | --------------------------------------------------------------------- |
| Description   | **Feature Vector Clustering** microservice configuration file path in JSON format corresponding to the definitions described in [Superconfig Topic Definitions]. |
| Required      | Required                                                              |

### ultinous.service.kafka.feature.vector.clustering.config.data

| Property      | `ultinous.service.kafka.feature.vector.clustering.config.data`        |
| ------------- | --------------------------------------------------------------------- |
| Description   | Clustering configuration defined in JSON format.                      |
| Required      | Optional                                                              |
| Notes         | Set only if the global configuration does not contain service configuration (the `configData` field is not set for `ClusteringConfigRecord`). |

### ultinous.service.kafka.feature.vector.clustering.config.file

| Property      | `ultinous.service.kafka.feature.vector.clustering.config.file`        |
| ------------- | --------------------------------------------------------------------- |
| Description   | Clustering configuration file path in JSON format                     |
| Required      | Optional                                                              |
| Notes         | Set only if the global configuration does not contain service configuration (the `configData` field is not set for `ClusteringConfigRecord`). |                                                               |

### ultinous.service.kafka.feature.vector.clustering.monitoring.port

| Property      | `ultinous.service.kafka.feature.vector.clustering.monitoring.port`    |
| ------------- | --------------------------------------------------------------------- |
| Description   | Monitoring server port.                                               |
| Required      | Required                                                              |
| Value Type    | `uint16`                                                              |

### ultinous.service.kafka.feature.vector.clustering.monitoring.threads

| Property      | `ultinous.service.kafka.feature.vector.clustering.monitoring.threads` |
| ------------- | --------------------------------------------------------------------- |
| Description   | Monitoring server thread pool size.                                   |
| Required      | Required                                                              |
| Value Type    | `uint16`                                                              |  

## Record Schemas

Configuration records are separated into the following values:

* `ClusteringMSConfig` specified in [Kafka superconfiguration proto]
* `FVClusteringConfigRecord` specified in [Kafka configuration proto]

While the output record is defined as `FVClusterUpdateRecord` specified in [Kafka data proto].

### Example of a ClusteringMSConfig from Kafka

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

In this example, the sources are set to be read from the given date and never stop being read (no end time is specified). Two feature vector sources are defined with broker list and name. The target stream is being replaced and also defined with broker list and name.

### Example of an FVClusteringConfigRecord from Kafka

```
{
   "clustering_config": {
       "method": "[USE_LAST | SIMPLE_AVERAGE | EXP_AVERAGE]",
       "cluster_merging": {
           "initial_threshold": 0.8,
           "threshold_discount_rate": 0.95,
           "min_threshold": 0.6,
           "time_interval_ms": 4
       },
       "cluster_realization": {
           "num_samples": 5,
           "time_limit_ms": 10000
       },
       "save_internal_state": true,
       "start_from_internal_state": true
   },
   "input_stream_configs": [{
       "stream_id": "camera_1",
       "fv_field_selector": {
           "[feature_vector_path | fv_cluster_path]": "features"
       },
       "reg_stream_config": {
           "reg_threshold": 0.8,
           "cluster_retention_period_ms": 86400000,
       },
   }]
}
```  
***FVClusteringConfigRecord Example***  
_See the table below for field descriptions._


| Field                         | Description |
| ----------------------------- | ----------- |
| `clustering_config`           | Configuration for the clustering. |
| `method`                      | Defines the clustering method. See [Clustering Methods] for possible values. |
| `cluster_merging`             | Shows that the event is a merge attempt, triggered by the first input arriving after the time interval set by `time_interval_ms` since the last attempt. Clusters more similar to each other than the [Current Similarity Threshold] are merged.<br>Optional, must be null for `"method": "USE_LAST"` |
| `initial_threshold`           | Child parameter of `cluster_merging`. Initial similarity threshold value. See [Current Similarity Threshold]. |
| `threshold_discount_rate`     | Child parameter of `cluster_merging`. Rate of decreasing the similarity threshold. See [Current Similarity Threshold]. |
| `min_threshold`               | Child parameter of `cluster_merging`. Minimal value of the similarity threshold. See [Current Similarity Threshold]. |
| `time_interval_ms`            | Child parameter of `cluster_merging`. Time interval set in milliseconds. |
| `cluster_realization`         | Shows that the event is a cluster realization.<br>Optional, must be null for `"method": "USE_LAST"`. |
| `num_samples`                 | Child parameter of `cluster_realization`. The number of observations in realized clusters. (when feasible within the set time limit). |
| `time_limit_ms`               | Child parameter of `cluster_realization`. A time limit set in milliseconds for realization even if the number of observations does not reach the value set by `num_samples`.<br>Measured from the first observation belonging to the cluster, after the previous realization of the same cluster. |
| `save_internal_state`         | If set to `true`, internal states are saved to a dedicated Kafka topic. See [Save and Start from Internal State]. |
| `start_from_internal_state`   | If set to `true`, the saved internal states are used to rebuild the DB instead of the input topics when the Feature Vector Clustering microservice starts. See [Save and Start from Internal State]. |
| `input_stream_configs`        | Configuration for input streams. Must contain the same number of records as the number of input streams defined in `ClusteringMSConfig` (the i<sup>th</sup> input stream is assigned to the i<sup>th</sup> configuration record). |
| `stream_id`                   | An arbitrary but application-unique name for the input stream. |
| `fv_field_selector`           | Selects a feature vector or cluster field in the input record. See `feature_vector_path` and `fv_cluster_path` child parameters. |
| `feature_vector_path`         | Child parameter of `fv_field_selector`. Specifies the path to a field of type `FeatureVector` within the input record.<br>String. |
| `fv_cluster_path`             | Child parameter of `fv_field_selector`. Specifies the path to a field of type `FVCluster` within the input record.<br>String. |
| `reg_stream_config`           | Contains the properties of the registration stream. |
| `reg_threshold`               | Child parameter of `reg_stream_config`. If the similarity between the input feature vector and any stored cluster is less than this value, a new cluster is registered. Otherwise, the cluster with the highest similarity score is updated. <br>Must be in the `[0.0..1.0]` interval, default is `0.0`. The value `1.0` means that every feature vector is stored. |
| `cluster_retention_period_ms` | Child parameter of `reg_stream_config`. Time interval in milliseconds; clusters stored for longer time than this period are deleted from the registration database. `0` means nothing is deleted.<br>Default is `0`.<br>Cluster delete events are triggered by the first input after the retention period expires.<br>The same period is used to look back to the previous inputs at startup when `start_from_internal_state` is false. |  
|`realized_cluster_action`      | Determines how realized clusters are handled:<br>`0`: **INVALID**<br>`1`: **REMOVE** - Remove the realized cluster from internal DB. A delete event is triggered.<br>`2`: **UNREALIZE** - The realized cluster becomes unrealized until `num_samples` number of new observations arrive again.<br>`3`: **KEEP REALIZED** - Once realized, the cluster remains realized until removed.  
  
<a name="clustering_methods"></a>
**Clustering methods**  
The following values are valid for the `method` field:

* `USE_LAST`: If an observed feature vector is recognized to belong to a
  previously stored cluster, its representative feature vector is replaced
  by the newly observed one.

* `SIMPLE_AVERAGE`: Stores the average feature vector of the matching observations as cluster representative, and the number of samples (that are averaged).

<a name="current_threshold"></a>
> **Current Similarity Threshold**
>
>```
>current_threshold = max(min_threshold, initial_threshold × threshold_discount_rate^num_inputs)
>```
>
>where `num_inputs` is the sum of the potentially mergeable clusters.

### Examples of FVClusterUpdateRecord from Kafka

`FVClusterUpdateRecord` can have the following events indicated by the `type` field:

* `REG_EVENT`: the event is a registration or a cluster update
* `MERGE_EVENT`: the event is a cluster merge (some clusters are merged into one)
* `DELETE_EVENT`: the event is a cluster removal (its retention period expires)
* `END_OF_INPUT_RECORD`: the input is processed and there are no more messages:
   
   ```
   {"type":"END_OF_INPUT_RECORD"}
   ```

#### Registration FVClusterUpdateRecord Example

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

* The observed feature vector or cluster is not found in the database, so a
  new cluster is created.

* The observed feature vector or cluster is found in the database,
  so an already stored cluster is updated.

The record shows the same information in both cases.


The `input_stream_id` field of the event shows that the feature vector comes from
the source which has the ID `entranceCamera`.

The `cluster_id` field contains the time, key and stream information of the
detection.

The `cluster` field contains information about the stored cluster.
The `representative_fv` field is a representation of all feature vectors in
this cluster. It is not necessarily equal to any input feature vector.
`num_observations` shows the number of input feature vectors belonging
to this cluster.

`is_realized` shows if a cluster is ready to be used for further processing,
see `cluster_realization` in [`FVClusteringConfigRecord`].
If its value is `false`, then outputs are only saved to keep track of input
keys and their clusters.

#### Merge FVClusterUpdateRecord Example

```
{"type":"MERGE_EVENT",
  "merge_event":
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
      },
	"merged_clusters":
      [
        {
          "first_detection_time":"1571138183912",
          "first_detection_key":"1571138183912_0",
          "first_detection_stream_id":"entranceCamera"
        }
        {
          "first_detection_time":"1571146859533",
          "first_detection_key":"1571146859533_0",
          "first_detection_stream_id":"entranceCamera"
        }
      ]
  }
}
```

This example shows a `merge_event` event, meaning that some clusters are merged
into one.

The `cluster_id` field contains the time, key and stream information after
merging.

The `cluster` field contains information about the stored cluster after merging.
The `representative_fv` field is a representation of all feature vectors in
this cluster. It is not necessarily equal to any input feature vector.
`num_observations` shows the number of input feature vectors belonging
to this cluster.

The `merged_clusters` field contains a list of records containing information
of the merged clusters

#### Deletion FVClusterUpdateRecord Example

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
period, see `cluster_retention_period` in [`FVClusteringConfigRecord`].

The `deleted_cluster` field contains the first detection time, key and stream
information of the deleted cluster.


[Clustering Methods]: #clustering_methods
[Current Similarity Threshold]: #current_threshold
[`FVClusteringConfigRecord`]: #example-of-an-fvclusteringconfigrecord-from-kafka
[Kafka superconfiguration proto]: ../../proto_files/ultinous/proto/common/kafka_superconfig.proto
[Kafka configuration proto]: ../../proto_files/ultinous/proto/common/kafka_config.proto
[Kafka data proto]: ../../proto_files/ultinous/proto/common/kafka_data.proto
[Superconfig Authentication Definitions]: conf_superconfig.md#authentication-definition
[Superconfig Topic Definitions]: conf_superconfig.md#topic-definitions  
[Save and Start from Internal State]: func_save_start_from_int_state.md
