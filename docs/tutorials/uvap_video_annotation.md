---
id: uvap_video_annotation
title: Video Annotation Tutorial
hide_title: true
---

# Video Annotation Tutorial

## Prerequisites
Before continuing with the tutorial, ensure the following:
- UVAP is installed as instructed in [Setting Up UVAP]
- No UVAP-related Docker containers are running

## Preparing Source Video and Containers

1. Create the source directory for videos:
   ```
   $ mkdir -p "${UVAP_HOME}"/videos
   ```

1. Copy the source video to the created directory:
   ```
   $ cp -i <current_video_path>/testvideo.mkv "${UVAP_HOME}"/videos/testvideo.mkv
   ```

   >**Note:**  
   By using `-i` for interactive, the user is asked if the file is to be replaced (if already exists).

1. Check video resolution and frame rate:
   ```
   $ ffprobe "${UVAP_HOME}"/videos/testvideo.mkv
   ```


   >**Note:**  
   Important part of the output of `ffprobe`:
   ```
   [...]
       Stream #0:0(eng): Video: h264 (Main), yuvj420p(pc, bt709, progressive), 1280x720 [SAR 1:1 DAR 16:9], 6 fps, 6 tbr, 1k tbn, 2k tbc (default)
   [...]
   ```
   >Where:  
   - Resolution is 1280 × 720 (width × height)
   - Frame rate is 6 fps

1. Stop, remove, and restart Zookeeper and Kafka containers with the following command:

   >**Attention!**  
   This process removes all topics from Kafka.

   ```
   $ "${UVAP_HOME}"/scripts/restart_empty_kafka.sh
   ```

## Demo Usage for Video Annotation

### Available Arguments

List available arguments of video annotation command with the following command:

```
$ "${UVAP_HOME}/scripts/video_annotation.sh --help
```
Expected output:
```
Usage: ./video_annotation.sh [OPTION]...
Options (those, that do not have a default value, are mandatory options):
	--demo-name                               	<head_detection|head_pose|demography|tracker|skeleton|basic_reidentification>
	--video-dir                               	directory path of the input and output videos - default: /home/ultinous/uvap/scripts/../videos
	--video-file-name                         	basename of the input video file inside the --video-dir directory
	--fps-number                              	the FPS number of the input video
	--width-number                            	the width in pixels of the input video
	--height-number                           	the height in pixels of the input video
	--demo-applications-dir                   	directory path of demo applications scripts - default: /home/ultinous/uvap/scripts/../demo_applications
	--templates-dir                           	directory path of configuration templates - default: /home/ultinous/uvap/scripts/../templates
	--config-ac-dir                           	directory path of configuration files - will be created if not existent - default: /home/ultinous/uvap/scripts/../config
	--models-dir                              	directory path of AI models - default: /home/ultinous/uvap/scripts/../models
	--license-data-file                       	data file of your UVAP license - default: /home/ultinous/uvap/scripts/../license/license.txt
	--license-key-file                        	key file of your UVAP license - default: /home/ultinous/uvap/scripts/../license/license.key
	--uvap-mgr-docker-image-name              	tag of docker image to use - default: will be determined by git tags
	--uvap-demo-applications-docker-image-name	tag of docker image to use - default: will be determined by git tags
	--uvap-kafka-tracker-docker-image-name    	tag of docker image to use - default: will be determined by git tags
	--uvap-kafka-reid-docker-image-name       	tag of docker image to use - default: will be determined by git tags
	--verbose  
```
>**Note:**
Options that do not have a default value are mandatory.

### Annotating the Video

Use the video writer script to create the output video into `"${UVAP_HOME}"/videos`
with `[IMAGE_TOPIC_NAME].avi` name, overwriting the existing file:

```
   $ "${UVAP_HOME}"/scripts/video_annotation.sh \
   --demo-name [DEMO_NAME] \
   --video-file-name [INPUT_VIDEO] \
   --fps-number [FPS] \
   --width-number [WIDTH] \
   --height-number [HEIGHT] 
```

Parameters:
- `[DEMO_NAME]`: name of the demo. Replace (including the brackets) with a name of the
demo (string).  
  Valid values of `[DEMO_NAME]` are the following:
  - `head_detection`
  - `head_pose`
  - `demography`
  - `tracker`
  - `skeleton`
  - `basic_reidentification`
- `[INPUT_VIDEO]`: name of the input video. Replace parameter with the name of the
existing video, following the example above: `testvideo.mkv`.
- `[FPS]`, `[WIDTH]`, and `[HEIGHT]`: parameters of output video. Replace with the
parameters of the original video, see [Preparing Source Video and Containers].

Expected console output:
```
Starting to configure...
Finished configuring.
Starting the core analysis...
Finished core analysing.
Starting to annotate...
Finished annotating.
Starting to write video...
Finished writing video.
```

Default path of result video:
```
$ "${UVAP_HOME}"/videos/[DEMO_MODE].cam.0.[DEMO_NAME].Image.jpg.avi
```


[Preparing Source Video and Containers]: #preparing-source-video-and-containers
[Setting Up UVAP]: ../install/uvap_install_setup.md