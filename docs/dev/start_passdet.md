---
id: start_passdet
title: Starting Pass Detector
hide_title: true
---

# Starting Pass Detector

Reads tracks of the detected persons from a JSON topic, and detects crosses on
predefined passlines.

## Prerequisites

It is assumed that **Multi-Graph Runner (MGR)** and **Tracker** is running,
because tracking records are necessary input. For more information on running
**MGR** and **Tracker**, see [Starting Multi-Graph Runner] and
[Starting Tracker].

Path of the configuration file:

```
"${UVAP_HOME}"/config/uvap_kafka_passdet/uvap_kafka_passdet.properties
```

By default, the configuration contains two perpendicular passlines
in the middle of the image, optimized for resolution 1920x1080.

Set different coordinates of passlines by changing the
`ultinous.service.kafka.passdet.config` property.

For more information on **Pass Detector** configuration, see
[Configuring Pass Detector].

Required input topic:

```
<prefix>.cam.0.tracks.TrackChangeRecord.json
```

>**Note:**  
Not available for multiple input streams.
This microservice can only process one input.

## Starting Pass Detector

To start **Pass Detector**:

1. Run the microservice:

   > **Attention!**  
   Before starting this microservice, the command below silently stops and
   removes the Docker container named `uvap_kafka_passdet`, if such already exists.
   
   ```
   $ "${UVAP_HOME}"/scripts/run_kafka_passdet.sh -- --net=uvap
   ```

   The output of the above command contains the following:
   * Information about pulling the required Docker image
   * The ID of the Docker container created
   * The name of the Docker container created: `uvap_kafka_passdet`

   There are more optional parameters for the `run_kafka_passdet.sh` script to
   override defaults. Use the `--help` parameter to get more details.
   
1. Wait for  approximately 30 seconds, then check if the containers are still
   running:

   ```
   $ docker container inspect --format '{{.State.Status}}' uvap_kafka_passdet
   ```
   
   Expected output:
   
   ```
   running
   ```
   
1. Check the output:

   ```
   $ docker exec kafka kafka-console-consumer --bootstrap-server kafka:9092 \
     --topic base.cam.0.passdet.PassDetectionRecord.json
   ```
   
   Expected example output:
   
   ```
   {"type":"HEARTBEAT"}
   {"type":"HEARTBEAT"}
   {"type":"HEARTBEAT"}
   {"type":"HEARTBEAT"}
   {"type":"HEARTBEAT"}
   {"type":"HEARTBEAT"}
   {"type":"HEARTBEAT"}
   {"type":"HEARTBEAT"}
   {"type":"PASS_CANDIDATE","pass_candidate":{"pass":{"id":{"track_key":"1566822226487_2826","serial":0},"pass_line_id":"y","cross_dir":"RL","section_idx":0,"cross_point":{"x":960,"y":103}},"is_extrapolated":false}}
   {"type":"HEARTBEAT"}
   {"type":"PASS_CANDIDATE","pass_candidate":{"pass":{"id":{"track_key":"1566822226487_2826","serial":1},"pass_line_id":"y","cross_dir":"LR","section_idx":0,"cross_point":{"x":960,"y":227}},"is_extrapolated":false}}
   {"type":"HEARTBEAT"}
   {"type":"HEARTBEAT"}
   {"type":"END_OF_TRACK","end_of_track":{"track_key":"1566822226487_2826"}}
   {"type":"HEARTBEAT"}
   {"type":"END_OF_TRACK","end_of_track":{"track_key":"1566822246986_2828"}}
   {"type":"END_OF_TRACK","end_of_track":{"track_key":"1566822247352_2829"}}
   {"type":"HEARTBEAT"}
   {"type":"HEARTBEAT"}
   {"type":"HEARTBEAT"}
   {"type":"HEARTBEAT"}
   ```

The following output topic is created:

```
<prefix>.cam.0.passdet.PassDetectionRecord.json
```


[Configuring Pass Detector]: conf_passdet.md#configuring-pass-detector
[Starting Multi-Graph Runner]: start_mgr.md#starting-multi-graph-runner
[Starting Tracker]: start_track.md#starting-tracker
