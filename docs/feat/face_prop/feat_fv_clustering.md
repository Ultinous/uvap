---
id: feat_fv_clustering
title: Feature Vector Clustering
hide_title: true
---

# Feature Vector Clustering

The _Feature Vector Clustering_ feature creates clusters of input feature vectors. The input vectors belonging to the same cluster are associated based on similarity.  
Recognized feature vectors used as input for creating a cluster are called feature vector observations.    

All clusters are stored in the same database regardless to which stream the input feature vectors come from. Each 
cluster is represented by a single feature vector which can be different from all feature vector observations.  

The feature implements cluster updates which can be the following:
* Updating an existing cluster based on an observed new feature vector that is similar to the representative feature 
vector of the concerning cluster stored in the data base
* Creating a new cluster based on an observed new feature vector that is not similar to any existing representative 
feature vectors.  

Creating a new cluster is called cluster realization. Realizing a cluster and handling newly relaized clusters depend on Feature Vector Clustering configuration parameters defined in [Configuring Feature Vector Clustering].
* Merging two or more clusters into one when they are more similar to each other than a configurable threshold.
See [Feature Vector Cluster Merging].  

A typical use case of the feature is pre-clustering for _Reidentification_. The _Reidentification_ feature matches observed feature vectors to the representative feature vectors of relized clusters that are stored in a database. Single feature vectors can be unreliable for face recognition while pre-clustering can increase the accuracy.  
The representative feature vector of a cluster can be used as input for the _Reidentification_ feature after the cluster is realized. For details about realizing a new cluster see [Cluster Realization].  
  
A typical configuration example for pre-clustering is shown below:  
```
{
   "clustering_config": {
       "method": "SIMPLE_AVERAGE",
       "cluster_realization": {
           "min_num_samples": 5,
           "time_limit_ms": 10000
       },
       "save_internal_state": false,
       "start_from_internal_state": false
   },
   "input_stream_configs": [{
       "stream_id": "camera_1",
       "fv_field_selector": {
           "feature_vector_path": "features"
       },
       "reg_stream_config": {
           "reg_threshold": 0.8,
           "cluster_retention_period_ms": 86400000,
       },
   }]
}
```

  
For details about the _Reidentification_ feature see [Reidentification].  
This feature depends on the _Facial Feature Vector_ feature.  
  
[Configuring Feature Vector Clustering]: ../../dev/conf_cluster.md  
[Feature Vector Cluster Merging]: feat_cluster_merging.md  
[Cluster Realization]: feat_cluster_realization.md  
[Reidentification]: feat_reid.md