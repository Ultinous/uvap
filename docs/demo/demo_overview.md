---
id: demo_overview
title: Starting Feature Demos
hide_title: true
---

# Starting Feature Demos

## Introduction

This guide gives an overview of the UVAP features and aims to teach
the user the followings:

* Start UVAP for the basic detections.
* Visualize the basic detections with Python scripts.
* Resolve a few simple use cases.

### Requirements

To start the demos, UVAP needs to be installed first. For detailed instructions
and more information, see [Installation].

### Notations

For the notations used in this document, see [Typographic Conventions].

## Starting the Analysis

### Configuring UVAP

To configure UVAP:

```
$ "${UVAP_HOME}"/scripts/config.sh --stream-uri [STREAM_URI] \
  --demo-mode [DEMO_MODE]
```

Where:

* **`[STREAM_URI]`**

  A URI referring to a valid video file or stream.  
  Replace `[STREAM_URI]` (including brackets) with one of the followings:
  
  * An IP camera, for example:
  
    ```
    rtsp://192.168.0.1/
    ```
  
    The Stream URI can also contain username and password if the stream is
    protected, for example:
  
    ```
    rtsp://username:password@192.168.0.1/
    ```

  * A USB device, for example:
  
    ```
    /dev/video0
    ```

  * A pre-recorded video
  
  Multiple streams to be analyzed may be configured by using more
  `--stream-uri [STREAM_URI]` parameter pairs, for example:

  ```
  $ "${UVAP_HOME}"/scripts/config.sh \
    --stream-uri "rtsp://192.168.0.1/" \
    --stream-uri "rtsp://username:password@192.168.0.2/" \
    --stream-uri "rtsp://192.168.0.3/" \
    --demo-mode [DEMO_MODE]
  ```
  
  The Stream URI(s) can be changed later by running this configuration
  script again.

* **`[DEMO_MODE]`**

  The demo mode.  
  Different configuration are used for base detections to save GPU resources.  
  Replace `[DEMO_MODE]` (including the brackets)
  with a string of the following set:
    
  * `base`
  * `fve`
  * `skeleton`

There are more optional parameters for the `config.sh` script to
override defaults. Use the `--help` parameter to get more details. 

### Running the Components of UVAP

For running the components of UVAP, see the instructions below:

* [Starting Multi Graph Runner]
* [Starting Tracker]
* [Starting Pass Detection]
* [Starting Reidentification]  
* [Starting Feature Vector Clustering]

### Setting the Retention Period

Kafka has a default retention period set to 168 hours. The `*.Image.jpg` topics
require a large amount of storage space because they contain all frames in
JPG image format. The retention period of JPG topics can be changed with the
`set_retention.sh` script.

 > **Attention!**  
   By default, the retention period is disabled. Without these settings, the
   `*.Image.jpg` topics use a lot of storage.

To set retention time:

```
$ "${UVAP_HOME}"/scripts/set_retention.sh --retention-unit [UNIT] \
   --retention-number [NUMBER] 
```

Where:

* **`[UNIT]`**

  A unit of time.  
  Replace `[UNIT]` (including brackets) with one of the following
  time units:
  
  * `ms` for milliseconds
  * `second` for seconds
  * `minute` for minutes
  * `hour` for hours
  * `day` for days

* **`[NUMBER]`**

  A parameter defining duration.  
  Replace `[NUMBER]` (including brackets) with a number, that
  (together with the retention unit) defines the retention time to set.

For example, to set the retention to 15 minutes:

```
$ "${UVAP_HOME}"/scripts/set_retention.sh --retention-unit minute \
  --retention-number 15
```

Expected output:

```
INFO: These topics will change:
base.cam.0.anonymized_original.Image.jpg
base.cam.0.original.Image.jpg
Completed Updating config for entity: topic 'base.cam.0.anonymized_original.Image.jpg'.
Topic:base.cam.0.anonymized_original.Image.jpg	PartitionCount:1	ReplicationFactor:1	Configs:retention.ms=900000
	Topic: base.cam.0.anonymized_original.Image.jpg	Partition: 0	Leader: 1001	Replicas: 1001	Isr: 1001
Completed Updating config for entity: topic 'base.cam.0.original.Image.jpg'.
Topic:base.cam.0.original.Image.jpg	PartitionCount:1	ReplicationFactor:1	Configs:retention.ms=900000
	Topic: base.cam.0.original.Image.jpg	Partition: 0	Leader: 1001	Replicas: 1001	Isr: 1001
```

