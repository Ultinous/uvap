---
id: uvap_notations
title: Typographic Conventions
hide_title: true
---

# Typographic Conventions

## Code Blocs and Examples
Lines with monospace font starting with `$` (dollar) signs are to be executed.
The `$` (dollar) sign itself should not be copied into the terminal. For example:  
```
$ docker container inspect --format '{{.State.Status}}' uvap_kafka_reid
```

Lines starting with `something$` and `something#` are to be treated as
`$` lines, only the folllowing part should be copied. For example:  
```
<DOCKER># command-to-run
```
This means that the command should be run inside a Docker container.

Commands broken into multiple lines are denoted with a `\` (backslash) at the
end of each line. All such lines must be copied together.
There will be no `\` (backslash) at the end of the last line.
For example:
```
$ command-to-run argument1 argument2 \
  argument3 argument4
```

## UVAP Components

**Bold font** denotes UVAP microservices. For example:  
>**Reidentification** microservice processes feature vectors and finds reappearances.

_Italics font_ denotes UVAP features. For example:  
>The _Tracking_ feature is provided by the **Tracker** microservice.

**`Monospaced bold font`** denotes Kafka Topics. For example:  
>**Tracker** microservice uses the **`Head_Detections`** Kafka topic.
