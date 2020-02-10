---
id: feat_cluster_realization
title: Cluster Realization
hide_title: true
---

# Cluster Realization  
  
_Cluster Realization_ is an option to distinguish output clusters that are composed of sufficient number of feature vector observations.  
When _Cluster Realization_ is enabled, newly created clusters are initially unrealized.
When the number of observations reaches a configurable value or a defined time interval 
passes since the creation of the cluster (the time of the first observation) the cluster 
becomes realized. Registration events are generated for both realized and unrealized 
clusters.  
Once a cluster is realized it is handled and actions are performed based on Feature 
Vector Clustering configuration parameter settings. For details about using Feature Vector Clustering configuration parameters to set the conditions of Cluster Realization and define the handling of realized clusters, see [Configuring Feature Vector Clustering].  
_Cluster Realization_ is a property of both the _Feature Vector Clustering_ and the _Reidentification_ features.  
  
[Configuring Feature Vector Clustering]: ../../dev/conf_cluster.md
