---
id: start_mgr
title: Starting Multi-Graph Runner
hide_title: true
---

# Starting Multi-Graph Runner

Starts head detection on the frames of a previously configured video stream.

## Prerequisites

It is assumed that UVAP is properly configured. For more information on
configuration, see [Configuring UVAP].

For information on **Multi-Graph Runner (MGR)** configuration, see
[Configuring Multi-Graph Runner].

## Starting Multi-Graph Runner 

To start **MGR**:

1. Run the microservice:

   > **Attention!**  
   Before starting this microservice, the command below silently stops and
   removes the Docker container named `uvap_mgr`, if such already exists.
   
   ```
   $ "${UVAP_HOME}"/scripts/run_mgr.sh -- --net=uvap
   ```
	
   The output of the above command contains the following:
   * Information about pulling the required Docker image
   * The ID of the Docker container created
   * The name of the Docker container created: `uvap_mgr`

   There are more optional parameters for the `run_mgr.sh` script to
   override defaults. Use the `--help` parameter to get more details.

   All video devices (`/dev/video*`) on the host — on which the **MGR**
   is being started with the `run_mgr.sh` script — is mounted into the
   `uvap_mgr` container.

   If prerecorded videos (stored on the local filesystem) are configured as
   streams to be analyzed, the files need to be mounted into the `uvap_mgr`
   container – this can be done by passing regular Docker mount parameters
   at the end of the above command line (after the `--net=uvap` parameter).
   For more information on Docker mounting, see
   <a
   href="https://docs.docker.com/engine/reference/commandline/run/#add-bind-mounts-or-volumes-using-the---mount-flag"
   target="_blank">
   <i>Add bind mounts or volumes using the --mount flag</i>
   </a> in _docker docs_.
   
   For example, if there is a video file on the host
   `/mnt/videos/video1.avi`, and it is configured for **MGR** as
   `/some/directory/my_video.avi`, the following command runs
   **MGR** accordingly:
   
   ```
   $ "${UVAP_HOME}"/scripts/run_mgr.sh -- --net=uvap \
     --mount type=bind,readonly,src=/mnt/videos/video1.avi,dst=/some/directory/my_video.avi
   ```
   
1. Check if the `uvap_mgr` container is running:

   ```
   $ docker container inspect --format '{{.State.Status}}' uvap_mgr
   ```

   Expected output:
	
   ```
   running
   ```

   > **Note:**  
   If the status of the UVAP container is `not running`, send the output of
   the following command to `support@ultinous.com`:
   >```
   >$ docker logs uvap_mgr
   >```
	
   These Docker containers can be managed with standard Docker commands.
   For more information, see
   <a
   href="https://docs.docker.com/engine/reference/commandline/docker/"
   target="_blank">
   <i>docker (base command)</i>
   </a> in _docker docs_.

1. Check if the Kafka topics are created:

   ```
   $ docker exec kafka kafka-topics --list --zookeeper zookeeper:2181
   ```
   
   Expected output:
   
   * In case of [Base Mode Demos]:
   
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
	   
   * In case of [Feature Vector Mode Demos]:
   
       ```
       fve.cam.0.dets.ObjectDetectionRecord.json
       fve.cam.0.fvecs.FeatureVectorRecord.json
       fve.cam.0.original.Image.jpg
       fve.cam.1.dets.ObjectDetectionRecord.json
       fve.cam.1.fvecs.FeatureVectorRecord.json
       fve.cam.1.original.Image.jpg
       ```
	   
   * In case of [Skeleton Mode Demos]:
   
       ```
       skeleton.cam.0.original.Image.jpg
       skeleton.cam.0.skeletons.SkeletonRecord.json
       skeleton.cam.1.original.Image.jpg
       skeleton.cam.1.skeletons.SkeletonRecord.json
       ```
	   
1. Fetch data from a Kafka topic:

   ```
   $ docker exec kafka kafka-console-consumer --bootstrap-server kafka:9092 \
     --topic base.cam.0.dets.ObjectDetectionRecord.json
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

[Configuring Multi-Graph Runner]: conf_mgr.md#configuring-multi-graph-runner
[Configuring UVAP]: ../demo/demo_overview.md#configuring-uvap
[Base Mode Demos]: ../demo/demo_overview.md#base-mode-demos
[Feature Vector Mode Demos]: ../demo/demo_overview.md#feature-vector-mode-demos
[Skeleton Mode Demos]: ../demo/demo_overview.md#skeleton-mode-demos