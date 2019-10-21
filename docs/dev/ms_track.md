---
id: ms_track
title: Tracker
hide_title: true
---

# Tracker

**Tracker** microservice builds routes based on the result of head detection.
If a head detection is close enough to a former head detection, a track is
formed from the two. Each following head detections close enough extends this
track with new entries.

The geometric and temporal distance thresholds can be configured.

_Further reading:_

* [Cofiguring Tracker]

[Cofiguring Tracker]: conf_track.md
