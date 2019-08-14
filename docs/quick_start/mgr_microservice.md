# Multi Graph Runner (MGR) microservice starting

The following steps should be followed to start head detection on the frames of the previously confiugred video stream.

1. Run framework  
    As a first step, you have to start up the framework:
    ```
    $ ~/uvap/scripts/run_mgr.sh --models-directory "$HOME/uvap/models" \
      --license-data-file-path "$(readlink -f ~/uvap/license/license.txt)" \
      --license-key-file-path "$(readlink -f ~/uvap/license/license.key)" -- --net=uvap
    ```
1. Check if the container (named `uvap_mgr`) is running:
    ```
    $ docker container inspect --format '{{.State.Status}}' uvap_mgr
    ```
    Expected output:
    ```
    running
    ```
1. Report problem  
    If the status of uvap container is not running then send the output of the following command to `support@ultinous.com`.
    ```
    $ docker logs uvap_mgr
    ```
    These docker containers can be managed with standard docker commands. [Learn more...](https://docs.docker.com/engine/reference/commandline/docker/)

1. Check if the kafka topics are created:
    ```
    $ docker exec -it kafka /bin/bash -c 'kafka-topics --list --zookeeper zookeeper:2181'
    ```
1. Try to fetch data from a kafka topic:
    ```
    $ kafkacat -b kafka -t base.cam.0.dets.ObjectDetectionRecord.json
    ```
