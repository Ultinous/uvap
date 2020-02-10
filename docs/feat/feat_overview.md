---
id: feat_overview
title: Features Overview
hide_title: true
---

# Features Overview

## Introduction

UVAP provides various key features that enable a wide range of practical
applications.
The features are categorized into the following three areas:

- [Person Detection]
- [Facial Properties and Recognition]
- [Movement Detection]


UVAP has been used to solve real world problems in different domains. 
Some examples:

- Queue management system for retail stores. Customers are counted at the doors 
and in the queuing area in real-time. A prediction model can tell if there will 
be a queue in the next few minutes and staff is alerted before it happens.

- Fall detection in elderly care homes. The system uses two 3D calibrated cameras 
per room and runs human body pose estimation. Based on the body pose fallen body 
pose can be recognized. An alert is sent to the staff in real-time. Staff personals 
can look at the alert, validate the images and decide to take action.

- Measure waiting time on Airports. Face recognition is applied at the entrance and 
exit points in real-time to measure actual waiting time. Prediction is applied and 
displayed to customers entering the queue.

- Recognize unsafe escalator usage. Based on head detection, tracking and full body 
pose different unsafe situations are recognized such as: wrong direction, leaning out, crowd.

### Person Detection

Features relevant to person detection are the following:

- [Head Detection]
- [Anonymization]
- [3D Head Pose]
- [Skeleton Detection]


### Facial Properties and Recognition

Features relevant to facial properties and recognition are the following:

- [Gender Detection]
- [Age Detection]
- [Feature Vector]
- [Feature Vector Clustering]
- [Reidentification]

### Movement Detection

Features relevant to movement detection and tracking are the following:

- [Person Tracking]
- [Pass Detection]
  
### Additional Functions

UVAP has some other features that not directly pertain to video analysis but
help the integrator to set up and monitor the system.
These technical features are the following:

- [Detection Filter]
- [Image Streams]
- [Frame Info]
- [Stream Configurator]
- [Video Annotation]

[3D Head Pose]: detect_person/feat_head_pose.md
[Age Detection]: face_prop/feat_age.md
[Anonymization]: detect_person/feat_anonym.md
[Detection Filter]: other/feat_det_filter.md
[Facial Properties and Recognition]: #facial-properties-and-recognition
[Feature Vector]: face_prop/feat_feature_vector.md
[Frame Info]: other/feat_frame_info.md
[Gender Detection]: face_prop/feat_gender.md
[Head Detection]: detect_person/feat_head_det.md
[Image Streams]: other/feat_show_image.md
[Movement Detection]: #movement-detection
[Person Detection]: #person-detection
[Person Tracking]: detect_movement/feat_track.md
[Pass Detection]: detect_movement/feat_pass_det.md
[Reidentification]: face_prop/feat_reid.md
[Skeleton Detection]: detect_person/feat_skeleton.md
[Stream Configurator]: other/feat_sc_ui.md
[Video Annotation]: other/feat_video_annotation.md
[Feature Vector Clustering]: face_prop/feat_fv_clustering.md
