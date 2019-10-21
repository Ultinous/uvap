---
id: demo_show_image
title: Show Image Demo
hide_title: true
---

# Anonymization

Plays video from a JPEG topic and displays it on the screen.

There are no required topics for the demo, it can use any JPEG topic as input.
Give the name of the selected topic as a parameter in the URL when the demo is
started

## Prerequisites

Before starting the demo ensure the following:

* UVAP is installed as instructed in [Setting Up UVAP]
* UVAP is configured in `base` demo mode as instructed in [Configuring UVAP for Base Demo Mode]
* The following microservices are running:
  * [Multi-Graph Runner]
* Web display is started as instructed in [Starting Web Player].

## Display in Web Browser

Navigate to the following URL to display the demo:
   
   * Original stream image:
     
	 ```
	 http://localhost:9999#base.cam.0.original.Image.jpg
	 ```
	 
   * Anonymized stream image:
   
	 ```
	 http://localhost:9999#base.cam.0.anonymized_original.Image.jpg
	 ```

[Configuring UVAP for Base Demo Mode]: demo_config_base.md#configuring-uvap-for-base-demo-mode
[Multi-Graph Runner]: ../dev/start_mgr.md#starting-multi-graph-runner
[Setting the Retention Period]: demo_set_ret.md#setting-the-retention-period
[Setting Up UVAP]: ../install/uvap_install_setup.md#setting-up-uvap
[Starting Web Player]: demo_web_player.md#starting-web-player
