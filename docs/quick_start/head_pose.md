# Head Pose Demo

![Head pose demo](../images/head-pose-demo.png)

Plays video from a jpeg topic and visualizes the head pose.  

![The yaw pitch and roll angles in the human head motion](../images/head-motion.png)

Required topics:
- `<prefix>.cam.0.lowres.Image.jpg`
- `<prefix>.cam.0.dets.ObjectDetectionRecord.json`
- `<prefix>.cam.0.poses.HeadPose3DRecord.json`

The results can be displayed with opencv-python or in browser.

## Display with opencv-python

1. Run the docker container in interactive mode (detailed description can be found [here](../quick_start_guide.md#interactiveDockerMode)):
   ```
   $ xhost +
   $ docker run -it --rm --name "python_env" \
   -v "/tmp/.X11-unix":"/tmp/.X11-unix" \
   -v "$HOME/uvap/demo_applications":"/ultinous_app" \
   -e DISPLAY=$DISPLAY \
   --net=uvap \
   --env="QT_X11_NO_MITSHM=1" \
   ultinous/uvap:uvap_demo_applications_latest /bin/bash
   ```
1. opencv-python display modes:
   1. Display output on screen:
      ```
      <DOCKER># cd /ultinous_app
      <DOCKER># /usr/bin/python3.6 apps/uvap/head_pose_DEMO.py kafka:9092 base -d
      ```
   1. Display output on full screen:
      ```
      <DOCKER># cd /ultinous_app
      <DOCKER># /usr/bin/python3.6 apps/uvap/head_pose_DEMO.py kafka:9092 base -f -d
      ```
   1. Write output to `<prefix>.cam.0.poses.HeadPose3DRecord.json`:
      ```
      <DOCKER># cd /ultinous_app
      <DOCKER># /usr/bin/python3.6 apps/uvap/head_pose_DEMO.py kafka:9092 base -o
      ```

## Web display for Kafka topic
The generally web display demo description can be found [here](../quick_start_guide.md#webDisplay).

1. Use case of the `run_demo.sh` (from the [Topic Writer Demo](../quick_start_guide.md#topicWriterDemoStarting) chapter):
   ```
   $ ~/uvap/scripts/run_demo.sh --name-of-demo head_pose --demo-mode base
   ```
   :exclamation: **Warning** :exclamation: After the first run of these scripts
    [set_retention.sh](../quick_start_guide.md#setRetention) script should be executed 
    manually because new (`*.Image.jpg`) topics are created.

1. Starting UVAP wep player (detailed description can be found [here](../quick_start_guide.md#playInTheBowser)):
   ```
   $ ~/uvap/scripts/run_web_player.sh --config-directory  "$HOME/uvap/models/uvap-web_player"
   ```

1. Display in web browser
   Use this URL to [display the demo](../quick_start_guide.md#inTheBowser):
   ```
   http://localhost:9999#base.cam.0.head_pose.Image.jpg
   ```
