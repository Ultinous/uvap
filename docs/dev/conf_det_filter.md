---
id: conf_det_filter
title: Configuring the Detection Filter
hide_title: true
---

# Configuring the Detection Filter

This microservice is not GPU related.

## Environment Variables

- `KAFKA_DETECTION_FILTER_MS_PROPERTY_FILE_PATHS`: property files path list.

## Properties

The values of properties with the `.file` extension are the paths of the `.json`
files, while the values of properties with the `.data` extention are the `.json`
configurations themselves.

>**Attention!**  
Setting `.data` and `.file` properties are exclusive to each other, meaning
setting both `ultinous.service.kafka.detection.filter.ms.config.data` and
`ultinous.service.kafka.detection.filter.ms.config.file` results in an error.

### ultinous.service.kafka.detection.filter.ms.config.data

| Property      | ultinous.service.kafka.detection.filter.ms.config.data   |
| ------------- | ------------------------------------------------------ |
| Description   | **Detection Filter** microservice configuration, and optionally authentication and detection filter configuration. Content must be in one-liner JSON format described in [Superconfig Topic Definitions].  |
| Required      | Required   |


### ultinous.service.kafka.detection.filter.ms.config.file

| Property      | ultinous.service.kafka.detection.filter.ms.config.file   |
| ------------- | ------------------------------------------------------ |
| Description   | **Detection Filter** microservice configuration, and optionally authentication and detection filter configuration. Content must be the path to the JSON format configuration file.  |
| Required      | Required   |

Example:

```
{
  "source_options": {
    "start":"START_DATETIME",
    "start_date_time": "2019-05-31T10:30:00.000 +02:00",
    "end":"END_NEVER"
  },
  "source": {
    "broker_list": "127.0.0.1:64997",
    "name": "some_kafka_topic.ObjectDetectionRecord.json"
  },
  "target_options": {
    "handling": "REPLACE"
  },
  "target": {
    "broker_list": "127.0.0.1:64997",
    "name": "some_other_kafka_topic.ObjectDetectionRecord.json"
  },
  "config_data": { ... }
}

```


In this example, the sources are set to be read from the given date and never
stop reading them. One feature vector source is defined with broker list and
name. The target stream is being replaced.

For an example of the properties of the `config_data` field, see the
[Example of a DetectionFilterConfigRecord from Kafka].

### ultinous.service.kafka.detection.filter.auth.defs.data

| Property      | ultinous.service.kafka.detection.filter.auth.defs.data   |
| ------------- | ------------------------------------------------------ |
| Description   | Authentication definition data in one-liner JSON format corresponding to the definitions described in [Superconfig Authentication Definitions].  |
| Required      | Optional   |
| Note          | Required if ID based authentication is used in `ultinous.service.kafka.detection.filter.ms.config.*` |

### ultinous.service.kafka.detection.filter.auth.defs.file

| Property      | ultinous.service.kafka.detection.filter.auth.defs.file   |
| ------------- | ------------------------------------------------------ |
| Description   | Authentication definition file path. Content of the file should be in JSON format described described in [Superconfig Authentication Definitions].  |
| Required      | Optional   |
| Note          | Required if ID based authentication is used in `ultinous.service.kafka.detection.filter.ms.config.*` |

### ultinous.service.kafka.detection.filter.config.data

| Property      | ultinous.service.kafka.detection.filter.config.data   |
| ------------- | ------------------------------------------------------ |
| Description   | Detection filter configuration.   |
| Required      | Optional   |
| Note          | Required if `config_data` is not defined in `ultinous.service.kafka.detection.filter.ms.config.*`  |

### ultinous.service.kafka.detection.filter.config.file

| Property      | ultinous.service.kafka.detection.filter.config.file   |
| ------------- | ------------------------------------------------------ |
| Description   | Detection filter configuration.   |
| Required      | Optional   |
| Note          | Required if `config_data` is not defined in `ultinous.service.kafka.detection.filter.ms.config.*`  |

### ultinous.service.kafka.detection.filter.monitoring.port

| Property      | ultinous.service.kafka.detection.filter.monitoring.port   |
| ------------- | ------------------------------------------------------ |
| Description   | Monitoring server port.   |
| Required      | Required   |

### ultinous.service.kafka.detection.filter.monitoring.threads

| Property      | ultinous.service.kafka.detection.filter.monitoring.threads   |
| ------------- | ------------------------------------------------------ |
| Description   | Monitoring server thread pool size.   |
| Required      | Optional   |

## Record Schemas

Configuration records are separated into the following three values:

* `DetectionFilterMSConfig` specified in [Kafka Superconfiguration Proto]
* `DetectionFilterConfigRecord` specified in [Kafka Configuration Proto]
* `AuthDef` specified in [Kafka Superconfiguration Droto]
* `ObjectDetectionRecord` specified in [Kafka Data Proto].

### Example of a DetectionFilterConfigRecord from Kafka


```
{
  "min_confidence": 0.699999988079071,
  "detection_types": [
    "PERSON_HEAD"
  ],
  "negative_areas": [
    {
      "vertices": [
        {
          "x": 800,
          "y": 600
        },
        {
          "x": 1060,
          "y": 600
        },
        {
          "x": 1100,
          "y": 620
        },
        {
          "x": 900,
          "y": 620
        },
        {
          "x": 970,
          "y": 610
        }
      ]
    }
  ],
  "positive_areas": [
    {
      "vertices": [
        {
          "x": 1185,
          "y": 593
        },
        {
          "x": 1185,
          "y": 625
        },
        {
          "x": 1000,
          "y": 625
        },
        {
          "x": 1000,
          "y": 593
        }
      ]
    }
  ]
}

```

In this example the `min_confidence` field contains information on the confidence
value. The `detection_types` field specifies that only head detections are valid.
The `negative_areas` and `positive_areas` fields define the filtered areas.

### Example Configuration

```
{
  "source_options": {},
  "source": {
    "broker_list": "127.0.0.1:64997",
    "name": "OutputTopicsForTest.OUT1.ObjectDetectionRecord.json"
  },
  "target_options": {
    "handling": "REPLACE"
  },
  "target": {
    "broker_list": "127.0.0.1:64997",
    "name": "OutputTopicsForTest.OUT2.ObjectDetectionRecord.json"
  },
  "config_data": {
    "min_confidence": 0.699999988079071,
    "positive_areas": [
      {
        "vertices": [
          {
            "x": 1185,
            "y": 593
          },
          {
            "x": 1185,
            "y": 625
          },
          {
            "x": 1000,
            "y": 625
          },
          {
            "x": 1000,
            "y": 593
          }
        ]
      }
    ]
  }
}
```



[Example of a DetectionFilterConfigRecord from Kafka]: #example-of-a-detectionfilterconfigrecord-from-kafka
[Kafka Superconfiguration Proto]: ../../proto_files/ultinous/proto/common/kafka_superconfig.proto
[Kafka Configuration Proto]: ../../proto_files/ultinous/proto/common/kafka_config.proto
[Kafka Data Proto]: ../../proto_files/ultinous/proto/common/kafka_data.proto
[Superconfig Authentication Definitions]: conf_superconfig.md#authentication-definition
[Superconfig Topic Definitions]: conf_superconfig.md#topic-definitions







