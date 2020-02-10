---
id: feat_reid
title: Reidentification
hide_title: true
---

# Reidentification

The _Reidentification_ feature compares a face on a video frame with
previously detected faces and saves the comparison result.  
This feature depends on the _Facial Feature Vector_ feature. The _Reidentification_ feature also incorporates the properties of [Feature Vector Clustering]. These properties can be configured by the common configuration parameters of the two components, see [Configuring Feature Vector Clustering].  
_Reidentification_ feature is suitable for detecting the re-appearance of a person
or for various security purposes.  
For example, giving access to a resource for the authorized individuals only,
or tracking people on multiple video streams.

This feature is provided by the UVAP **Reidentifier** microservice.
For further information, see [Reidentifier].

For a quick example setup of the _Reidentification_ feature, see
[Single-Camera Reidentification Demo with Pre-clustering] and 
[Reidentification Demo with Person Names].

  
[Feature Vector Clustering]: feat_fv_clustering.md  
[Cluster Realization]: feat_cluster_realization.md  
[Reidentifier]: ../../dev/ms_reid.md
[Single-Camera Reidentification Demo with Pre-clustering]: ../../demo/demo_reid_1.md
[Configuring Feature Vector Clustering]: ../../dev/conf_cluster.md  
[Reidentification Demo with Person Names]: ../../demo/demo_reid_with_name.md
