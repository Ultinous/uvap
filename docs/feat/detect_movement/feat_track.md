---
id: feat_track
title: People Tracking
hide_title: true
---

# People Tracking

The _Tracking_ feature links head detections on a sequence of video frames.
This feature depends on _Head Detection_ feature.

If the position of a head detection is close enough to a former position and
the corresponding video frames are close enough to each other in time, they
form a track.  
A track is a sequence of head detections of a person on a video stream from the
first detection to the disappearance, that is the path of their movement.
The _Tracking_ also serves as a basic feature for higher level UVAP features,
such as _Pass Detection_.

The _Tracking_ feature is provided by the **Tracker** microservice.
For further information, see [Tracker].

For a quick example setup of the _Tracking_ feature, see the [Demo].

[Tracker]: ../../dev/ms_track.md
[Demo]: ../../demo/demo_track.md
