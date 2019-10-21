---
id: feat_feature_vector
title: Facial Feature Vector
hide_title: true
---

# Facial Feature Vector

The _Facial Feature Vector_ feature converts the facial images of a person to
1024 byte long representations named as Feature Vector. 

Feature Vectors cannot be converted back to image, however they serve as basic
data for reidentification and facial similarity search (also called lookalike
search).

The _Facial Feature Vector_ feature is highly dependent on UVAP's _3D Head Pose_
and _Head Detection_ features as only images where the detected person is facing
the camera (in good resolution) are suitable for Feature Vector creation.

This feature is provided by **Multi-Graph Runner (MGR)**.
For further information, see [MGR].

>**Note:**  
In an integrator application, it is recommended to aggregate multiple feature
vectors of the same person in order to improve the accuracy.


[MGR]: ../../dev/ms_mgr.md
