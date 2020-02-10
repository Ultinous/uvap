---
id: start_fv_clustering
title: Starting Feature Vector Clustering
hide_title: true
---

# Starting Feature Vector Clustering

Starts the Feature Vector Clustering microservice on one or more video streams to 
improve the accuracy of _Reidentification_.  
When using more than one camera to provide multiple input streams, a separate instance 
of the Feature Vector Clustering microservice needs to be started for each input 
stream.

## Prerequisites

It is assumed that **Multi-Graph Runner (MGR)** is running in `fve` mode,
because feature vector  records are necessary input. For more information on
running **MGR**, see [Starting Multi-Graph Runner].

For information on **Feature Vector Clustering** configuration, see
[Configuring Feature Vector Clustering].
  
## Starting Feature Vector Clustering

To start **Feature Vector Clustering**:

1. Run the microservice

   > **Attention!**  
   Before starting this microservice, the command below silently stops and
   removes the Docker container named `uvap_kafka_fvc`, if such already exists.

   ```
   $ "${UVAP_HOME}"/scripts/run_kafka_fvc.sh --instance-id [stream_idx] \
     -- --net=uvap
   ```

   Where `[stream_idx]` is the identifier of the input stream which this 
   instance of the microservice is started for. Start as many instances as the number 
   of cameras. For example, when using two cameras, issue the command twice. Once 
   with value **0** and once with value **1** as the `[stream_idx]`.

   The output of the above command contains the following:
   * Information about pulling the required Docker image
   * The ID of the Docker container created
   * The name of the Docker container created: `uvap_kafka_fvc`

   There are more optional parameters for the `run_kafka_fvc.sh` script to
   override defaults. Use the `--help` parameter to get more details.

1. Check if the `uvap_kafka_fvc` container is running:

   ```
   $ docker container inspect --format '{{.State.Status}}' uvap_kafka_fvc
   ```

   Expected output:

   ```
   running
   ```

   > **Note:**  
   If the status of the UVAP container is not `running`, send the output of
   the following command to `support@ultinous.com`:
   >```
   >$ docker logs uvap_kafka_fvc
   >```

   These Docker containers can be managed with standard Docker commands.
   For more information, see
   <a>
   href="https://docs.docker.com/engine/reference/commandline/docker/"
   target="_blank">
   <i>docker (base command)</i>
   </a> in _docker docs_.

1. Check the output:

   ```
   $ docker exec kafka kafka-console-consumer \
     --bootstrap-server kafka:9092 \
     --topic fve.cam.0.fvc.FVClusterUpdateRecord.json  
   ```

   Expected example output:

   ```
   {"type":"END_OF_INPUT_RECORD"}
   {"type":"END_OF_INPUT_RECORD"}
   {"type":"END_OF_INPUT_RECORD"}
   {"type":"END_OF_INPUT_RECORD"}
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
   {"type":"END_OF_INPUT_RECORD"}
   {"type":"END_OF_INPUT_RECORD"}
   {"type":"END_OF_INPUT_RECORD"}
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
   {"type":"END_OF_INPUT_RECORD"}
   {"type":"END_OF_INPUT_RECORD"}
   {"type":"END_OF_INPUT_RECORD"}
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

[Configuring UVAP]: ../demo/demo_overview.md#configuring-uvap
[Starting Multi-Graph Runner]: start_mgr.md#starting-multi-graph-runner
[Configuring Feature Vector Clustering]: conf_cluster.md
