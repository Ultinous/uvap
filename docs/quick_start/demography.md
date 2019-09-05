# Demography Demo

Plays video from a jpeg topic and visualizes the head detection with an orange bounding box around a
head and renders demography (gender & age) data above the head.

Required topics:
- `base.cam.0.original.Image.jpg`
- `base.cam.0.dets.ObjectDetectionRecord.json`
- `base.cam.0.genders.GenderRecord.json`
- `base.cam.0.ages.AgeRecord.json`

The results can be displayed with opencv-python or in browser.

## Display with opencv-python

1. Run the Docker container in interactive mode (detailed description can be found [here](../quick_start_guide.md#interactiveDockerMode)):
   ```
   $ xhost +
   $ docker run -it --rm --name "python_env" \
   -v "/tmp/.X11-unix":"/tmp/.X11-unix" \
   -v "${UVAP_HOME}/demo_applications":"/ultinous_app" \
   -e DISPLAY=$DISPLAY \
   --net=uvap \
   --env="QT_X11_NO_MITSHM=1" \
   ultinous/uvap:uvap_demo_applications_latest /bin/bash
   ```
1. opencv-python display modes:
   1. Display output on screen:
      ```
      <DOCKER># cd /ultinous_app
      <DOCKER># /usr/bin/python3.6 apps/uvap/demography_DEMO.py kafka:9092 base -d
      ```
   1. Display output on full screen:
      ```
      <DOCKER># cd /ultinous_app
      <DOCKER># /usr/bin/python3.6 apps/uvap/demography_DEMO.py kafka:9092 base -f -d
      ```
   1. Write output to `base.cam.0.demography.Image.jpg`:
      ```
      <DOCKER># cd /ultinous_app
      <DOCKER># /usr/bin/python3.6 apps/uvap/demography_DEMO.py kafka:9092 base -o
      ```

## Web display for Kafka topic
The generally web display demo description can be found [here](../quick_start_guide.md#webDisplay).

1. Use case of the `run_demo.sh` (from the [Topic Writer Demo](../quick_start_guide.md#topicWriterDemoStarting) chapter):
   ```
   $ "${UVAP_HOME}"/scripts/run_demo.sh --demo-name demography \
     --demo-mode base -- --net uvap
   ```
   :exclamation: **Warning** :exclamation: After the first run of these scripts
    [set_retention.sh](../quick_start_guide.md#setRetention) script should be executed
    manually because new (`*.Image.jpg`) topics are created.

1. Starting UVAP wep player (detailed description can be found [here](../quick_start_guide.md#playInTheBowser)):
   ```
   $ "${UVAP_HOME}"/scripts/run_web_player.sh -- --net uvap
   ```

1. Display in web browser
   Use this URL to [display the demo](../quick_start_guide.md#inTheBowser):
   ```
   http://localhost:9999#base.cam.0.demography.Image.jpg
   ```
