---
id: func_save_start_from_int_state
title: Save and Start from Internal State
hide_title: true
---

# Save and Start from Internal State  
  
The _Save Internal Sate_ and _Start from Internal State_ functions are properties of the _Feature Vector Clustering_ and the _Reidentification_ microservices.  
Both functions are used to start the concerned microservice from a saved internal state instead of an empty database. This is useful for example in a case of unexpected stop or crash of the microservice.  
By default, the microservice starts with an empty database and records feature vectors and clusters while running. If the `save_internal_state` cluster configuration parameter is set to `true` (see [Configuring Feature Vector Clustering]) the _Save Internal Sate_ function saves the clustering database state to a dedicated Kafka topic at frequent times. This information describes how to restore the internal state of the microservice at the given time when the last save was made.  
If the `start_from_internal_state` cluster configuration parameter  is set to `true` (see [Configuring Feature Vector Clustering]) the _Start from Internal State_ function tries to read the last saved state once from the mentioned dedicated topic. If the reading is successful the microservice continues to run with the last saved database state (as if all events happened again from the original start to the stopping of the microservice).  
  
[Configuring Feature Vector Clustering]: conf_cluster.md
