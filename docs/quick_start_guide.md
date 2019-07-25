# UVAP Quick Start Guide
## Table of contents
1. [Introduction](#introduction)
1. [Starting the Analysis](#startAnalysis)
   1. [Configuring UVAP](#configUVAP)
   1. [How to run the components of UVAP](#startUVAP)
      1. [Multi Graph Runner (MGR) microservice starting](#startMGR)
      1. [Tracker microservice starting](#startTracker)
   1. [Setting the Retention Period](#setRetention)
1. [Demo usage](#demoUsage)
   1. [Environment](#environment)
   1. [Helper Scripts](#helperScripts)
   1. [Demos (Base Mode)](#basicDemos)
      1. [Viewing Images](#showImages)
      1. [Head Detection](#headDetection)
      1. [Head Pose](#headPose)
      1. [Demography](#demography)
      1. [Tracking](#tracking)
   1. [Demos (Skeleton Mode)](#advancedDemos)
      1. [Human Body Pose (Skeleton)](#humanSkeleton)
1. [Web Display](#webDisplay)
   1. [Starting the Topic Writer Demo](#topicWriterDemoStarting)
   1. [Viewing in a Browser](#playInTheBowser)
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
```
$ ~/uvap/scripts/config.sh --models-directory "$HOME/uvap/models" --stream-url [RTSP_URL] \
  --demo-mode [DEMO_MODE] --keep-rate [KEEP_RATE]
```

The `[RTSP_URL]` (including square brackets) should be replaced with a URL
which refers to a valid RTSP stream, for example an IP camera.
This should look like this: `rtsp://192.168.0.1/`. This URL
can also contain username and password if the stream is protected, e.g. `rtsp://username:password@192.168.0.1/`.
The stream url can be changed later by running this install script again.

We use different configuration for base detections to save GPU resources.
The `[DEMO_MODE]` (including the square brackets) should be replaced with
a string. Valid values of `[DEMO_MODE]` are `base` or `skeleton`.

The 'base' demos:
- Show image
- Head detection
- Head pose
- Demography
- Tracking

The 'skeleton' demo(s):
- Human skeleton

The `[KEEP_RATE]` is an optional parameter for changing the frequency of
analysis on frames. By default, UVAP uses all frames for the analysis.
If you set the `[KEEP_RATE]` to e.g. `3`, UVAP
will use every 3rd frame for analysis, so it will be faster.
Replace `[KEEP_RATE]` (including square
brackets) with the desired keep rate.

<a name="startUVAP"></a>
### How to run the components of UVAP  
<a name="startMGR"></a>
#### Multi Graph Runner (MGR) microservice starting

The following steps should be followed to start head detection on the frames of the previously confiugred video stream.

1. Run framework  
    As a first step, you have to start up the framework:
    ```
    $ ~/uvap/scripts/run_mgr.sh --models-directory "$HOME/uvap/models" \
      --license-data-file-path "$(readlink -f ~/uvap/license/license.txt)" \
      --license-key-file-path "$(readlink -f ~/uvap/license/license.key)" -- --net=uvap
    ```
1. Check if the container (named `uvap_mgr`) is running:
    ```
    $ docker container inspect --format '{{.State.Status}}' uvap_mgr
    ```
    Expected output:
    ```
    running
    ```
1. Report problem  
    If the status of uvap container is not running then send the output of the following command to `support@ultinous.com`.
    ```
    $ docker logs uvap_mgr
    ```
    These docker containers can be managed with standard docker commands. [Learn more...](https://docs.docker.com/engine/reference/commandline/docker/)

1. Check if the kafka topics are created:
    ```
    $ docker exec -it kafka /bin/bash -c 'kafka-topics --list --zookeeper zookeeper:2181'
    ```
1. Try to fetch data from a kafka topic:
    ```
    $ kafkacat -b kafka -t base.cam.0.dets.ObjectDetectionRecord.json
    ```

<a name="startTracker"></a>
#### Tracker microservice starting

Reads head detections from a json topic, and creates tracks of the detected persons.
It assumes MGR is running, as it needs object detection records as input.

Required input topic: `<prefix>.cam.0.dets.ObjectDetectionRecord.json`  
Created output topic: `<prefix>.cam.0.tracks.TrackChangeRecord.json`

1. Run framework:
   ```bash
   $ ~/uvap/scripts/run_kafka_tracker.sh --config-directory "$HOME/uvap/models/uvap-kafka-tracker" -- --net=uvap
   ```

1. Wait for ~30 seconds, then check if the containers are still running:
   ```bash
   $ docker container inspect --format '{{.State.Status}}' uvap_kafka_tracker
   ```
   Expected output:
   ```
   running
   ```
1. Output checking:
   ```bash
   $ kafkacat -b kafka -t base.cam.0.tracks.TrackChangeRecord.json
   ```
   Expected output:
   ```
   {"end_of_track":false,"detection_key":"1563262804472_0","point":{"x":598,"y":150}}
   {"end_of_track":false,"detection_key":"1563262804472_2","point":{"x":804,"y":249}}
   {"end_of_track":true,"detection_key":""}
   % Reached end of topic base.tracks.TrackChangeRecord.json [0] at offset 4916
   {"end_of_track":false,"detection_key":"1563262804847_0","point":{"x":598,"y":150}}
   {"end_of_track":false,"detection_key":"1563262804847_2","point":{"x":804,"y":249}}
   {"end_of_track":false,"detection_key":"1563262804847_1","point":{"x":1077,"y":353}}
   ```

<a name="setRetention"></a>
### Setting the Retention Period

Kafka has a default retention period set to 168 hours. The `*.Image.jpg`
topics will require a large amount of storage space
because they contain all frames in JPG image format.
We can change the lifetime of topics with the `set_retention.sh` script.  

Usage:
```
$  ~/uvap/scripts/set_retention.sh
usage: ./set_retention.sh (--retention-ms|--retention-minute|--retention-second|--retention-hour|--retention-day) number
```
For example, set the retention to 15 minutes:
```
$  ~/uvap/scripts/set_retention.sh --retention-minute 15
```
:exclamation: **Warning** :exclamation: Without these settings the
`*.Image.jpg` topics use a lot of storage space!

You can see something like this:
```
These topics will change:
base.cam.0.anonymized_lowres.Image.jpg
base.cam.0.lowres.Image.jpg
Completed Updating config for entity: topic 'base.cam.0.anonymized_lowres.Image.jpg'.
Topic:base.cam.0.anonymized_lowres.Image.jpg	PartitionCount:1	ReplicationFactor:1	Configs:retention.ms=900000
	Topic: base.cam.0.anonymized_lowres.Image.jpg	Partition: 0	Leader: 1001	Replicas: 1001	Isr: 1001
Completed Updating config for entity: topic 'base.cam.0.lowres.Image.jpg'.
Topic:base.cam.0.lowres.Image.jpg	PartitionCount:1	ReplicationFactor:1	Configs:retention.ms=900000
	Topic: base.cam.0.lowres.Image.jpg	Partition: 0	Leader: 1001	Replicas: 1001	Isr: 1001

```
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
│       ├── show_image_DEMO.py
│       ├── skeleton_DEMO.py
│       └── tracker_DEMO.py
├── resources
│   ├── powered_by_black.png
│   └── powered_by_white.png
└── utils
    ├── kafka
    │   └── time_ordered_generator_with_timeout.py
    └── uvap
        ├── graphics.py
        └── uvap.py
```

<a name="environment"></a>
### Environment
All dependencies are packed in a docker image. (ultinous/uvap:uvap_demo_applications_latest)  
Run the docker container in interactive mode:
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
The following scripts can be run in the docker image.
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
base.cam.0.lowres.Image.jpg
base.cam.0.ages.AgeRecord.json
base.cam.0.poses.HeadPose3DRecord.json
base.cam.0.ages.GenderRecord.json
base.cam.0.dets.ObjectDetectionRecord.json
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

<a name="basicDemos"></a>
### Demos (Base Mode)
The `[DEMO_MODE]` should be 'base' during the [configuration](#configUVAP).

<a name="showImages"></a>
#### Viewing Images
1.) Original images (images of the RTSP stream are stored in Kafka)
```
<DOCKER># /usr/bin/python3.6 /ultinous_app/apps/uvap/show_image_DEMO.py kafka:9092 base.cam.0.lowres.Image.jpg
```

2.) Original images in full screen
```
<DOCKER># /usr/bin/python3.6 /ultinous_app/apps/uvap/show_image_DEMO.py kafka:9092 base.cam.0.lowres.Image.jpg -f
```

3.) Anonymized images (created by UVAP)
```
<DOCKER># /usr/bin/python3.6 /ultinous_app/apps/uvap/show_image_DEMO.py kafka:9092 base.cam.0.anonymized_lowres.Image.jpg
```

<a name="headDetection"></a>
#### Head Detection

![Head detection demo](images/head-det-demo.png)

Plays video from a jpeg topic and visualizes the head detection.

Required topics:
- `<prefix>.cam.0.lowres.Image.jpg`
- `<prefix>.cam.0.dets.ObjectDetectionRecord.json`

```
<DOCKER># cd /ultinous_app

# display output on screen
<DOCKER># /usr/bin/python3.6 apps/uvap/head_detection_DEMO.py kafka:9092 base -d

# display output on full screen
<DOCKER># /usr/bin/python3.6 apps/uvap/head_detection_DEMO.py kafka:9092 base -f -d

# write output to <prefix>.cam.0.head_detection.Image.jpg
<DOCKER># /usr/bin/python3.6 apps/uvap/head_detection_DEMO.py kafka:9092 base -o
```

<a name="headPose"></a>
#### Head Pose

![Head pose demo](images/head-pose-demo.png)

Plays video from a jpeg topic and visualizes the head pose.  

Required topics:
- `<prefix>.cam.0.lowres.Image.jpg`
- `<prefix>.cam.0.dets.ObjectDetectionRecord.json`
- `<prefix>.cam.0.poses.HeadPose3DRecord.json`

![The yaw pitch and roll angles in the human head motion](images/head-motion.png)
```
<DOCKER># cd /ultinous_app

# display output on screen
<DOCKER># /usr/bin/python3.6 apps/uvap/head_pose_DEMO.py kafka:9092 base -d

# display output on full screen
<DOCKER># /usr/bin/python3.6 apps/uvap/head_pose_DEMO.py kafka:9092 base -f -d

# write output to <prefix>.cam.0.poses.HeadPose3DRecord.json
<DOCKER># /usr/bin/python3.6 apps/uvap/head_pose_DEMO.py kafka:9092 base -o
```

<a name="demography"></a>
#### Demography
Plays video from a jpeg topic and visualizes the head detection with an orange bounding box around a
head and renders demography (gender & age) data above the head. Required topics:
- `<prefix>.cam.0.lowres.Image.jpg`
- `<prefix>.cam.0.dets.ObjectDetectionRecord.json`
- `<prefix>.cam.0.genders.GenderRecord.json`
- `<prefix>.cam.0.ages.AgeRecord.json`

```
<DOCKER># cd /ultinous_app

# display output on screen
<DOCKER># /usr/bin/python3.6 apps/uvap/demography_DEMO.py kafka:9092 base -d

# display output on full screen
<DOCKER># /usr/bin/python3.6 apps/uvap/demography_DEMO.py kafka:9092 base -f -d

# write output to <prefix>.cam.0.demography.Image.jpg
<DOCKER># /usr/bin/python3.6 apps/uvap/demography_DEMO.py kafka:9092 base -o

```

<a name="tracking"></a>
#### Tracking

![Tracking demo](images/tracking-demo.png)

Plays video from a jpeg topic, and visualizes the tracks of detected individuals.

Required topic:
- `<prefix>.cam.0.lowres.Image.jpg`
- `<prefix>.cam.0.dets.ObjectDetectionRecord.json`
- `<prefix>.cam.0.tracks.TrackChangeRecord.json`

```
<DOCKER># cd /ultinous_app

# display output on screen
<DOCKER># /usr/bin/python3.6 apps/uvap/tracker_DEMO.py kafka:9092 base -d

# display output on full screen
<DOCKER># /usr/bin/python3.6 apps/uvap/tracker_DEMO.py kafka:9092 base -f -d

# write output to <prefix>.cam.0.tracks.Image.jpg
<DOCKER># /usr/bin/python3.6 apps/uvap/tracker_DEMO.py kafka:9092 base -o

```

<a name="advancedDemos"></a>
### Demos (Skeleton Mode)
The `[DEMO_MODE]` should be 'skeleton' during the [configuration](#configUVAP).

<a name="humanSkeleton"></a>
#### Human skeleton

![Skeleton demo](images/skeleton-demo.png)

Plays video from a jpeg topic and draws the main points of a human skeleton
linked with colorful lines.  

Required topics:
- `<prefix>.cam.0.lowres.Image.jpg`
- `<prefix>.cam.0.skeletons.SkeletonRecord.json`

```
<DOCKER># cd /ultinous_app

# display output on screen
<DOCKER># /usr/bin/python3.6 apps/uvap/skeleton_DEMO.py kafka:9092 skeleton -d

# display output on full screen
<DOCKER># /usr/bin/python3.6 apps/uvap/skeleton_DEMO.py kafka:9092 skeleton -f -d

# write output to <prefix>.cam.0.head_detection.Image.jpg
<DOCKER># /usr/bin/python3.6 apps/uvap/skeleton_DEMO.py -d kafka:9092 skeleton -o
```

<a name="webDisplay"></a>
## Web Display
There is an alternative way for demo presentation compared to python scripts
displaying in a window. The following demos run in docker and write
their results into Kafka topics (`*[name_of_demo].Image.jpg`) instead of
the display. From these topics, it is possible to play image streams using the **web display** application.

<a name="topicWriterDemoStarting"></a>
### Starting the Topic Writer Demo
The following script template can be used to start the demos. `[NAME_OF_DEMO]` (including the square brackets)
should be replaced with a string from this set {`head_detection`, `head_pose`, `demography`, `skeleton`}.   
As earlier, `[DEMO_MODE]` (including the square brackets) should be replaced
with a string from this set {`base`, `skeleton`}.  
```
$ ~/uvap/scripts/run_demo.sh \
  --name-of-demo [NAME_OF_DEMO] \
  --demo-mode [DEMO_MODE]
```
Available running options:
1. Head detection demo:
    ```
    $ ~/uvap/scripts/run_demo.sh --name-of-demo head_detection --demo-mode base
    ```
1. Head pose demo:
    ```
    $ ~/uvap/scripts/run_demo.sh --name-of-demo head_pose --demo-mode base
    ```
1. Demography demo:
    ```
    $ ~/uvap/scripts/run_demo.sh --name-of-demo demography --demo-mode base
    ```
1. Tracker demo:  
    Running the tracker demo assumes that the tracker microservice is already running (see [Track calculation](#startTracker)) and creating track detections.
    ```
    # start the demo
    $ ~/uvap/scripts/run_demo.sh --name-of-demo tracker --demo-mode base
    ```
1. Human skeleton demo:
    ```
    $ ~/uvap/scripts/run_demo.sh --name-of-demo skeleton --demo-mode skeleton
    ```

:exclamation: **Warning** :exclamation: After the first run of these scripts [set_retention.sh](#setRetention) script should be executed manually because new (`*.Image.jpg`) topics are created.

<a name="playInTheBowser"></a>
### Viewing in a Browser

1. Starting
    ```
    $ ~/uvap/scripts/run_web_player.sh --config-directory  "$HOME/uvap/models/uvap-web_player"
    ```
1. Testing (optional)  
    a.) checking the log of the docker container
    ```
    $ docker logs uvap_web_player
    ```
    Expected output example:  

    ```bash
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
    $ telnet localhost 9999
    ```
1. In the browser  
    Open a browser and type the following URL:
    ```
    http://localhost:9999#[KAFKA_IMAGE_TOPIC_NAME]
    ```
     - For demo display the `[KAFKA_IMAGE_TOPIC_NAME]` should be replaced with:  
        - Head detection demo: `base.cam.0.head_detection.Image.jpg`
        - Head pose demo: ` base.cam.0.head_pose.Image.jpg`
        - Demography demo: ` base.cam.0.demography.Image.jpg`
        - Tracking demo: `base.cam.0.tracks.Image.jpg`
        - Human skeleton demo: `skeleton.cam.0.skeleton.Image.jpg`
     - For image display the `[KAFKA_IMAGE_TOPIC_NAME]` should be replaced with:   
        - Original stream image: `base.cam.0.lowres.Image.jpg`
        - Anonymized stream image: `base.cam.0.anonymized_lowres.Image.jpg`

    :exclamation: **Warning** :exclamation:  
    **This tool is for demo/debug purposes only!**
    It only has real time playing capability and it has no authorization or authentication.  
    It should only be used in a private network, because it provides a direct access for Kafka (`*.Image.jpg`) topics.   

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
