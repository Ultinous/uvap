---
id: demo_pass_det
title: Pass Detection Demo
hide_title: true
---

#  Pass Detection Demo

This section demonstrates the setup and usage of the [Pass Detection] feature.

The demo plays video from a JPEG topic, and visualizes the
tracks of detected individuals, predefined polylines (passlines), and shows if
any track intersects a passline:

![Pass detection](../assets/feat_img/pass_det.png)

## Prerequisites

Before starting the demo ensure the following:

* UVAP is installed as instructed in [Setting Up UVAP]
* UVAP is configured in `base` demo mode as instructed in [Configuring UVAP for Base Demo Mode]
* The following microservices are running:
  * [Multi-Graph Runner]
  * [Tracker]
  * [Pass Detector]
* Web display is started as instructed in [Starting Web Player].

Required topics:

* `<prefix>.cam.0.lowres.Image.jpg`
* `<prefix>.cam.0.dets.ObjectDetectionRecord.json`
* `<prefix>.cam.0.tracks.TrackChangeRecord.json`
* `<prefix>.cam.0.passdet.PassDetectionRecord.json`

## Start Pass Detection Demo
   
Start the demo with `run_demo.sh`:
   
   ```
   $ ~/uvap/scripts/run_demo.sh --name-of-demo pass_detection --demo-mode base \
     --config-file $HOME/uvap/models/uvap-kafka-passdet/uvap_kafka_passdet.properties
   ```
   
   >**Note:**  
   After the first run of these scripts, execute `set_retention.sh` script
   manually because new (`*.Image.jpg`) topics are created. For
   further information, see [Setting the Retention Period].

## Display in Web Browser

Navigate to the following URL to display the demo:
  
   ```
   http://localhost:9999#base.cam.0.passdet.Image.jpg
   ```

[Configuring UVAP for Base Demo Mode]: demo_config_base.md#configuring-uvap-for-base-demo-mode
[Multi-Graph Runner]: ../dev/start_mgr.md#starting-multi-graph-runner
[Pass Detection]: ../feat/detect_movement/feat_pass_det.md#pass-detection
[Pass Detector]: ../dev/start_passdet.md#starting-pass-detector
[Setting the Retention Period]: demo_set_ret.md#setting-the-retention-period
[Setting Up UVAP]: ../install/uvap_install_setup.md#setting-up-uvap
[Starting Web Player]: demo_web_player.md#starting-web-player
[Tracker]: ../dev/start_track.md