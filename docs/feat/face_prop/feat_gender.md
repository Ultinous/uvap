---
id: feat_gender
title: Gender Detection
hide_title: true
---

# Gender Detection

The _Gender Detection_ feature estimates and saves the gender data of a human
face on a video frame.

This feature depends on UVAP's _3D Head Pose_ and _Head Detection_ features, as
only images where the detected person is facing the camera (in good resolution)
are suitable for gender estimation. In practice, a person's gender can be
estimated from multiple detections and the _Gender Detection_ feature only
provides basic gender data. 

The _Gender Detection_ feature is provided by **Multi-Graph Runner (MGR)**.
For further information, see [MGR].

>**Note:**  
In an integrator application, in order to improve accuracy it is recommended
to aggregate multiple gender detection results based on tracks provided by the
_Tracker_ feature or feature vector similarity.

For a quick example setup of the _Gender Detection_ feature, see the [Demo].


[MGR]: ../../dev/ms_mgr.md
[Demo]: ../../demo/demo_demography.md
