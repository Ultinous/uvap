# UVAP Quick Start Guide
## Introduction
### Goals
After this section:
- you can start UVAP for the basic detection
- you can visualize the basic detections with pyhthon scripts
- you can resolve few simple use cases

### Requirements
Finished every points in [Installation Guide](installation_guide.md).

## Start analysis

### Configure UVAP

The `[RTSP_URL]` should be replaced with a URL which points to a valid RTSP stream, for example an IP camera. This should look like this: `rtsp://192.168.0.1/` This URL also can contain username and password if the stream is protected, for example: `rtsp://username:password@192.168.0.1/`  
We use different configuration for base detection for save GPU resources.
The `[DEMO_MODE]` should be replaced with a string from this set {base, skeleton}.  
The 'base' demos:
- show image
- Head detection
- Head pose
- Demography

The 'skeleton' demo(s):
- Human skeleton

The `[DROP_RATE]` is an optional parameter for change the frequency of analysis on frames, by default the UVAP uses all frame for the analysis. If you set the `[DROP_RATE]` to be 3, the UVAP will use every 3th frame for analysis, so it will be faster.
```
$ ~/uvap/scripts/config.sh --models-directory "$HOME/uvap/models" --stream-url [RTSP_URL] --demo-mode [DEMO_MODE] --drop-rate [DROP_RATE]
```
If you want to change the stream url later, you just need to run this install script again.

### Starting UVAP
Finally you have to start up the framework:
```
$ ~/uvap/scripts/run.sh --models-directory "$HOME/uvap/models" --license-data-file-path [ABSOLUTE_FILE_PATH_OF_LICENSE_TXT_FILE] --license-key-file-path [ABSOLUTE_FILE_PATH_OF_LICENSE_KEY_FILE] -- --net=uvap
```
Check if the container (named `uvap_mgr`) is running:
```
$ docker container inspect --format '{{.State.Status}}' uvap_mgr
   running
```
If the status of uvap container is not running then send the output of the following command to `support@ultinous.com`.
```
$ docker logs uvap_mgr
```
You can also manage these docker containers with standard docker commands.
Details: https://docs.docker.com/engine/reference/commandline/docker/

Check if the kafka topics are created:
```
$ docker exec -it kafka /bin/bash -c 'kafka-topics --list --zookeeper zookeeper:2181'
```
Try to fetch data from a kafka topic:
```
$ kafkacat -b kafka -t base.cam.0.dets.ObjectDetectionRecord.json
```
### Set retention

The `*.Image.jpg` topics required a huge storage, because it contains every frame image in JPG format. We can change the lifetime of topic, for example 15 minutes:
```
$  ~/uvap/scripts/set_retention.sh
```
:exclamation: **Warning** :exclamation: Without this settings the `*.Image.jpg` topics use a lot of storage space!

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
## Demo usage
Tree view of demo package:
```
~/uvap$ tree demo_applications/
demo_applications/
├── apps
│   └── uvap
│       ├── demography_DEMO.py
│       ├── head_detection_DEMO.py
│       ├── head_pose_DEMO.py
│       ├── list_messages.py
│       ├── list_topics.py
│       ├── show_image_DEMO.py
│       └── skeleton_DEMO.py
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
### Environment
We packed every requirements into a docker image. (ultinous/uvap:uvap_demo_applications_latest)  
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
You can run the following scripts here!
All script in `/apps/uvap` directory have help function:
```
 root@<CONTAINER ID>:/ultinous_app# /usr/bin/python3.6 apps/uvap/*.py -h
