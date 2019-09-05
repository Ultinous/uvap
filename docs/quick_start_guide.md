# UVAP Quick Start Guide
## Table of contents
1. [Introduction](#introduction)
1. [Starting the Analysis](#startAnalysis)
   1. [Configuring UVAP](#configUVAP)
   1. [How to run the components of UVAP](#startUVAP)
   1. [Setting the Retention Period](#setRetention)
   1. [Reconfiguring UVAP](#reConfigUVAP)
1. [Demo usage](#demoUsage)
   1. [Environment](#environment)
   1. [Helper Scripts](#helperScripts)
   1. [Web Display](#webDisplay)
      1. [Starting the Topic Writer Demo](#topicWriterDemoStarting)
      1. [Viewing in a Browser](#playInTheBrowser)
   1. [Demos (Base Mode)](#basicDemos)
   1. [Demos (Feature Vector Mode)](#fveDemos)
   1. [Demos (Skeleton Mode)](#skeletonDemos)
1. [Use Cases for Practising](#useCases)

<a name="introduction"></a>
## Introduction
#### Goals
After this section:
- You will be able to start UVAP for the basic detections
- You will be able to visualize the basic detections with python scripts
- You will be able to resolve a few simple use cases

#### Requirements
You completed the [Installation Guide](installation_guide.md).

#### Notations
For the notations used in this document, see [Notations](notations.md).

<a name="startAnalysis"></a>
## Starting the Analysis

<a name="configUVAP"></a>
### Configuring UVAP

In order to configure UVAP, the following script template needs to be edited as described below,
and then executed:
<a name="uvapConfigSh"></a>
```
$ "${UVAP_HOME}"/scripts/config.sh --stream-uri [STREAM_URI] \
  --demo-mode [DEMO_MODE] --keep-rate-number [KEEP_RATE]
```

The `[STREAM_URI]` (including square brackets) should be replaced with a
URI which refers to a valid video file or stream, for example an IP
camera.
This should look like this: `rtsp://192.168.0.1/`. This URI
can also contain username and password if the stream is protected, e.g.
`rtsp://username:password@192.168.0.1/`.
The URI can also be the device name of a camera plugged into a USB port,
e.g. `/dev/video0`, or simply a filename of a pre-recorded video.
The stream URI(s) can be changed later by running this configurator
script again.

<a name="multipleInput"></a>
Multiple streams to be analyzed may be configured by using more
`--stream-uri [STREAM_URI]` parameter pairs, for example:
```
$ "${UVAP_HOME}"/scripts/config.sh \
  --stream-uri "rtsp://192.168.0.1/" \
  --stream-uri "rtsp://username:password@192.168.0.2/" \
  --stream-uri "rtsp://192.168.0.3/" \
  --demo-mode [DEMO_MODE] --keep-rate-number [KEEP_RATE]
```

We use different configuration for base detections to save GPU resources.
The `[DEMO_MODE]` (including the square brackets) should be replaced with
a string. Valid values of `[DEMO_MODE]` are `base`, `skeleton` or `fve`.

<a name="baseMode"></a>
The `base` demos:
- Demography
- Head detection
- Head pose
- Show image
- Tracker
- Pass detection

<a name="fveMode"></a>
The `fve` demo(s):
- Basic reidentification

<a name="skeletonMode"></a>
The `skeleton` demo(s):
- Human skeleton

The `[KEEP_RATE]` is an optional parameter for changing the frequency of
analysis on frames. By default, UVAP uses all frames for the analysis.
If you set the `[KEEP_RATE]` to e.g. `3`, UVAP
will use every 3rd frame for analysis, so it will be faster.
Replace `[KEEP_RATE]` (including square
brackets) with the desired keep rate.

There are more optional parameters for the `config.sh` script to
override defaults. Use the `--help` parameter to get more details.

<a name="startUVAP"></a>
### How to run the components of UVAP  
#### [Multi Graph Runner (MGR) microservice](quick_start/mgr_microservice.md)
#### [Kafka Tracker microservice](quick_start/kafka_tracker_microservice.md)
#### [Kafka Pass Detection microservice](quick_start/kafka_pass_detection_microservice.md)
#### [Basic Reidentification microservice](quick_start/basic_reidentification_microservice.md)

<a name="setRetention"></a>
### Setting the Retention Period

Kafka has a default retention period set to 168 hours. The `*.Image.jpg`
topics will require a large amount of storage space
because they contain all frames in JPG image format.
We can change the lifetime of JPG topics with the `set_retention.sh`
script.

Usage:
```
$ "${UVAP_HOME}"/scripts/set_retention.sh --retention-unit [UNIT] \
  --retention-number [NUMBER]
```
The `[UNIT]` (including the square brackets) should be replaced with one
of the following time units: `ms`, `second`, `minute`, `hour` and `day`.
The `[NUMBER]` (including the square brackets) should be replaced with
a number, that (together with the retention unit) defines the retention
time to set.

For example, to set the retention time to 15 minutes:
```
$ "${UVAP_HOME}"/scripts/set_retention.sh --retention-unit minute \
  --retention-number 15
```
:exclamation: **Warning** :exclamation: Without these settings the
`*.Image.jpg` topics will use a lot of storage space!

You can see something like this:
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
<a name="reConfigUVAP"></a>
### Reconfiguring UVAP
If UVAP has already been successfully started, but you want to modify
the configuration of it (e.g. switch to a different demo mode), the
easiest way to do it is:
1. Stop and remove the running Docker containers of UVAP microservices
   ```
   $ docker container stop $(docker container ls -a -f 'name=uvap_*' -q)
   $ docker container rm $(docker container ls -a -f 'name=uvap_*' -q)
   ```
1. Reconfigure UVAP with the `config.sh` script (see details:
   [Configuring UVAP](#uvapConfigSh))
1. Run the UVAP microservices by starting the demo of your choice. See
   more details in the following sections.
<a name="demoUsage"></a>
## Demo Usage
Tree view of demo package:
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
│       ├── basic_reidentification_DEMO.py
│       ├── show_image_DEMO.py
│       ├── skeleton_DEMO.py
│       └── tracker_DEMO.py
├── resources
│   ├── powered_by_black.png
│   └── powered_by_white.png
└── utils
    ├── kafka
    │   └── time_ordered_generator_with_timeout.py
    ├── uvap
    │   ├── graphics.py
    │   └── uvap.py
    ├── generator_interface.py
    ├── heartbeat.py
    └── jinja_template_filler.py
```

<a name="environment"></a>
### Environment
<a name="interactiveDockerMode"></a>  
All dependencies are packed in a Docker image
(`ultinous/uvap:uvap_demo_applications_latest`).
Run the Docker container in interactive mode:
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
The following scripts can be run in the Docker container.
All scripts in `/apps/uvap` directory have help function. For example:

```
<DOCKER># /usr/bin/python3.6 apps/uvap/show_image_DEMO.py -h
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
           Plays and optionaly dumps video from a jpeg topic (a topic that ends with Image.jpg).

```

<a name="helperScripts"></a>
### Helper Scripts
The `[DEMO_MODE]` should be 'base' during the [configuration](#configUVAP).
Data in Kafka can be checked with the following scripts:
#### List topics
List topics from Kafka.
```
<DOCKER># /usr/bin/python3.6 /ultinous_app/apps/uvap/list_topics.py kafka:9092
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

#### List messages
List messages from a topic, e.g.:
```
<DOCKER># /usr/bin/python3.6 /ultinous_app/apps/uvap/list_messages.py kafka:9092 base.cam.0.genders.GenderRecord.json
```
Expected output:
```
1561360391236 <bound method NoKeyErrorDict.asdict of {'base': {'0': {'head_detection': {'1561360391236_0': {'gender': {'gender': 'MALE', 'confidence': 0.952010512, 'end_of_frame': False}}}}}}>
1561360391272 <bound method NoKeyErrorDict.asdict of {'base': {'0': {'head_detection': {'1561360391272_0': {'gender': {'gender': 'MALE', 'confidence': 0.941216767, 'end_of_frame': False}}}}}}>
1561360391304 <bound method NoKeyErrorDict.asdict of {'base': {'0': {'head_detection': {'1561360391304_0': {'gender': {'gender': 'MALE', 'confidence': 0.947949708, 'end_of_frame': False}}}}}}>
1561360391336 <bound method NoKeyErrorDict.asdict of {'base': {'0': {'head_detection': {'1561360391336_0': {'gender': {'gender': 'MALE', 'confidence': 0.919374943, 'end_of_frame': False}}}}}}>
```

<a name="webDisplay"></a>
### Web Display
There is an alternative way for demo presentation compared to python scripts
displaying in a window. The following demos run in Docker and write
their results into Kafka topics (`*[name_of_demo].Image.jpg`) instead of
the display. From these topics, it is possible to play image streams using the **web display** application.

<a name="topicWriterDemoStarting"></a>
#### Starting the Topic Writer Demo
The following script template can be used to start the demos. `[NAME_OF_DEMO]` (including the square brackets)
should be replaced with a string from this set
{`demography`, `head_detection`, `head_pose`, `basic_reidentification`, `show_image`, `skeleton`, `tracker`, `pass_detection`}.   
As earlier, `[DEMO_MODE]` (including the square brackets) should be replaced
with a string from this set {`base`, `skeleton`, `fve`}.  
```
$ "${UVAP_HOME}"/scripts/run_demo.sh \
  --demo-name [NAME_OF_DEMO] \
  --demo-mode [DEMO_MODE] \
  -- --net uvap
```
The output of the above command should be:
* some information about pulling the required Docker image
* the ID of the Docker container created
* the name of the Docker container created: `uvap_demo`

:exclamation: Warning :exclamation: before starting this
microservice, the above command will silently stop and remove the
Docker container named `uvap_demo`, if such already exists.

:exclamation: **Warning** :exclamation: Each time this script is run in
a demo mode, that wasn't in use before, the demo application is creating
a new (`*.Image.jpg`) topic in Kafka. Similarly to the other JPG topics,
these demo-writed-topics will consume a lot of storage space, unless the
retention time of them is decreased with the
[set_retention.sh](#setRetention) script.

The available parametrization can be found in the [basic](#basicDemos), [fve](#fveDemos) or [skeleton](#skeletonDemos) demo descriptions.

There are more optional parameters for the `run_demo.sh` script to
override defaults. Use the `--help` parameter to get more details.

<a name="playInTheBrowser"></a>
#### Viewing in a Browser

1. Starting
    ```
    $ "${UVAP_HOME}"/scripts/run_web_player.sh -- --net uvap
    ```
    The output of the above command should be:
    * some information about pulling the required Docker image
    * the ID of the Docker container created
    * the name of the Docker container created: `uvap_web_player`

    :exclamation: Warning :exclamation: before starting this
    microservice, the above command will silently stop and remove the
    Docker container named `uvap_web_player`, if such already exists.

    There are more optional parameters for the `run_web_player.sh`
    script to override defaults. Use the `--help` parameter to get more
    details.
1. Testing (optional)  
    a.) checking the log of the Docker container
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

    b.) checking service
    ```
    $ wget --save-headers --content-on-error --output-document=- \
      --show-progress=no --quiet 'http://localhost:9999/' | head -n1
    ```
    You should see the following output:
    ```
    HTTP/1.1 200 OK
    ```
    <a name="inTheBrowser"></a>
1. In the browser  
    On browser use following URL template:
    ```
    http://localhost:9999#[KAFKA_IMAGE_TOPIC_NAME]
    ```
    The available `[KAFKA_IMAGE_TOPIC_NAME]` values can be found in the [basic](#basicDemos), [fve](#fveDemos) or [skeleton](#skeletonDemos) demo descriptions.

    Web display required a refresh (press 'F5' button) after it got a new topic name!

    Full screen mode:
    - Activate: Click on the video to activate the full screen mode.
    - Exit: Press 'Esc' button to exit the full screen mode.

    :exclamation: **Warning** :exclamation:  
    **This tool is for demo/debug purposes only!**
    It only has real time playing capability and it has no authorization or authentication.  
    It should only be used in a private network, because it provides a direct access for Kafka (`*.Image.jpg`) topics.   

<a name="basicDemos"></a>
### Demos (Base Mode)
The `[DEMO_MODE]` should be 'base' during the [configuration](#configUVAP).

#### [Viewing Images](quick_start/show_image.md)
#### [Head Detection](quick_start/head_detection.md)
#### [Head Pose](quick_start/head_pose.md)
#### [Demography](quick_start/demography.md)
#### [Tracking](quick_start/tracking.md)
#### [Pass Detection](quick_start/pass_detection.md)


<a name="fveDemos"></a>
### Demos (Feature Vector Mode)
The `[DEMO_MODE]` should be 'fve' during the [configuration](#configUVAP).

#### [Basic Reidentification](quick_start/basic_reidentification.md)

<a name="skeletonDemos"></a>
### Demos (Skeleton Mode)
The `[DEMO_MODE]` should be 'skeleton' during the [configuration](#configUVAP).

#### [Human Skeleton](quick_start/human_skeleton.md)

<a name="useCases"></a>
## Use Cases for Practising
### Alerting system
Task:  

Create a demo with people counting in area. If there are more than 1 person
in the area, give a visualized alert.

Details:

- Modify an existing demo script.
- The resolution of your camera is 1920x1080.
- The area is a rectangle, coordinates of top left corner: (200,200) and
the bottom right corner: (1200, 900). Draw it on the screen with a white line.
- For the alert visualization use an 'Alert' image (`/image/alert.png`) and
change the rectangle color to red.

### See the s(h)elf
Task:  

Create a demo with people counting who seeing a shelf exactly in front of
the camera.

Details:  

- Modify an existing demo script.
- The resolution of your camera is 1920x1080.
- For the visualization write a number (how many were in the order) above the head of the person.

### High five
Task:  

Create a demo with detecting and visualizing the valid high fives on the screen.

Details:

- Modify an existing demo script.
- The resolution of your camera is 1920x1080.
- Valid high fives: 2 right hands, located above the shoulders
- For the visualization create a border of the screen and change the color of it.
