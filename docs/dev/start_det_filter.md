---
id: start_det_filter
title: Starting Detection Filter
hide_title: true
---

# Starting Detection Filter

Starts filtering the detections in the input topic.

## Prerequisites

Each detection filter instance requires one `ObjectDetectionRecord` topic
specified in the configuration.

For information on the **Detection Filter** configuration, see [Configuring the Detection Filter].

## Starting Detection Filter

To start **Detections Filter** run the following command:

```
$ "${UVAP_HOME}"/scripts/run_kafka_detection_filter.sh -- --net=uvap
```

   The output of the above command contains the following:
   * Information about pulling the required Docker image
   * The ID of the Docker container created
   * The name of the Docker container created: `uvap_kafka_detection_filter`	

   There are more optional parameters for the `run_kafka_detection_filter.sh` script to
   override defaults. Use the `--help` parameter to get more details.

1. Check if the `uvap_kafka_detection_filter` container is running:

   ```
   $ docker container inspect --format '{{.State.Status}}' uvap_kafka_detection_filter
   ```
	
   Expected output:
	
   ```
   running
   ```
	
   > **Note:**  
   If the status of the UVAP container is `not running`, send the output of
   the following command to `support@ultinous.com`:
   >```
   >$ docker logs uvap_kafka_detection_filter
   >```
	
   These Docker containers can be managed with standard Docker commands.
   For more information, see
   <a
   href="https://docs.docker.com/engine/reference/commandline/docker/"
   target="_blank">
   <i>docker (base command)</i>
   </a> in _docker docs_.

1. Check if the output topic was created:

   ```
   $ docker exec kafka kafka-topics --list --zookeeper zookeeper:2181
   ```
	
   Expected output contains the following:
	
   ```
   [TOPIC NAME].ObjectDetectionRecord.json
   ```
	
1. Fetch data from the Kafka topic:

   ```
   $ docker exec kafka kafka-console-consumer \
   --bootstrap-server kafka:9092 \
   --topic [TOPIC NAME].ObjectDetectionRecord.json
   ```

The putput `ObjectDetectionRecord` topic is created.

[Configuring the Detection Filter]: conf_det_filter.md