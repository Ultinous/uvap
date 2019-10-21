# Setting the Retention Period

Kafka has a default retention period set to 168 hours. The `*.Image.jpg` topics
require a large amount of storage space because they contain all frames in
JPG image format. The retention period of JPG topics can be changed with the
`set_retention.sh` script.

 > **Attention!**  
   By default, the retention period is disabled. Without these settings, the
   `*.Image.jpg` topics use a lot of storage.

To set retention time:

```
$ "${UVAP_HOME}"/scripts/set_retention.sh --retention-unit [UNIT] \
   --retention-number [NUMBER] 
```

Where:

* **`[UNIT]`**:

  A unit of time.  
  Replace `[UNIT]` (including brackets) with one of the following
  time units:
  
  * `ms` for milliseconds
  * `second` for seconds
  * `minute` for minutes
  * `hour` for hours
  * `day` for days

* **`[NUMBER]`**:

  A parameter defining duration.  
  Replace `[NUMBER]` (including brackets) with a number, that
  (together with the retention unit) defines the retention time to set.

For example, to set the retention to 15 minutes:

```
$ "${UVAP_HOME}"/scripts/set_retention.sh --retention-unit minute \
  --retention-number 15
```

Expected output:

```
INFO: These topics will change:
base.cam.0.anonymized_original.Image.jpg
base.cam.0.original.Image.jpg
Completed Updating config for entity: topic 'base.cam.0.anonymized_original.Image.jpg'.
Topic:base.cam.0.anonymized_original.Image.jpg	PartitionCount:1	ReplicationFactor:1	Configs:retention.ms=900000
	Topic: base.cam.0.anonymized_original.Image.jpg	Partition: 0	Leader: 1001	Replicas: 1001	Isr: 1001
Completed Updating config for entity: topic 'base.cam.0.original.Image.jpg'.
Topic:base.cam.0.original.Image.jpg	PartitionCount:1	ReplicationFactor:1	Configs:retention.ms=900000
	Topic: base.cam.0.original.Image.jpg	Partition: 0	Leader: 1001	Replicas: 1001	Isr: 1001
```
