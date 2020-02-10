---
id: start_reid
title: Starting Reidentifier
hide_title: true
---

# Starting Reidentifier

Starts reidentification on the frames of a previously configured video stream.

## Prerequisites

It is assumed that **Multi-Graph Runner (MGR)** is running in `fve` mode,
because feature vector  records are necessary input. For more information on
running **MGR**, see [Starting Multi-Graph Runner].

Required input topics:

* If only one `[STREAM_URI]` was specified during configuration:
  
  ```
  fve.cam.0.fvecs.FeatureVectorRecord.json
  ```

  In this case, both registration and reidentification takes place
  in this process

* If multiple `[STREAM_URI]` were specified during configuration:

  ```
  fve.cam.0.fvecs.FeatureVectorRecord.json
  fve.cam.1.fvecs.FeatureVectorRecord.json
  ...
  ```
  
  In this case, the processor runs reidentification based on the
  feature vectors of reidentification topic (for example, `cam.1`),
  and collects the registration based on the feature vectors of
  registration topics (for example, `cam.0`).

For information on **Reidentifier** configuration, see
[Configuring Reidentifier].

## Starting Reidentifier

To start **Reidentifier**:

1. Run the microservice

   > **Attention!**  
   Before starting this microservice, the command below silently stops and
   removes the Docker container named `uvap_kafka_reid`, if such already exists.
   
   ```
   $ "${UVAP_HOME}"/scripts/run_kafka_reid.sh -- --net=uvap
   ```

   The output of the above command contains the following:
   * Information about pulling the required Docker image
   * The ID of the Docker container created
   * The name of the Docker container created: `uvap_kafka_reid`	

   There are more optional parameters for the `run_kafka_reid.sh` script to
   override defaults. Use the `--help` parameter to get more details.
	
1. Check if the `uvap_kafka_reid` container is running:

   ```
   $ docker container inspect --format '{{.State.Status}}' uvap_kafka_reid
   ```
	
   Expected output:
	
   ```
   running
   ```
	
   > **Note:**  
   If the status of the UVAP container is `not running`, send the output of
   the following command to `support@ultinous.com`:
   >```
   >$ docker logs uvap_kafka_reid
   >```
	
   These Docker containers can be managed with standard Docker commands.
   For more information, see
   <a
   href="https://docs.docker.com/engine/reference/commandline/docker/"
   target="_blank">
   <i>docker (base command)</i>
   </a> in _docker docs_.

1. Check if the `fve.cam.99.reids.ReidRecord.json` topic is created:

   ```
   $ docker exec kafka kafka-topics --list --zookeeper zookeeper:2181
   ```
	
   Expected output contains the following:
	
   ```
   fve.cam.99.reids.ReidRecord.json
   ```
	
1. Fetch data from the Kafka topic:

   ```
   $ docker exec kafka kafka-console-consumer \
   --bootstrap-server kafka:9092 \
   --topic fve.cam.99.reids.ReidRecord.json
   ```

The following output topic is created:

```
fve.cam.99.reids.ReidRecord.json
```

This is an aggregated topic, consuming feature vectors from every cameras and producing a single topic containing registration and reidentification entries.

[Configuring Reidentifier]: conf_reid.md#configuring-reidentifier
[Starting Multi-Graph Runner]: start_mgr.md#starting-multi-graph-runner
