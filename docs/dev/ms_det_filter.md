---
id: ms_det_filter
title: Detection Filter
hide_title: true
---

# Detection Filter

**Detection Filter** microservice suppliments the _Object Detection_ Kafka
topic produced by the other microservices.

>**Note:**  
For each detection filter a separate microservice needs to be run.

The filter is configured by `.json` configuration files. For further details on
the configuration, see [Cofiguring Detection Filter].

If no areas are specified in the microservice configuration, the entire frame
is considered as a positive area.

The microservice works the following way:
1. **Detection Filter** checks if the detection reaches the confidence level.
1. **Detection Filter** checks if the detection type matches the ones configured.  
   If no detection types are defined, all detections are included.
1. **Detection Filter** checks if the detection does not fall into a negative area.
1. **Detection Filter** checks if the detection falls into a positive area.  
   If no positive areas are defined, the detection is considered to be in a positive area.

If the detection passes all checks, it is included in the produced topic.


[Cofiguring Detection Filter]: conf_det_filter.md