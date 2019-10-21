---
id: feat_head_pose
title: 3D Head Pose
hide_title: true
---

# 3D Head Pose

The _3D Head Pose_ feature detects the three dimensional orientation of the
head of a person on video frames. The orientation of the detected head is saved
as three angles in degrees: yaw, pitch, and roll. _3D Head Pose_ detection
depends on the _Head Detection_ feature.

The _3D Head Pose_ feature provides low level data for attention detection
and serves as a filter to increase the accuracy of other detections, such as
_Age_, _Gender_, and _Facial Feature Vector_. It can also be used in higher level
UVAP features.

This feature is provided by **Multi-Graph Runner (MGR)**.
For further information, see [MGR].

For a quick example setup of the _Head Pose_ feature, see the [Demo].

[MGR]: ../../dev/ms_mgr.md
[Demo]: ../../demo/demo_head_pose.md
