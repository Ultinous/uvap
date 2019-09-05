# KAFKA Superconfig
The overall general integration configuration settings of Kafka UVAP microservices.
## Table of contents
1. [Configuration](#configuration)
    1. [Authentication definition](#authDefs)
1. [Topic definitions](#topicDefs)
    1. [Source Topic Options](#sourceOptions)
    1. [Source Topic Configs](#sourceConfigs)
    1. [Target Topic Options](#targetOptions)  
    1. [Target Topic Configs](#targetConfigs)  
1. [Examples](#examples)

<a name="authDefs"></a>
## Authentication definition
Optional authentication definitions of source and target topic brokers.
The definitions should contain the broker id, user name and password in JSON format. 
  - `auth_defs`: list of authentication definition data.
    - `id`: Authentication definition unique id.
    - `user_name`: The SASL authentication username.
    - `password`: The SASL authentication password.
<a name="topicDefs"></a>
## Topic definitions
<a name="sourceOptions"></a>
### Source topic options
  - `source_options`
    - `consumer_group`: Kafka consumer group. If left empty a UUID will be generated.
    - `start`: Defines the record position where Kafka starts reading from the topic.  
      Available values:
        - `START_BEGIN`: Start from the first record.
        - `START_DATETIME`: Start from a specific timestamp.          
        - `START_NOW`: Start from the current timestamp.
      - `START_END`: Start at the end of the records.
    - `start_date_time`: Must only be set if `start` is set to `START_DATETIME`.  
    Starts reading from the set timestamp defined in ISO-8601 format (opt. millisec and tz)  
    Example: `2019-04-08 10:10:24.123 +01:00`
    - `end`: Defines the record position where Kafka stops reading.  
      Available values:
        - `END_NEVER`: The microservice will not stop after the last record has been processed, will wait for new input records.
        - `END_DATETIME`: Ends at a specific timestamp.
        - `END_END`: The microservice stops after processing the last source record
    - `end_date_time`: Must only be set if `end` is set to `END_DATETIME`.  
    Ends reading at reaching a specific timestamp defined in ISO-8601 format (opt. millisec and tz)  
    Example: `2019-04-08 10:10:24.123 +01:00`
<a name="sourceConfigs"></a>
### Source topic configs
  - `sources`: Configuration of input topic brokers.  
    - `broker_list`: Source broker address and port.
    - `name`: [Source topic name](../../developers_guide.md#topicNamingConvention).
    - `auth_ref`: Optional authentication definition id. Exclusive to `user_name` and `password`.
    - `user_name`: Optional SASL authentication username of the source.
    - `password`: Optional SASL authentication password of the source.
<a name="targetOptions"></a>
### Target topic options
  - `target_options`
    - `handling`: Defines the target topic behaviour.  
    Available values:
      - `REPLACE`: Delete target topic.
      - `CHECK_TS`: Raise error if topic exists with more recent *latest timestamp*.
      - `SKIP_TS`: Skip events up to the latest timestamp in target topic.
<a name="targetConfigs"></a>
### Target topic configs
  - `target`: Configuration of target topic brokers. 
    - `broker_list`: Target broker address and port.
    - `name`: [Target topic name](../../developers_guide.md#topicNamingConvention).
    - `auth_ref`: Optional authentication definition id. Exclusive to `user_name` and `password`.
    - `user_name`: Optional SASL authentication username of the target.
    - `password`: Optional SASL authentication password of the target.

## Examples 
### Authentication Definitions
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
Two authentication definitions are configured. The first one is used for the source broker connections, while the second one is not used in this example.
### Example Microservice Configuration
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
The sources were set to be read from the given date and never stop reading them. 
Two feature vector sources are defined with broker list and name, using the predefined authentication parameters. 
The target stream is being replaced and can be accessed without any authentication.
