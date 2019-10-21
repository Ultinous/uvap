---
id: ms_reid
title: Basic Reidentifier
hide_title: true
---

# Basic Reidentifier

**Basic Reidentifier** microservice processes feature vectors and finds
reappearances.

If a processed feature vector is unknown for the system, it becomes
**registered**. If the processed feature vector is already registered,
it is **reidentified** by the system.

Each input topic can be used for registration, reidentification
or both. The microservice can handle multiple input topics and produces results
into one output topic. The roles of input topics, reidentification parameters,
registration parameters, and topic consuming parameters can be configured.

For each individual, the produced feature vectors correlate even when changing
the distance, head pose, and so on. For each pair of feature vectors, a
similarity score is produced. This score falls between `0.0` and `1.0`. A higher
score means, it is more likely that the two feature vectors represent the same
individual. **Basic Reidentifier** is recognizing this correlation between
feature vectors based on similarity scores.

The microservice has basically two functions:

* Registers the new feature vectors coming from registration streams. Feature
  vectors coming from reidentification-only streams are never stored.

* Tries to reidentify feature vectors coming from reidentification streams.
  This is proceeded by producing the score with each stored feature vector; the
  result is controlled by configuration parameters.

_Further reading:_

* [Cofiguring Basic Reidentifier]

[Cofiguring Basic Reidentifier]: conf_reid.md