```
### Helpes scripts
The `[DEMO_MODE]` should be 'base'. (see: Start analysis/Configure UVAP)  
You can check data in Kafka with the following scripts:
#### List topics
List topics from Kafka.
```
root@<CONTAINER ID>:/ultinous_app# /usr/bin/python3.6 apps/uvap/list_topics.py kafka:9092
```
You can see something like this:
```
base.cam.0.lowres.Image.jpg
base.cam.0.ages.AgeRecord.json
base.cam.0.poses.HeadPose3DRecord.json
base.cam.0.ages.GenderRecord.json
base.cam.0.dets.ObjectDetectionRecord.json
```

#### List messages
List messages from a topic.
E.g.:
```
root@<CONTAINER ID>:/ultinous_app# /usr/bin/python3.6 apps/uvap/list_messages.py kafka:9092 base.cam.0.ages.GenderRecord.json
```
You can see something like this:
```
1561360391236 <bound method NoKeyErrorDict.asdict of {'base': {'0': {'head_detection': {'1561360391236_0': {'gender': {'gender': 'MALE', 'confidence': 0.952010512, 'end_of_frame': False}}}}}}>
1561360391272 <bound method NoKeyErrorDict.asdict of {'base': {'0': {'head_detection': {'1561360391272_0': {'gender': {'gender': 'MALE', 'confidence': 0.941216767, 'end_of_frame': False}}}}}}>
1561360391304 <bound method NoKeyErrorDict.asdict of {'base': {'0': {'head_detection': {'1561360391304_0': {'gender': {'gender': 'MALE', 'confidence': 0.947949708, 'end_of_frame': False}}}}}}>
1561360391336 <bound method NoKeyErrorDict.asdict of {'base': {'0': {'head_detection': {'1561360391336_0': {'gender': {'gender': 'MALE', 'confidence': 0.919374943, 'end_of_frame': False}}}}}}>
```
### Basic demos
The `[DEMO_MODE]` should be 'base'. (see: Start analysis/Configure UVAP)
#### Show images
1.) Original image (stored the RTSP stream in Kafka)
```
root@<CONTAINER ID>:/ultinous_app# /usr/bin/python3.6 apps/uvap/show_image_DEMO.py kafka:9092 base.cam.0.lowres.Image.jpg
```
2.) Anonymized image (by UVAP)
```
root@<CONTAINER ID>:/ultinous_app# /usr/bin/python3.6 apps/uvap/show_image_DEMO.py kafka:9092 base.cam.0.anonymized_lowres.Image.jpg
```
#### Head_detection
Play video from a jpeg topic and visualize the head detection with an orange bounding box around a head].
Required topics:
- <prefix>.cam.0.lowres.Image.jpg
- <prefix>.cam.0.dets.ObjectDetectionRecord.json

```
root@<CONTAINER ID>:/ultinous_app# /usr/bin/python3.6 apps/uvap/head_detection_DEMO.py kafka:9092 base
```

#### Head pose
Play video from a jpeg topic and visualize the head pose with 3 diff color lines.  
Required topics:
- <prefix>.cam.0.lowres.Image.jpg
- <prefix>.cam.0.dets.ObjectDetectionRecord.json
- <prefix>.cam.0.poses.HeadPose3DRecord.json

![The yaw pitch and roll angles in the human head motion](images/head-motion.png)
```
root@<CONTAINER ID>:/ultinous_app# /usr/bin/python3.6 apps/uvap/head_pose_DEMO.py kafka:9092 base
```
#### Demography
Play video from a jpeg topic and visualize the head detection with an orange bounding box around a head and write demography (gender & age) data above the head.  
Required topics:
- <prefix>.cam.0.lowres.Image.jpg
- <prefix>.cam.0.dets.ObjectDetectionRecord.json
- <prefix>.cam.0.genders.GenderRecord.json
- <prefix>.cam.0.ages.AgeRecord.json

```
root@<CONTAINER ID>:/ultinous_app# /usr/bin/python3.6 apps/uvap/demography_DEMO.py kafka:9092 base
```

### Advanced demos
The `[DEMO_MODE]` should be 'skeleton'. (see: Start analysis/Configure UVAP)
#### Human skeleton
Play video from a jpeg topic and main points of a human skeleton linked with colorful lines.  
Required topics:
- <prefix>.cam.0.lowres.Image.jpg
- <prefix>.cam.0.skeletons.SkeletonRecord.json

```
root@<CONTAINER ID>:/ultinous_app# /usr/bin/python3.6 apps/uvap/skeleton_DEMO.py kafka:9092 skeleton
```
### Use cases (for practice)
#### Alerting system
Task:   
Create a demo with people counting in area and if there are more then 1 person give a visualized alert.  
Details:  
- Modify an existing demo script.
- You camera's resolution is 1920x1080.
- The area is a rectangles, coordinates of top left corner: (200,200) and coordinates of bottom right corner: (1200, 900), draw it on the screen with a while line.
- For the visualization use an 'Alert' image (/image/alert.png) and change the rectangle color to red.

#### See the s(h)elf
Task:  
Create a demo with people counting who seeing a shelf exactly in front of the camera.
Details:  
- Modify an existing demo script.
- You camera's resolution is 1920x1080.
- For the visualization write a number (how many were in the order) above the head of the person.

#### High five
Task:  
Create a demo with detecting and visualizing the valid high fives on the screen.
Details:  
- Modify an existing demo script.
- You camera's resolution is 1920x1080.
- Valid high fives: 2 right hands, upper then the shoulders
- For the visualization create a border of the screen and change the color of it.
