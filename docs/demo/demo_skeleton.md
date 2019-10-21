---
id: demo_skeleton
title: Human Skeleton Demo
hide_title: true
---

# Human Skeleton Demo

This section demonstrates the setup and usage of the [Skeleton Detection] feature.

The demo plays a video from a JPEG topic and draws the main points of a human
skeleton linked with colored lines:

![Skeleton demo](../assets/feat_img/skeleton.png)

## Prerequisites

Before starting the demo ensure the following:

* UVAP is installed as instructed in [Setting Up UVAP]
* UVAP is configured in `skeleton` demo mode as instructed in [Configuring UVAP for Skeleton Demo Mode]
* The following microservices are running:
  * [Multi-Graph Runner]
* Web display is started as instructed in [Starting Web Player].

Required topics:

* `skeleton.cam.0.orginal.Image.jpg`
* `skeleton.cam.0.skeletons.SkeletonRecord.json`

## Start Human Skeleton Demo
   
Start the demo with `run_demo.sh`:

   ```
   $ "${UVAP_HOME}"/scripts/run_demo.sh --demo-name skeleton \
     --demo-mode skeleton -- --net uvap
   ```
   
   >**Note:**  
   After the first run of these scripts, execute `set_retention.sh` script
   manually because new (`*.Image.jpg`) topics are created. For
   further information, see [Setting the Retention Period].
   
## Display in Web Browser

Navigate to the following URL to display the demo:

   ```
   http://localhost:9999#skeleton.cam.0.skeleton.Image.jpg
   ```

[Configuring UVAP for Skeleton Demo Mode]: demo_config_skeleton.md#configuring-uvap-for-skeleton-demo-mode
[Multi-Graph Runner]: ../dev/start_mgr.md#starting-multi-graph-runner
[Setting the Retention Period]: demo_set_ret.md#setting-the-retention-period
[Setting Up UVAP]: ../install/uvap_install_setup.md#setting-up-uvap
[Starting Web Player]: demo_web_player.md#starting-web-player
[Skeleton Detection]: ../feat/detect_person/feat_skeleton.md#skeleton-detection
