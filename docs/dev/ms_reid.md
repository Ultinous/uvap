---
id: ms_reid
title: Reidentifier
hide_title: true
---

# Reidentifier

**Reidentifier** microservice processes feature vectors or clusters
and finds reappearances.

If a processed feature vector or cluster is unknown for the system, it becomes
**registered**. If the processed feature vector or cluster is already
registered, it is **reidentified** by the system.

Camera input streams and already clustered streams can be used for registration, reidentification
or both. The microservice can handle multiple input topics and produces results
into one output topic. The roles of input topics, reidentification parameters,
registration parameters, and topic consuming parameters can be configured.

The feature vectors or clusters belonging to a single individual are similar even
when changing the distance, head pose, and so on. For each pair of feature
vectors or clusters, a similarity score is produced. This score falls between
`0.0` and `1.0`. A higher score means, it is more likely that the two feature
vectors or clusters represent the same individual. **Reidentifier** is
recognizing this correlation between feature vectors and clusters based on
similarity scores.

The microservice has basically two functions:

* Registers the new feature vectors or clusters coming from registration
  streams. Feature vectors and clusters coming from reidentification-only
  streams are never stored.

* Tries to reidentify feature vectors and clusters coming from reidentification
  streams. The input is compared to all stored clusters and the similarity scores
  are computed; the result is controlled by configuration parameters.

## Person Stream

The person stream is used to add feature vectors of previously known individuals
to the internal database of the Reidentifier. Keys of the records in the person
stream can be changed to any string, such as the name of the individual or a
unique ID.

In general, the identity of the detected persons detected by the reidentifier
is unknown when the source is simple camera stream. The person stream offers a
solution to this by enabling the reidentifier to match the detected persons to
a previously defined identity.  

Person streams can also be regarded as feature vector databases, in case they are compacted. In this case, only one feature vector belongs to each key.  
  

_Further reading:_  
  
* [Cofiguring Reidentifier]
* [Person Stream Configuration]

[Cofiguring Reidentifier]: conf_reid.md
[Person Stream Configuration]: conf_reid.md#person_stream_configuration