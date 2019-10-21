---
id: ms_mgr
title: Multi-Graph Runner
hide_title: true
---

# Multi-Graph Runner

**Multi-Graph Runner (MGR)** uses the image processing algorithm to turn video
streams into lightweight data streams, such as a detection stream, or a face
feature vector stream. **MGR** has various built-in image processing algorithms
that can be combined in a flexible way to produce the desired output. 

There are two types of algorithms:

* Deep learning models (such as; face detection, face recognition, and full
  body pose)

* Traditional image processing algorithms (such as; image resize, image
  rotation, cropping, and drawing)
   

Output of the **MGR** are typically lightweight data streams written to Kafka.
However, **MGR** can also produce image sequences or video streams for debugging
or presentation purposes. These streams need to be compressed before being sent
towards Kafka, because the bandwidth of uncompressed video streams is typically
close to or over disk and network I/O limits, so they cannot be handled by Kafka
otherwise. Modern video compression algorithms (such as H256) have a compression
ratio better than 1:100.

>**Note:**  
**MGR** uses Nvidia GPUs to do most of the data processing. One **MGR** instance
can process multiple video streams in real-time. One MGR can handle only one
GPU, so for each GPU, a separate **MGR** instance has to be run.

## Deployment

To run MGR, the server must have an Nvidia 1060 GPU with 6GB GPU memory or
better. MGR is has to be executed with `nvidia-docker`. If the server
has more GPUs, a separate MGR instance is needed for each GPU for optimal
performance.

## Runtime Performance

One MGR instance can process multiple video streams but the load of the system
has to be carefully calculated. If the MGR has more tasks than it is able to 
handle, it throws away input frames without processing or  queues them. This
can be controlled with the drop mode in the `environment` section:

   ```
   environment:
   {
     debug_level: 4
     profile: true
     analysis_thread_count: 2
     gui: NORMAL
     drop_off: {}    # do not drop frames, instead queue them up
     #drop_on: {}    # if the system gets overloaded drop frames
     kafka_broker_list: "localhost:9092"
   }
   ```

Using the `nvidia-smi` tool to monitor GPU load is recommended.

Though runtime performance depends on various factors, the following operations
are the most demanding:

* Running deep learning models
* Encoding video
* Decoding video

### Detector

The first deep learning model is typically a detector (for example, head
detector). This is one of the most demanding operations. Cost of the detector
is a complex function but the most important factors are the following:

* **FPS**: cost of the detector is linear with the frame rate. If the system 
is overloaded one of the easiest way to decrease is to decrease the frame rate. 
It can be done on the camera or by using the ```keep_rate``` and ```frame_period_ms``` 
parameter. The ```keep_rate``` is an optional parameter for changing the frequency of 
analysis on frames. By default, UVAP uses all frames for the analysis. If you set 
the ```keep_rate``` to e.g. `3`, UVAP will use every 3rd frame for analysis, 
so it will be faster. Emphasize that ```frame_period_ms``` is about camera frame rate. 
The ```keep_rate``` is applied after that.  
 Example:  
 frame_period_ms = 40 # 25 FPS  
 keep_rate = 3   
 It means that process every 3rd frame from a camera that expected to give 25 frames per seconds.

* **Resolution**: cost of the detector is directly proportional to the number
   of pixels (and quadratically to the image size). The resolution can be set
   with the `scaling_factor` parameter. Halving `scaling_factor` decreases the
   cost of the detector four times.

### Skeleton

Skeleton models have the same cost characteristics as the detector. It does not
support scale factor (it rescales the input image to a fixed resolution). FPS
is the only option to control the load of this model.

### Other Models

The cost of head pose, face recognition, demographics are all proportional to
the number of crops. The load can increase significantly in crowded environments.
<!--TODO: use object filter to limit the number of crops. */-->

### Saving Video

Saving video always involves video encoding, which is a computation heavy
operation.
<!--TODO: write to avi, write to kafka.-->

_Further reading:_

* [Configuring Multi-Graph Runner]


[Configuring Multi-Graph Runner]: conf_mgr.md
