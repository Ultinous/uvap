---
id: demo_web_player
title: Starting Web Player
hide_title: true
---

# Web Display

## Starting Web Player

1. Start the web player:

    > **Attention!**  
	Before starting this microservice, the command below silently stops and
	removes the Docker container named `uvap_web_player`, if such already exists.
    
	```
    $ "${UVAP_HOME}"/scripts/run_uvap_web_player.sh -- --net uvap
    ```
    
	The output of the above command should be:
    * some information about pulling the required Docker image
    * the ID of the Docker container created
    * the name of the Docker container created: `uvap_web_player`

    There are more optional parameters for the `run_uvap_web_player.sh`
    script to override defaults. Use the `--help` parameter to get more
    details.

1. Test status:

    a.) Check the log of the Docker container:
    
	```
    $ docker logs uvap_web_player
    ```
    
	Expected output example:  

    ```
    2019-07-16T10:38:12.043161Z INFO    [main]{com.ultinous.util.jmx.JmxUtil}(startConnectorServer/063) JMXConnectorServer listening on localhost:6666
    Jul 16, 2019 10:38:12 AM io.netty.handler.logging.LoggingHandler channelRegistered
    INFO: [id: 0xa3704b61] REGISTERED
    Jul 16, 2019 10:38:12 AM io.netty.handler.logging.LoggingHandler bind
    INFO: [id: 0xa3704b61] BIND: /0.0.0.0:9999
    Jul 16, 2019 10:38:12 AM io.netty.handler.logging.LoggingHandler channelActive
    INFO: [id: 0xa3704b61, L:/0:0:0:0:0:0:0:0%0:9999] ACTIVE
    2019-07-16T10:38:12.130916Z INFO    [main]{com.ultinous.uvap.web.player.MjpegPlayerServer}(start/075) Video Player listening on 0.0.0.0:9,999
    Jul 16, 2019 10:39:15 AM io.netty.handler.logging.LoggingHandler channelRead
    INFO: [id: 0xa3704b61, L:/0:0:0:0:0:0:0:0%0:9999] READ: [id: 0x9a81e318, L:/0:0:0:0:0:0:0:1%0:9999 - R:/0:0:0:0:0:0:0:1%0:59966]
    Jul 16, 2019 10:39:15 AM io.netty.handler.logging.LoggingHandler channelRead
    INFO: [id: 0xa3704b61, L:/0:0:0:0:0:0:0:0%0:9999] READ: [id: 0x56df1d95, L:/0:0:0:0:0:0:0:1%0:9999 - R:/0:0:0:0:0:0:0:1%0:59968]
    Jul 16, 2019 10:39:15 AM io.netty.handler.logging.LoggingHandler channelReadComplete
    INFO: [id: 0xa3704b61, L:/0:0:0:0:0:0:0:0%0:9999] READ COMPLETE
    ```

    b.) Check the service:
    
	```
    $ wget --save-headers --content-on-error --output-document=- \
      --show-progress=no --quiet 'http://localhost:9999/' | head -n1
    ```
    
	Expected output example:
    
	```
    HTTP/1.1 200 OK
    ```
 
## General Web Player Functions

### Live Image Display

The web player can play the live image sequence video of a Kafka topic. 

To play an image sequence, use the following link:

```
http://localhost:9999#[topic]
```

Where:
* `localhost` is the value of `com.ultinous.uvap.web.player.advertised.host`
* `9999` is the value of `com.ultinous.uvap.web.player.port`
* `[topic]` is the name of target topic from the
given Kafka broker (`com.ultinous.uvap.web.player.kafka.broker`)

### Listing Topics

A list of topics can be requested from the player server.

To request the topics, call the HTTP method `GET` with the following URL:

```
http://localhost:9999/topics
```
    
The content type of given response is `application/json`.
The content of response contains the list of available `image.josn` topics. 

### Display Historical Images

Historical images can also be viewed in the web player.

To request historical images, call the HTTP method `GET` with the following URL:
    
```
http://localhost:9999/single?topic=base.cam.0.head_detection.Image.jpg&timestamp=1570183573000
```

Where:
* `topic` is the name of target Kafka topic
* `timestamp` is the UTC timestamp

## UVAP Web Player Access from Client Machine

To use the web player from a client machine
(different from the processing node), modify
the default configuration of the web player:

1. Open the configuration file:
   
   ```  
   ~/uvap/config/uvap_web_player/uvap_web_player.properties
   ```
   
1. Modify the `com.ultinous.uvap.web.player.advertised.host` parameter to the 
   `<HOST_MACHINE_IP>` (default: `localhost`)
   
1. Restart web player with the following command:    
   
   ```
   $ docker restart uvap_web_player  
   ```  

> Attention!  
 `config.sh` overrides this configuration file.
