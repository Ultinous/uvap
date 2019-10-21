---
id: ms_passdet
title: Pass Detector
hide_title: true
---

# Pass Detector

**Pass Detector** microservice uses the _Track Changes_ Kafka topic produced
by the [Tracker] microservice, and produces the _Pass Detections_ Topic.
If one or more directed polylines (pass lines) are specified in the microservice
configuration, **Pass Detector** detects and produces records whenever a track
intersects a pass line. **Pass Detector** helps to detect if an individual enters
or leaves an area of interest.

_Further reading:_

* [Cofiguring Pass Detector]



[Cofiguring Pass Detector]: conf_passdet.md
[Tracker]: ms_track.md
