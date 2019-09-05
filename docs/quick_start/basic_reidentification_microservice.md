# Basic Reidentification microservice starting

The following steps should be followed to start reidentification on the frames of the previously configured video stream.
It assumes [MGR](mgr_microservice.md) is running in [`fve` mode](../quick_start_guide.md#fveMode), as it needs feature vector records as input.

**Required input topics**
* when only one `stream-uri` was specified in the [configuration](../quick_start_guide.md#configUVAP):
```
fve.cam.0.fvecs.FeatureVectorRecord.json
```
In this case, both registration and reidentification took place in this process
* when `stream-uri` was specified multiple times in the [configuration](../quick_start_guide.md#multipleInput):
 ```
fve.cam.0.fvecs.FeatureVectorRecord.json
fve.cam.1.fvecs.FeatureVectorRecord.json
...
 ```
In this case, the processor runs reidentification based on the feature vectors of reidentification topic (e.g. cam.1) and collects the registration based on the feature vectors of registration topics  (e.g. cam.0).

**Created output topic:**
```
fve.cam.99.reids.ReidRecord.json
```
This is an aggregated topic, consuming feature vectors from every cameras and producing a single topic containing registration and reidentification entries.

1. Run microservice  
    ```
    $ "${UVAP_HOME}"/scripts/run_kafka_reid.sh -- --net=uvap
    ```
    The output of the above command should be:
    * some information about pulling the required Docker image
    * the ID of the Docker container created
    * the name of the Docker container created: `uvap_kafka_reid`

    :exclamation: Warning :exclamation: before starting this
    microservice, the above command will silently stop and remove the
    Docker container named `uvap_kafka_reid`, if such already exists.

    There are more optional parameters for the `run_kafka_reid.sh`
    script to override defaults. Use the `--help` parameter to get more
    details.
1. Check if the container (named `uvap_kafka_reid`) is running:
    ```
    $ docker container inspect --format '{{.State.Status}}' uvap_kafka_reid
    ```
    Expected output:
    ```
    running
    ```
1. Report problem  
    If the status of uvap container is not running then send the output of the following command to `support@ultinous.com`.
    ```
    $ docker logs uvap_kafka_reid
    ```
    These Docker containers can be managed with standard Docker commands. [Learn more...](https://docs.docker.com/engine/reference/commandline/docker/)

1. Check if the fve.cam.99.reids.ReidRecord.json topic is created:
    ```
    $ docker exec kafka kafka-topics --list --zookeeper zookeeper:2181
    ```
    Expected output contains:
    ```
    fve.cam.99.reids.ReidRecord.json
    ```
1. Try to fetch data from the kafka topic:
    ```
    $ docker exec kafka kafka-console-consumer \
    --bootstrap-server kafka:9092 \
    --topic fve.cam.99.reids.ReidRecord.json
    ```
