---
id: ms_reid
title: Basic Reidentifier
hide_title: true
---

# Basic Reidentifier

**Basic Reidentifier** microservice processes feature vectors or clusters
and finds reappearances.

If a processed feature vector or cluster is unknown for the system, it becomes
**registered**. If the processed feature vector or cluster is already
registered, it is **reidentified** by the system.

A camera input stream can be used for registration, reidentification
or both. The microservice can handle multiple input topics and produces results
into one output topic. The roles of input topics, reidentification parameters,
registration parameters, and topic consuming parameters can be configured.

The feature vectors or clusters belonging to a single individual  are similar even
when changing the distance, head pose, and so on. For each pair of feature
vectors or clusters, a similarity score is produced. This score falls between
`0.0` and `1.0`. A higher score means, it is more likely that the two feature
vectors or clusters represent the same individual. **Basic Reidentifier** is
recognizing this correlation between feature vectors and clusters based on
similarity scores.

The microservice has basically two functions:

* Registers the new feature vectors or clusters coming from registration
  streams. Feature vectors and clusters coming from reidentification-only
  streams are never stored.

* Tries to reidentify feature vectors and clusters coming from reidentification
  streams. The input is compared to all stored clusters and the similarity scores
  are computed; the result is controlled by configuration parameters.

_Further reading:_

* [Cofiguring Basic Reidentifier]

[Cofiguring Basic Reidentifier]: conf_reid.md
