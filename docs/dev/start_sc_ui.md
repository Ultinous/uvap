---
id: start_sc
title: Starting Stream Configurator UI
hide_title: true
---

# Starting Stream Configurator UI

The Stream Configurator UI makes quick and easy passline configuration and
management possible.

## Setting Up Stream Configurator UI

To set up the Stream Configurator UI, run `config.sh` in base mode.  
This runs the `generate_stream_configurator_ui.sh` script with default settings,
intended to work with the default UVAP configuration.

The UI can be built with a custom configuration by directly calling
`generate_stream_configurator_ui.sh`. Use the provided parameters to specify the
output location and the Docker image used for the process.

### Running config.sh

>**Note:**  
For Stream Configurator UI to be built, the `-demo-mode` argument has to be set
to `base`.

Building the UI this way results in the followings:
- The properties file is read from `../config`.
- The UI is generated to location `../ui`.
- The Docker image used to generate the UI is determined automatically by Git tags.

The following arguments provided to `config.sh` can be used to configure the UI:

| Argument      | `--host-name`    |
| ------------- | ------------------------------------------------------ |
| Description   | Sets host name |
| Requirement   | Optional       |
| Default Value | `localhost`    |

| Argument      | `--web-player-port-number`    |
| ------------- | ------------------------------------------------------ |
| Description   | Sets port number |
| Requirement   | Optional       |
| Default Value | `9999`    |

### Running generate_stream_configurator_ui.sh

Stream Configurator UI can also be built by running `generate_stream_configurator_ui.sh`.

Use with the `--help` parameter to get more details.


## Starting Stream Configurator UI

### Prerequisites
To be able to display the video stream and topics, make sure the following
components are up and running:

>**Note**  
It is important that the components are started up in this order.

- [Kafka]
- [MGR]
- [Web Player]

To start the components:

1. Start Zookeper:

   ```
   docker run --net=uvap -d --name=zookeeper \
     -e ZOOKEEPER_CLIENT_PORT=2181 confluentinc/cp-zookeeper:4.1.0
   ```

2. Start Kafka:

   ```
   docker run --net=uvap -d -p 9092:9092 --name=kafka \
     -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 \
     -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092 \
     -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
     -e KAFKA_MESSAGE_MAX_BYTES=10485760 \
     -e ZOOKEEPER_CLIENT_PORT=2181 confluentinc/cp-kafka:4.1.0
   ```

3. Start **MGR**:

   ```
   "${UVAP_HOME}"/scripts/run_mgr.sh -- --net=uvap
   ```

4. Start Web player:

   ```
   "${UVAP_HOME}"/scripts/run_uvap_web_player.sh -- --net uvap
   ```

### Starting the UI

Only Google Chrome™ version 76 and later is supported.

1. Google Chrome™ version check:

   ```
   $ google-chrome --version
   ```
1. Google Chrome™ install process:

   ```
   $ wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
   $ sudo dpkg -i google-chrome-stable_current_amd64.deb
   ```

1. Stream Configurator UI can be started by opening in a web browser:
    
   ```
    $ google-chrome ${UVAP_HOME}/ui/uvap_stream_configurator_ui/index.html
   ```

See the [Stream Configurator UI Guide] for further information on the settings
and usage of the Stream Configurator UI.

[Kafka]: ../install/uvap_install_setup.md#starting-kafka
[MGR]: start_mgr.md
[Web Player]: ../demo/demo_web_player.md
[Stream Configurator UI Guide]: conf_sc_ui.md
[Zookeper]: ../install/uvap_install_setup.md#starting-kafka