### Reconfiguring UVAP

UVAP configuration can be modified after starting UVAP successfully. This can
come in handy if, for example, desired to switch to a different demo mode.

To modify configuration:

1. Stop and remove the running Docker containers of UVAP microservices:

   ```
   $ docker container stop $(docker container ls -a -f 'name=uvap_*' -q)
   $ docker container rm $(docker container ls -a -f 'name=uvap_*' -q)
   ```
   
1. Reconfigure UVAP with the `config.sh` script as described in
   [Configuring UVAP].
   
1. Run the UVAP microservices by starting the demo of your choice.
   See more details in the following sections.

## Demo Usage

Tree view of the demo package:

<a name="demo_tree">

```
demo_applications/
├── apps
│   └── uvap
│       ├── demography_DEMO.py
│       ├── head_detection_DEMO.py
│       ├── head_pose_DEMO.py
│       ├── list_messages.py
│       ├── list_topics.py
│       ├── pass_detection_DEMO.py
│       ├── reid_with_name_DEMO.py
│       ├── reidentification_DEMO.py
│       ├── show_image_DEMO.py
│       ├── skeleton_DEMO.py
│       └── tracker_DEMO.py
├── resources
│   ├── powered_by_black.png
│   └── powered_by_white.png
└── utils
    ├── kafka
    │   ├── kafka-cli.py
    │   └── time_ordered_generator_with_timeout.py
    ├── uvap
    │   ├── graphics.py
    │   └── uvap.py
    ├── generator_interface.py
    ├── heartbeat.py
    └── jinja_template_filler.py
```

### Environment

All dependencies are packed in a Docker image
(`ultinous/uvap:uvap_demo_applications_latest`).
Run the docker container in interactive mode:

```
$ docker run -it --rm --name "python_env" \
-v "/tmp/.X11-unix":"/tmp/.X11-unix" \
-v "${UVAP_HOME}/demo_applications":"/ultinous_app" \
-e DISPLAY=$DISPLAY \
-u $(id -u):$(id -g) \
--net=uvap \
--env="QT_X11_NO_MITSHM=1" \
ultinous/uvap:uvap_demo_applications_latest /bin/bash
```

The scripts in the `/apps/uvap` folder (see the [Tree View of the Demo Package])
can be run in the Docker container, and all of them have a help function.
For example:

```
<DOCKER># python3 apps/uvap/show_image_DEMO.py -h
```

Expected output:

```
usage: show_image_DEMO.py [-h] [-f] [-d] [-o OFFSET] broker topic

positional arguments:
  broker                The name of the kafka broker.
  topic                 The name of topic (*.Image.jpg).

optional arguments:
  -h, --help            show this help message and exit
  -f, --full_screen
  -d, --dump            if set images are stored in jpg files
  -o OFFSET, --offset OFFSET

Description:
           Plays and optionally dumps video from a jpeg topic (a topic that ends with Image.jpg).
```

### Helper Scripts

The `[DEMO_MODE]` should be `base` during the configuration.

The following Kafka data can be listed:

* [Topics]
* [Messages]

#### List Topics

To list topics from Kafka:

```
<DOCKER># python3 /ultinous_app/apps/uvap/list_topics.py kafka:9092
```

Expected output:

```
base.cam.0.ages.AgeRecord.json
base.cam.0.anonymized_original.Image.jpg
base.cam.0.dets.ObjectDetectionRecord.json
base.cam.0.frameinfo.FrameInfoRecord.json
base.cam.0.genders.GenderRecord.json
base.cam.0.original.Image.jpg
base.cam.0.poses.HeadPose3DRecord.json
base.cam.0.tracks.TrackChangeRecord.json
base.cam.0.passdet.PassDetectionRecord.json
```

#### List Messages

To list messages from a topic:

```
<DOCKER># python3 /ultinous_app/apps/uvap/list_messages.py kafka:9092 \
          [TOPIC]
```

Where `[TOPIC]` is a specified Kafka topic, for example:

```
<DOCKER># python3 /ultinous_app/apps/uvap/list_messages.py kafka:9092 \
          base.cam.0.genders.GenderRecord.json
```

Expected output:

```
1561360391236 <bound method NoKeyErrorDict.asdict of {'base': {'0': {'head_detection': {'1561360391236_0': {'gender': {'gender': 'MALE', 'confidence': 0.952010512, 'end_of_frame': False}}}}}}>
1561360391272 <bound method NoKeyErrorDict.asdict of {'base': {'0': {'head_detection': {'1561360391272_0': {'gender': {'gender': 'MALE', 'confidence': 0.941216767, 'end_of_frame': False}}}}}}>
1561360391304 <bound method NoKeyErrorDict.asdict of {'base': {'0': {'head_detection': {'1561360391304_0': {'gender': {'gender': 'MALE', 'confidence': 0.947949708, 'end_of_frame': False}}}}}}>
1561360391336 <bound method NoKeyErrorDict.asdict of {'base': {'0': {'head_detection': {'1561360391336_0': {'gender': {'gender': 'MALE', 'confidence': 0.919374943, 'end_of_frame': False}}}}}}>
```

### Web Display

There is an alternative way for demo presentation compared to Python scripts
displaying in a window. The following demos run in Docker and instead of the
display, write their results into Kafka Topics (`*[name_of_demo].Image.jpg`).
From these topics, it is possible to play image streams using the
**Web Display** application.

#### Starting the Topic Writer Demo

The following script template can be used to start the demos.

 > **Attention!**  
 Before starting this microservice, the command below silently stops and
 removes the Docker container named `uvap_demo`, if such already exists.
 <br><br>
 If this script is run in a demo mode for the first time, the demo application
 is creating a new (`*.Image.jpg`) topic in Kafka. Similarly to the other JPG
 topics, these demo-written-topics consume a lot of storage space, unless their
 retention time is decreased with the `set_retention.sh` script; for more
 information see [Setting the Retention Period].

```
$ "${UVAP_HOME}"/scripts/run_demo.sh \
  --demo-name [NAME_OF_DEMO] \
  --demo-mode [DEMO_MODE] \
  -- --net uvap
```

Where:

* **`[NAME_OF_DEMO]`**

  The demo name.  
  Replace `[NAME_OF_DEMO]` (including brackets)
  with a string from the following set:

  * `demography`
  * `head_detection`
  * `head_pose`
  * `reid_with_name`
  * `reidentification`
  * `show_image`
  * `skeleton`
  * `tracker`
  * `pass_detection`

* **`[DEMO_MODE]`**

  The demo mode.
  Replace`[DEMO_MODE]` (including brackets)
  with a string from the following set:

  * `base`
  * `skeleton`
  * `fve`

The output of the above command contains the following:

* Information about pulling the required Docker image
* The ID of the Docker container created
* The name of the Docker container created: `uvap_demo`

The available parametrization can be found in the
[`basic`], [`fve`] and [`skeleton`] demo descriptions.

There are more optional parameters for the `run_demo.sh` script to
override defaults. Use the `--help` parameter to get more details.

#### Viewing in a Browser

