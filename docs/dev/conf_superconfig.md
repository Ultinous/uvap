---
id: conf_superconfig
title: Microservice Superconfiguration
hide_title: true
---

# Microservice Superconfiguration

This document introduces overall general integration configuration settings of the
UVAP microservices.

## Authentication Definition

The following are optional authentication definitions of source and target topic brokers. The definitions contain the broker ID, user name and password in JSON format.

| `auth_defs` | List of authentication definition data |
|--|--|
| `id` | Authentication definition unique ID. |
| `user_name` | The SASL authentication username. |
| `password` | The SASL authentication password. |

## Topic Definitions

### Source Topic Options

The following `source_options` are available:


| `consumer_group` |Kafka consumer group. If left empty a UUID will be generated. |
|--|--|

| `start` | Defines the record position where Kafka starts reading from the topic. |
|--|--|
| `START_BEGIN` | Start from the first record. |
| `START_DATETIME` | Start from a specific timestamp. |
| `START_NOW` | Start from the current timestamp. |
| `START_END` | Start at the end of the records. |

| `start_date_time` | Starts reading from the set timestamp defined in ISO-8601 format (milliseconds and time zone are optional). Only records with equal or later timestamps are processed. |
|--|--|

>**Note:**  
Set `start_date_time` only if `start` is set to `START_DATETIME`.  
For example: `2019-04-08 10:10:24.123 +01:00`


| `end` | Defines the record position where Kafka stops reading. |
|--|--|
| `END_NEVER` | The microservice does not stop after the last record is processed, instead it waits for new input records. |
| `END_DATETIME` | Ends at a specific timestamp. |
| `END_END` | The microservice stops after processing the last source record. |

| `end_date_time` |  Ends reading at reaching a specific timestamp defined in ISO-8601 format (milliseconds and time zone are optional). Only records with earlier timestamps are processed. |
|--|--|

>**Note:**
Set `end_date_time` only if `end` is set to `END_DATETIME`.  
For example: `2019-04-08 10:10:24.123 +01:00`
	
### Source Topic Configs

| `sources` | Configuration of input topic brokers. |
|--|--|
| `broker_list` | Source broker address and port. |
| `name` | See [Topic Naming Convention]. |
| `auth_ref` | Optional authentication definition id. Exclusive to `user_name` and `password`. |
| `user_name` | Optional SASL authentication username of the source. |
| `password` | Optional SASL authentication password of the source. |

### Target Topic Options

The following `target_options` are available.

| `handling` | Defines the target topic behaviour. |
|--|--|
| `REPLACE` | Delete target topic.|
| `CHECK_TS` | Raise an error if the topic exists with a newer <b>latest timestamp</b>. |
| `SKIP_TS` | Skip events up to the latest timestamp in the target topic. |

### Target Topic Configs


| `target` | Configuration of target topic brokers. |
|--|--|
| `broker_list` | Target broker address and port. |
| `name` | See [Topic Naming Convention]. |
| `auth_ref` | Optional authentication definition id. Exclusive to `user_name` and `password`. |
| `user_name` | Optional SASL authentication username of the target. |
| `password` | Optional SASL authentication password of the target. |

## Examples 

### Authentication Definitions

Two authentication definitions are configured. The first one is used for the
source broker connections, while the second one is not used in this example.

```
{
  "authDefs":
  [
    {
      "id":"srcAuth", 
      "user_name":"user1",
      "password:"srcPasswd"
    }, 
    {
      "id":"dstAuth",
      "user_name":"user2",
      "password":"dstPasswd"
    }
  ]
}
```

### Example Microservice Configuration

The sources are set to be read from the given date and never stop being read.
Two feature vector sources are defined with broker list and name, using the
predefined authentication parameters.
The target stream is being replaced and can be accessed without any authentication.

```
{
  "source_options":
  {
    "start":"START_DATETIME",
    "start_date_time": "2019-05-31T10:30:00.000 +02:00"
    "end":"END_NEVER",
    "consumer_group":"hardwareStore"
  },
  "sources":
  [  
    {
      "broker_list":"demoserver:9092",
      "name":"staff.FeatureVectorRecord.json",
      "auth_ref":"srcAuth"
    }
    {
      "broker_list":"demoserver:9092",
      "name":"cam.entrance.FeatureVectorRecord.json",
      "auth_ref":"srcAuth"
    },
    {
      "broker_list":"demoserver:9092",
      "name":"cam.exit.FeatureVectorRecord.json",
      "user_name":"user1",
      "password":"srcPasswd"
    }    
  ],
  "target_options":
  {
    "handling":"REPLACE"
  },
  "target":
  {
    "broker_list":"localhost:9092",
    "name":"sample.ReidRecord.json",
  }
}
```

[Topic Naming Convention]: uvap_data_model.md#topic-naming-convention