---
id: demo_det_filter
title: Detection Filter Demo
hide_title: true
---

# Detection Filter

This section demonstrates the setup and usage of the [Detection Filter] feature.

The **Detection Filter** microservice filters detections based on the
confidence values of the detections and their positions. Only the detections
that have high enough confidence and fall into the specified areas are
recorded.

In the demo the detections that pass the filter are marked orange
bounding boxes, while the filtered detections are marked grey bounding boxes.

![Detection Filter Demo](../assets/demo/demo_det_filter_1.png)  

## Prerequisites

Before starting the demo, ensure the following:

* UVAP is installed as instructed in [Setting Up UVAP]
* UVAP is configured in `base` demo mode as instructed in [Configuring UVAP for Base Demo Mode]
* Web display is started as instructed in [Starting Web Player].

Required topics:

 * `base.cam.0.original.Image.jpg`
 * `base.cam.0.filtered_dets.ObjectDetectionRecord.json`
 * `base.cam.0.dets.ObjectDetectionRecord.json`

## Starting Detection Filter Demo

Start the demo with `run_demo.sh`:

```
$ "${UVAP_HOME}"/scripts/run_demo.sh \
  --demo-name detection_filter \
  --demo-mode base \
  --config-file $HOME/uvap/models/uvap-kafka-uvap_kafka_detection_filter/uvap_kafka_detection_filter.properties
  -- --net uvap
```

   >**Note:**  
   After the first run of these scripts it is recommended that `set_retention.sh script`
   is executed manually because new (`*.Image.jpg`) topics are created. For
   further information, see [Setting the Retention Period].

## Display in Web Browser

Navigate to the following URL to display the demo:
  
```
http://localhost:9999/#base.cam.0.filtered_dets.Image.jpg
```


[Detection Filter]: ../dev/start_det_filter.md
[Configuring UVAP for Base Demo Mode]: demo_config_base.md
[Setting Up UVAP]: ../install/uvap_install_setup.md#setting-up-uvap
[Starting Web Player]: demo_web_player.md#starting-web-player
[Web display]: demo_web_player.md#web-display
[Setting the Retention Period]: demo_set_ret.md#setting-the-retention-period
