---
id: feat_age
title: Age Detection
hide_title: true
---

# Age Detection

The _Age Detection_ feature estimates and saves the age data of a human face on
a video frame. For example, this feature can be used to provide statistical
data or to set age limits.

This feature depends on UVAP's _3D Head Pose_ and _Head Detection_
features as only images where the detected person is facing the camera
(in good resolution) are suitable for age estimation. In practice, a person's
age can be estimated from multiple detections and the _Age Detection_ feature
only provides basic age data.

This feature is provided by **Multi-Graph Runner (MGR)**.
For further information, see [MGR].

>**Note:**  
In an integrator application, in order to improve accuracy it is recommended
to aggregate multiple age detection results based on tracks provided by the
_Tracker_ feature or feature vector similarity.

For a quick example setup of the _Age Detection_ feature, see the [Demo].


[MGR]: ../../dev/ms_mgr.md
[Demo]: ../../demo/demo_demography.md
