# Kafka Pass Detection microservice starting 

Reads tracks of the detected persons from a json topic, and detects crosses on predefined passlines.
It assumes [MGR](mgr_microservice.md) and [Kafka Tracker](kafka_tracker_microservice.md) is running, as it needs tracking records as input.

Required input topic: `<prefix>.cam.0.tracks.TrackChangeRecord.json`  
(Not available for [multiple input streams](../quick_start_guide.md#multipleInput). A microservice can only process one input.)  
Created output topic: `<prefix>.cam.0.passdet.PassDetectionRecord.json`

The generated configuration is at `"${UVAP_HOME}"/config/uvap_kafka_passdet/uvap_kafka_passdet.properties`
contains two perpendicular passlines in the middle of the image, optimized for resolution 1920x1080.

If you want edit it, you have to change the `ultinous.service.kafka.passdet.config` property to set the coordinates of 
your own passlines. Check the [developer guide](../developers_guide/microservices/kafka-passdet.md) to learn more about the possibilities.

1. Run microservice:
   ```
   $ "${UVAP_HOME}"/scripts/run_kafka_passdet.sh -- --net=uvap
   ```
    The output of the above command should be:
    * some information about pulling the required Docker image
    * the ID of the Docker container created
    * the name of the Docker container created: `uvap_kafka_passdet`

    :exclamation: Warning :exclamation: before starting this
    microservice, the above command will silently stop and remove the
    Docker container named `uvap_kafka_passdet`, if such already exists.

   There are more optional parameters for the `run_kafka_passdet.sh`
   script to override defaults. Use the `--help` parameter to get more
   details.
1. Wait for ~30 seconds, then check if the containers are still running:
   ```
   $ docker container inspect --format '{{.State.Status}}' uvap_kafka_passdet
   ```
   Expected output:
   ```
   running
   ```
1. Output checking:
   ```
   $ docker exec kafka kafka-console-consumer --bootstrap-server kafka:9092 --topic base.cam.0.passdet.PassDetectionRecord.json
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
