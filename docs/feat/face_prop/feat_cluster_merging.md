---
id: feat_cluster_merging
title: Feature Vector Cluster Merging
hide_title: true
---

# Feature Vector Cluster Merging

_Cluster Merging_ is a property of [Feature Vector Clustering] and [Reidentifier] that merges two or more clusters into one when they are more
similar to each other than a configurable threshold. The current similarity threshold is
defined by the `initial threshold` and the `threshold_discount_rate` parameters and
decreases as the number of input samples in the potentially mergeable clusters grows. But never goes under
the `min_threshold` parameter. For details about configurable parameters and calculating
the `current threshold` of the _Cluster Merging_ feature, see [Configuring Feature
Vector Clustering].  
The result of merging is a `MERGE_EVENT` shown in the `FVClusterUpdateRecord` of
the concerning stream's Kafka topic. A new cluster is created with it's own `cluster id`
and representative feature vector and the merged ones are deleted. For an example of a
`MERGE_EVENT` type `FVClusterUpdateRecord` output, see [Configuring Feature Vector
Clustering].  
  
[Configuring Feature Vector Clustering]: ../../dev/conf_cluster.md  
[Feature Vector Clustering]: feat_fv_clustering.md  
[Reidentifier]: feat_reid.md
