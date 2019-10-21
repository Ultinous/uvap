---
id: feat_reid
title: Reidentification (Basic)
hide_title: true
---

# Reidentification (Basic)

The _Reidentification_ feature compares a face on a video frame with
previously detected faces and saves the comparison result.  
This feature depends on _Facial Feature Vector_ feature.

_Reidentification_ feature suitable for detecting the re-appearance of a person
or for various security purposes.  
For example, giving access to a resource for the authorized individuals only,
or tracking people on multiple video streams.

This feature is provided by the UVAP **Basic Reidentifier** microservice.
For further information, see [Basic Reidentifier].

For a quick example setup of the _Reidentification_ feature, see
[Basic Reidentification Demo with One Camera] and
[Basic Reidentification Demo with Two Cameras].


[Basic Reidentifier]: ../../dev/ms_reid.md
[Basic Reidentification Demo with One Camera]: ../../demo/demo_reid_1.md
[Basic Reidentification Demo with Two Cameras]: ../../demo/demo_reid_2.md
