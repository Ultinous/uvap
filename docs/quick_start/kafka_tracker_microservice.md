# Tracker microservice starting

Reads head detections from a json topic, and creates tracks of the detected persons.
It assumes [MGR](mgr_microservice.md) is running, as it needs object detection records as input.

Required input topic: `base.cam.0.dets.ObjectDetectionRecord.json`  
(Not available for [multiple input streams](../quick_start_guide.md#multipleInput). A microservice can only process one input.)  
Created output topic: `base.cam.0.tracks.TrackChangeRecord.json`

1. Run the microservice:
   ```
   $ "${UVAP_HOME}"/scripts/run_kafka_tracker.sh -- --net=uvap
   ```
    The output of the above command should be:
    * some information about pulling the required Docker image
    * the ID of the Docker container created
    * the name of the Docker container created: `uvap_kafka_tracker`

    :exclamation: Warning :exclamation: before starting this
    microservice, the above command will silently stop and remove the
    Docker container named `uvap_kafka_tracker`, if such already exists.

   There are more optional parameters for the `run_kafka_tracker.sh`
   script to override defaults. Use the `--help` parameter to get more
   details.
1. Wait for ~30 seconds, then check if the containers are still running:
   ```
   $ docker container inspect --format '{{.State.Status}}' uvap_kafka_tracker
   ```
   Expected output:
   ```
   running
   ```
1. Output checking:
   ```
   $ docker exec kafka kafka-console-consumer --bootstrap-server kafka:9092 --topic base.cam.0.tracks.TrackChangeRecord.json
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
