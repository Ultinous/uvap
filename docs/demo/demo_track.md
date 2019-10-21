---
id: demo_track
title: Tracking Demo
hide_title: true
---

# Tracking Demo

This section demonstrates the setup and usage of the [Tracking] feature.

The demo plays video from a JPEG topic, and visualizes the tracks of detected individuals:

![Tracking](../assets/feat_img/track.png)

## Prerequisites

Before starting the demo ensure the following:

* UVAP is installed as instructed in [Setting Up UVAP]
* UVAP is configured in `base` demo mode as instructed in [Configuring UVAP for Base Demo Mode]
* The following microservices are running:
  * [Multi-Graph Runner]
  * [Tracker]
* Web display is started as instructed in [Starting Web Player].

Required topics:

* `base.cam.0.original.Image.jpg`
* `base.cam.0.dets.ObjectDetectionRecord.json`
* `base.cam.0.tracks.TrackChangeRecord.json`

## Start Tracking Demo

Start the demo with `run_demo.sh`:
   
   ```
   $ "${UVAP_HOME}"/scripts/run_demo.sh --demo-name tracker \
     --demo-mode base -- --net uvap
   ```
   
   >**Note:**  
   After the first run of these scripts it is recommended that `set_retention.sh script`
   is executed manually because new (`*.Image.jpg`) topics are created. For
   further information, see [Setting the Retention Period].

## Display in Web Browser

Navigate to the following URL to display the demo:
  
   ```
   http://localhost:9999#base.cam.0.tracker.Image.jpg
   ```

[Configuring UVAP for Base Demo Mode]: demo_config_base.md#configuring-uvap-for-base-demo-mode
[Multi-Graph Runner]: ../dev/start_mgr.md#starting-multi-graph-runner
[Setting the Retention Period]: demo_set_ret.md#setting-the-retention-period
[Setting Up UVAP]: ../install/uvap_install_setup.md#setting-up-uvap
[Starting Web Player]: demo_web_player.md#starting-web-player
[Tracker]: ../dev/start_track.md#starting-tracker
[Tracking]: ../feat/detect_movement/feat_track.md#people-tracking