>**Uvap web player access from client machine (optional);**  
If you want to use the web player from a client machine (different from the processing node), 
you will have to modify the web player's default config.  
Open this config file:` ~/uvap/config/uvap_web_player/uvap_web_player.properties`    
Modify the `com.ultinous.uvap.web.player.advertised.host` parameter to the 
<HOST_MACHINE_IP> (default: localhost)  
Restart uvap_web_player if it is running     
Restart the web player with the following command:    
>```
>$ docker restart uvap_web_player  
>```  
>:exclamation: Warning :exclamation: [UVAP config](#uvapConfigSh) will override this configuration file.

1. Start the web player:

    > **Attention!**  
    Before starting this microservice, the command below silently stops and
    removes the Docker container named `uvap_web_player`, if such already exists.

    ```
    $ "${UVAP_HOME}"/scripts/run_uvap_web_player.sh -- --net uvap
    ```

    The output of the above command should be:
    * some information about pulling the required Docker image
    * the ID of the Docker container created
    * the name of the Docker container created: `uvap_web_player`

    There are more optional parameters for the `run_uvap_web_player.sh`
    script to override defaults. Use the `--help` parameter to get more
    details.

1. Test status:

    1. Checking the log of the Docker container:

        ```
        $ docker logs uvap_web_player
        ```

        Expected output example:  

        ```
        2019-07-16T10:38:12.043161Z INFO    [main]{com.ultinous.util.jmx.JmxUtil}(startConnectorServer/063) JMXConnectorServer listening on localhost:6666
        Jul 16, 2019 10:38:12 AM io.netty.handler.logging.LoggingHandler channelRegistered
        INFO: [id: 0xa3704b61] REGISTERED
        Jul 16, 2019 10:38:12 AM io.netty.handler.logging.LoggingHandler bind
       INFO: [id: 0xa3704b61] BIND: /0.0.0.0:9999
        Jul 16, 2019 10:38:12 AM io.netty.handler.logging.LoggingHandler channelActive
        INFO: [id: 0xa3704b61, L:/0:0:0:0:0:0:0:0%0:9999] ACTIVE
        2019-07-16T10:38:12.130916Z INFO    [main]{com.ultinous.uvap.web.player.MjpegPlayerServer}(start/075) Video Player listening on 0.0.0.0:9,999
        Jul 16, 2019 10:39:15 AM io.netty.handler.logging.LoggingHandler channelRead
        INFO: [id: 0xa3704b61, L:/0:0:0:0:0:0:0:0%0:9999] READ: [id: 0x9a81e318, L:/0:0:0:0:0:0:0:1%0:9999 - R:/0:0:0:0:0:0:0:1%0:59966]
        Jul 16, 2019 10:39:15 AM io.netty.handler.logging.LoggingHandler channelRead
        INFO: [id: 0xa3704b61, L:/0:0:0:0:0:0:0:0%0:9999] READ: [id: 0x56df1d95, L:/0:0:0:0:0:0:0:1%0:9999 - R:/0:0:0:0:0:0:0:1%0:59968]
        Jul 16, 2019 10:39:15 AM io.netty.handler.logging.LoggingHandler channelReadComplete
        INFO: [id: 0xa3704b61, L:/0:0:0:0:0:0:0:0%0:9999] READ COMPLETE
        ```

    1. Checking the service:

        ```
        $ wget --save-headers --content-on-error --output-document=- \
          --show-progress=no --quiet 'http://localhost:9999/' | \
          head -n1
        ```

        Expected output example:

        ```
        HTTP/1.1 200 OK
        ```

1. Navigate to the following URL in the browser:  
    
    > **Attention!**  
    This tool is intended for demo and debug purposes only.  
    It only has real time playing capability and it has no authorization or
    authentication.  
    It should only be used in a private network, because it provides a direct
    access for Kafka (`*.Image.jpg`) topics.

    ```
    http://localhost:9999#[KAFKA_IMAGE_TOPIC_NAME]
    ```

    Where `[KAFKA_IMAGE_TOPIC_NAME]` is the topic name. For more information
    on values, see [`basic`], [`fve`] or [`skeleton`] demo descriptions.

    > **Note:**  
    Refresh web display (press **F5**) after giving a new topic name.

    Full screen mode:
    
    * Activate: Click on the video to activate full screen mode.
    * Exit: Press **Esc** to exit full screen mode.

### Base Mode Demos

The `[DEMO_MODE]` should be `base` during the configuration.

Base mode demos are the following:

* [Demography]
* [Head detection]
* [Head pose]
* [Show image]
* [Tracking]
* [Pass detection]

### Feature Vector Mode Demos

The `[DEMO_MODE]` should be `fve` during the configuration.

Feature vector mode Demos are the following:

* [Single Camera Reidentification]
* [Reidentification Demo with Person Names]

### Skeleton Mode Demos

The `[DEMO_MODE]` should be `skeleton` during the configuration.

Skeleton mode demos are the following:

* [Human skeleton]


[`basic`]: #base-mode-demos
[Configuring UVAP]: #configuring-uvap
[Demography]: demo_demography.md
[`fve`]: #feature-vector-mode-demos
[Head detection]: demo_head_det.md
[Head pose]: demo_head_pose.md
[Human skeleton]: demo_skeleton.md
[Installation]: ../install/uvap_install_setup.md
[Messages]: #list-messages
[MGR Configuration]: ../dev/conf_mgr.md
[Pass detection]: demo_pass_det.md
[Reidentification Demo with Person Names]: demo_reid_with_name.md
[Single Camera Reidentification]: demo_reid_1.md
[Setting the Retention Period]: #setting-the-retention-period
[Show image]: demo_show_image.md
[`skeleton`]: #skeleton-mode-demos
[Starting Multi Graph Runner]: ../dev/start_mgr.md
[Starting Tracker]: ../dev/start_track.md
[Starting Pass Detection]: ../dev/start_passdet.md
[Starting Reidentification]: ../dev/start_reid.md  
[Starting Feature Vector Clustering]: ../dev/start_fv_clustering.md
[Topics]: #list-topics
[Tracking]: demo_track.md
[Tree View of the Demo Package]: #demo_tree
[Typographic Conventions]: ../help/uvap_notations.md
