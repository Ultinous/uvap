# Kafka Pass Detection microservice starting 

Reads tracks of the detected persons from a json topic, and detects crosses on predefined passlines.
It assumes [MGR](mgr_microservice.md) and [Kafka Tracker](kafka_tracker_microservice.md) is running, as it needs tracking records as input.

Required input topic: `<prefix>.cam.0.tracks.TrackChangeRecord.json`

Created output topic: `<prefix>.cam.0.passdet.PassDetectionRecord.json`

The generated configuration is at `~/uvap/models/uvap-kafka-passdet/uvap_kafka_passdet.properties`
contains two perpendicular passlines in the middle of the image, optimized for resolution 1920x1080.

If you want edit it, you have to change the `ultinous.service.kafka.passdet.config` property to set the coordinates of 
your own passlines. Check the [developer guide](../developers_guide/microservices/kafka-passdet.md) to learn more about the possibilities.

1. Run framework:
   ```bash
   $ ~/uvap/scripts/run_kafka_passdet.sh --config-directory "$HOME/uvap/models/uvap-kafka-passdet" -- --net=uvap
   ```

1. Wait for ~30 seconds, then check if the containers are still running:
   ```bash
   $ docker container inspect --format '{{.State.Status}}' uvap_kafka_passdet
   ```
   Expected output:
   ```
   running
   ```
1. Output checking:
   ```bash
   $ kafkacat -b kafka -t base.cam.0.passdet.PassDetectionRecord.json
   ```
   Expected output:
   ```
   {"pass_id":"","cross_dir":"NONE","section_idx":0,"track_key":"1564493674841_50183","is_extrapolated":false,"end_of_track_passes":true}
   {"pass_id":"","cross_dir":"NONE","section_idx":0,"track_key":"","is_extrapolated":false,"end_of_track_passes":false}
   {"pass_id":"","cross_dir":"NONE","section_idx":0,"track_key":"","is_extrapolated":false,"end_of_track_passes":false}
   {"pass_id":"x","cross_dir":"LR","section_idx":0,"cross_point":{"x":593,"y":500},"track_key":"1564493689041_50186","is_extrapolated":false,"end_of_track_passes":false}
   {"pass_id":"","cross_dir":"NONE","section_idx":0,"track_key":"","is_extrapolated":false,"end_of_track_passes":false}
   {"pass_id":"","cross_dir":"NONE","section_idx":0,"track_key":"","is_extrapolated":false,"end_of_track_passes":false}
   {"pass_id":"x","cross_dir":"RL","section_idx":0,"cross_point":{"x":814,"y":500},"track_key":"1564493689041_50186","is_extrapolated":false,"end_of_track_passes":false}
   {"pass_id":"","cross_dir":"NONE","section_idx":0,"track_key":"","is_extrapolated":false,"end_of_track_passes":false}
   {"pass_id":"x","cross_dir":"LR","section_idx":0,"cross_point":{"x":402,"y":500},"track_key":"1564493689041_50187","is_extrapolated":false,"end_of_track_passes":false}
   {"pass_id":"","cross_dir":"NONE","section_idx":0,"track_key":"","is_extrapolated":false,"end_of_track_passes":false}
   {"pass_id":"x","cross_dir":"RL","section_idx":0,"cross_point":{"x":511,"y":500},"track_key":"1564493689041_50187","is_extrapolated":false,"end_of_track_passes":false}
   {"pass_id":"","cross_dir":"NONE","section_idx":0,"track_key":"","is_extrapolated":false,"end_of_track_passes":false}
   {"pass_id":"","cross_dir":"NONE","section_idx":0,"track_key":"","is_extrapolated":false,"end_of_track_passes":false}
   {"pass_id":"","cross_dir":"NONE","section_idx":0,"track_key":"1564493689041_50187","is_extrapolated":false,"end_of_track_passes":true}
   {"pass_id":"","cross_dir":"NONE","section_idx":0,"track_key":"","is_extrapolated":false,"end_of_track_passes":false}
   {"pass_id":"","cross_dir":"NONE","section_idx":0,"track_key":"","is_extrapolated":false,"end_of_track_passes":false}
   {"pass_id":"","cross_dir":"NONE","section_idx":0,"track_key":"","is_extrapolated":false,"end_of_track_passes":false}
   {"pass_id":"","cross_dir":"NONE","section_idx":0,"track_key":"","is_extrapolated":false,"end_of_track_passes":false}
   {"pass_id":"","cross_dir":"NONE","section_idx":0,"track_key":"","is_extrapolated":false,"end_of_track_passes":false}
   {"pass_id":"","cross_dir":"NONE","section_idx":0,"track_key":"","is_extrapolated":false,"end_of_track_passes":false}
   {"pass_id":"","cross_dir":"NONE","section_idx":0,"track_key":"","is_extrapolated":false,"end_of_track_passes":false}
   {"pass_id":"","cross_dir":"NONE","section_idx":0,"track_key":"","is_extrapolated":false,"end_of_track_passes":false}
   {"pass_id":"","cross_dir":"NONE","section_idx":0,"track_key":"","is_extrapolated":false,"end_of_track_passes":false}
   {"pass_id":"","cross_dir":"NONE","section_idx":0,"track_key":"","is_extrapolated":false,"end_of_track_passes":false}
   {"pass_id":"","cross_dir":"NONE","section_idx":0,"track_key":"1564493689041_50186","is_extrapolated":false,"end_of_track_passes":true}
   {"pass_id":"","cross_dir":"NONE","section_idx":0,"track_key":"","is_extrapolated":false,"end_of_track_passes":false}
   {"pass_id":"","cross_dir":"NONE","section_idx":0,"track_key":"","is_extrapolated":false,"end_of_track_passes":false}
   {"pass_id":"","cross_dir":"NONE","section_idx":0,"track_key":"","is_extrapolated":false,"end_of_track_passes":false}
   {"pass_id":"y","cross_dir":"LR","section_idx":0,"cross_point":{"x":960,"y":382},"track_key":"1564493717146_50190","is_extrapolated":false,"end_of_track_passes":false}
   {"pass_id":"","cross_dir":"NONE","section_idx":0,"track_key":"","is_extrapolated":false,"end_of_track_passes":false}
   {"pass_id":"y","cross_dir":"RL","section_idx":0,"cross_point":{"x":960,"y":372},"track_key":"1564493717146_50190","is_extrapolated":false,"end_of_track_passes":false}
   {"pass_id":"","cross_dir":"NONE","section_idx":0,"track_key":"","is_extrapolated":false,"end_of_track_passes":false}
   {"pass_id":"","cross_dir":"NONE","section_idx":0,"track_key":"1564493717146_50190","is_extrapolated":false,"end_of_track_passes":true}
   ```
