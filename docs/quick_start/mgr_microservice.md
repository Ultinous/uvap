# Multi Graph Runner (MGR) microservice starting

The following steps should be followed to start head detection on the frames of the previously [configured](../quick_start_guide.md#configUVAP) video stream(s).

1. Run the microservice
    ```
    $ "${UVAP_HOME}"/scripts/run_mgr.sh -- --net=uvap
    ```
    The output of the above command should be:
    * some information about pulling the required Docker image
    * the ID of the Docker container created
    * the name of the Docker container created: `uvap_mgr`

    :exclamation: Warning :exclamation: before starting this
    microservice, the above command will silently stop and remove the
    Docker container named `uvap_mgr`, if such already exists.

    There are more optional parameters for the `run_mgr.sh` script to
    override defaults. Use the `--help` parameter to get more details.

    All video devices (`/dev/video*`) on the host (on which the MGR is
    being started with the `run_mgr.sh` script) will be mounted into the
    `uvap_mgr` container.

    If in the [Configuring UVAP section](#uvapConfigSh) pre-recorded
    videos - stored on the local filesystem - have been configured as
    streams to be analyzed, those files need to be mounted into the
    `uvap_mgr` container - this can be done by passing regular Docker
    mount parameters at the end of the above command line (after the
    `--net=uvap` parameter). [Learn more...](https://docs.docker.com/engine/reference/commandline/run/#add-bind-mounts-or-volumes-using-the---mount-flag)  
    For example, if there is a video file on the host
    `/mnt/videos/video1.avi`, and it is configured for the MGR as
    `/some/directory/my_video.avi`, the following command will run the
    MGR accordingly:
    ```
    $ "${UVAP_HOME}"/scripts/run_mgr.sh -- --net=uvap \
      --mount type=bind,readonly,src=/mnt/videos/video1.avi,dst=/some/directory/my_video.avi
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
    These Docker containers can be managed with standard Docker commands. [Learn more...](https://docs.docker.com/engine/reference/commandline/docker/)

1. Check if the kafka topics are created:
    ```
    $ docker exec kafka kafka-topics --list --zookeeper zookeeper:2181
    ```
    Expected results in case of two input stream:
    1. [in `base` mode](../quick_start_guide.md#baseMode)
       ```
       base.cam.0.ages.AgeRecord.json
       base.cam.0.anonymized_original.Image.jpg
       base.cam.0.dets.ObjectDetectionRecord.json
       base.cam.0.frameinfo.FrameInfoRecord.json
       base.cam.0.genders.GenderRecord.json
       base.cam.0.original.Image.jpg
       base.cam.0.poses.HeadPose3DRecord.json
       base.cam.1.ages.AgeRecord.json
       base.cam.1.anonymized_original.Image.jpg
       base.cam.1.dets.ObjectDetectionRecord.json
       base.cam.1.frameinfo.FrameInfoRecord.json
       base.cam.1.genders.GenderRecord.json
       base.cam.1.original.Image.jpg
       base.cam.1.poses.HeadPose3DRecord.json
       ```
    1. [in `fve` mode](../quick_start_guide.md#fveMode)
       ```
       fve.cam.0.dets.ObjectDetectionRecord.json
       fve.cam.0.fvecs.FeatureVectorRecord.json
       fve.cam.0.original.Image.jpg
       fve.cam.1.dets.ObjectDetectionRecord.json
       fve.cam.1.fvecs.FeatureVectorRecord.json
       fve.cam.1.original.Image.jpg
       ```
    1. [in `skeleton` mode](../quick_start_guide.md#skeletonMode)
       ```
       skeleton.cam.0.original.Image.jpg
       skeleton.cam.0.skeletons.SkeletonRecord.json
       skeleton.cam.1.original.Image.jpg
       skeleton.cam.1.skeletons.SkeletonRecord.json
       ```
1. Try to fetch data from a kafka topic:
    ```
    $ docker exec kafka kafka-console-consumer --bootstrap-server kafka:9092 --topic base.cam.0.dets.ObjectDetectionRecord.json
    ```
    Expected example output:
    ```
    {"type":"PERSON_HEAD","detection_confidence":0,"end_of_frame":true}
    {"type":"PERSON_HEAD","detection_confidence":0,"end_of_frame":true}
    {"type":"PERSON_HEAD","bounding_box":{"x":747,"y":471,"width":189,"height":256},"detection_confidence":0.99951756,"end_of_frame":false}
    {"type":"PERSON_HEAD","detection_confidence":0,"end_of_frame":true}
    {"type":"PERSON_HEAD","bounding_box":{"x":730,"y":484,"width":190,"height":255},"detection_confidence":0.991036654,"end_of_frame":false}
    {"type":"PERSON_HEAD","detection_confidence":0,"end_of_frame":true}
    {"type":"PERSON_HEAD","bounding_box":{"x":713,"y":467,"width":173,"height":252},"detection_confidence":0.999676228,"end_of_frame":false}
    {"type":"PERSON_HEAD","detection_confidence":0,"end_of_frame":true}
    {"type":"PERSON_HEAD","bounding_box":{"x":713,"y":467,"width":172,"height":252},"detection_confidence":0.999602616,"end_of_frame":false}
    {"type":"PERSON_HEAD","detection_confidence":0,"end_of_frame":true}
    {"type":"PERSON_HEAD","bounding_box":{"x":701,"y":468,"width":178,"height":253},"detection_confidence":0.999979258,"end_of_frame":false}
    {"type":"PERSON_HEAD","detection_confidence":0,"end_of_frame":true}
    ```
