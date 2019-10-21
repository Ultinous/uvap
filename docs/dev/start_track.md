---
id: start_track
title: Starting Tracker
hide_title: true
---

# Starting Tracker

Reads head detections from a JSON topic, and creates tracks of the detected persons.

## Prerequisites

It is assumed that **Multi-Graph Runner (MGR)** is running, because object
detection records are necessary input. For more information on running **MGR**,
see [Starting Multi-Graph Runner].

Required input topic:

```
base.cam.0.dets.ObjectDetectionRecord.json
```

>**Note:**  
Not available for multiple input streams.
This microservice can only process one input.

For information on **Tracker** configuration, see [Configuring Tracker].

## Starting Tracker

To start **Tracker**:

1. Run the microservice:

   > **Attention!**  
   Before starting this microservice, the command below silently stops and
   removes the Docker container named `uvap_kafka_tracker`, if such already exists.
   
   ```
   $ "${UVAP_HOME}"/scripts/run_kafka_tracker.sh -- --net=uvap
   ```

   The output of the above command contains the following:
   * Information about pulling the required Docker image
   * The ID of the Docker container created
   * The name of the Docker container created: `uvap_kafka_tracker`

   There are more optional parameters for the `run_kafka_tracker.sh` script to
   override defaults. Use the `--help` parameter to get more details.
   
1. Wait for approximately 30 seconds, then check if the containers are still
   running:

   ```
   $ docker container inspect --format '{{.State.Status}}' uvap_kafka_tracker
   ```
   
   Expected output:
   
   ```
   running
   ```
   
1. Check the output:

   ```
   $ docker exec kafka kafka-console-consumer --bootstrap-server kafka:9092 \
     --topic base.cam.0.tracks.TrackChangeRecord.json
   ```
   
   Expected example output:
   
   ```
   {"end_of_track":false,"detection_key":"1563262804472_0","point":{"x":598,"y":150}}
   {"end_of_track":false,"detection_key":"1563262804472_2","point":{"x":804,"y":249}}
   {"end_of_track":true,"detection_key":""}
   % Reached end of topic base.tracks.TrackChangeRecord.json [0] at offset 4916
   {"end_of_track":false,"detection_key":"1563262804847_0","point":{"x":598,"y":150}}
   {"end_of_track":false,"detection_key":"1563262804847_2","point":{"x":804,"y":249}}
   {"end_of_track":false,"detection_key":"1563262804847_1","point":{"x":1077,"y":353}}
   ```

The following output topic is created:

```
base.cam.0.tracks.TrackChangeRecord.json
```

[Configuring Tracker]: conf_track.md#configuring-tracker
[Starting Multi-Graph Runner]: start_mgr.md#starting-multi-graph-runner
