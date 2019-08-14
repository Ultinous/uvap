# Tracker microservice starting

Reads head detections from a json topic, and creates tracks of the detected persons.
It assumes MGR is running, as it needs object detection records as input.

Required input topic: `<prefix>.cam.0.dets.ObjectDetectionRecord.json`  
Created output topic: `<prefix>.cam.0.tracks.TrackChangeRecord.json`

1. Run framework:
   ```bash
   $ ~/uvap/scripts/run_kafka_tracker.sh --config-directory "$HOME/uvap/models/uvap-kafka-tracker" -- --net=uvap
   ```

1. Wait for ~30 seconds, then check if the containers are still running:
   ```bash
   $ docker container inspect --format '{{.State.Status}}' uvap_kafka_tracker
   ```
   Expected output:
   ```
   running
   ```
1. Output checking:
   ```bash
   $ kafkacat -b kafka -t base.cam.0.tracks.TrackChangeRecord.json
   ```
   Expected output:
   ```
   {"end_of_track":false,"detection_key":"1563262804472_0","point":{"x":598,"y":150}}
   {"end_of_track":false,"detection_key":"1563262804472_2","point":{"x":804,"y":249}}
   {"end_of_track":true,"detection_key":""}
   % Reached end of topic base.tracks.TrackChangeRecord.json [0] at offset 4916
   {"end_of_track":false,"detection_key":"1563262804847_0","point":{"x":598,"y":150}}
   {"end_of_track":false,"detection_key":"1563262804847_2","point":{"x":804,"y":249}}
   {"end_of_track":false,"detection_key":"1563262804847_1","point":{"x":1077,"y":353}}
   ```
