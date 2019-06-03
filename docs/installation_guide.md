# Ultinous Video Analyitics Platform (UVAP) Installation Guide

This document describes the minimum hardware and software requirements to install the UVAP (Ultinous Video Analytics Platform) in a demo environment. This is a standalone installation without need to access anything remotely. However the installation requires internet access and access to some Ultinous repositories.

## Hardware requirements

The following table includes all the minimum necessary hardware requirements to be able to use the UVAP. The following configurations defines 3 different levels of performance which could be used for the testing.
You can choose if you would like to test with a USB or an IP camera, but you could also use a pre-recorded video stream from a file.

The test node can be even a laptop which contains the necessary components, like a strong gamer laptop with the necessary processor and GPU.

### Camera

| Camera type | Example |
| - | - |
| USB Camera | Logitech BRIO |
| IP Camera  | Hikvision IP camera with HD resolution |

### Server

#### Small node

| Part | Spec |
| - | - |
| CPU | Intel i5-6500 3200MHz |
| RAM | 8GB |
| Video card | NVIDIA GeForce GTX1060 |
| Disk | 500GB |

#### Medium node

| Part  | Spec |
| - | - |
| CPU | Intel Xeon E5-1650 3.6GHz |
| RAM | 16GB |
| Video card | NVIDIA GeForce GTX1080 |
| Disk | 500GB |

## Software requirements

The UVAP runs on Ubuntu Linux 18.04 LTS. The desktop edition is recommended, as it could be necessary to be able to play back videos or display pictures for checking the source stream or the results.
To install Ubuntu Linux 18.04 LTS on the node follow the installation tutorial: https://tutorials.ubuntu.com/tutorial/tutorial-install-ubuntu-desktop
The following components should be pre-installed to be able to install the UVAP on the node.

### Create New user for UVAP

1. Create a user called ultinous
```
$ sudo adduser ultinous
```
2. Add your user to the docker group and to the sudoer group
```
$ sudo addgroup ultinous docker
$ sudo addgroup ultinous sudo
```
3. Change user on graphical environment (log out and log in with ‘ultinous’ user)

### NVIDIA video driver

The SDK requires a specific GPU driver installed to run properly.
1. Add the graphics-drivers/ppa repository to the apt:
```
$ sudo add-apt-repository ppa:graphics-drivers/ppa
$ sudo apt update
```
2. Install the NVIDIA video driver
```
$ sudo apt install nvidia-driver-410
```
3. Reboot the node to use the new driver (and  log in with ‘ultinous’ user)

### Acquiring the license key

1. Collect the HW information for license generation
```
$ nvidia-smi -L | rev | cut -c2-37 | rev
```
2. Please send the output of the above command to your sales representative. Based on this information, you will receive two license files which are required to run the UVAP.

E.g.:
license.txt:
```
Product Name    = UVAP
GPU             = aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee
Expiration Date = 2018-01-01
Customer    	 = Demo User
```
licence.key:
```
--- No human readable key data ---
```

Without license files you can continue the installation process until the UVAP usage.

### Additional tools

There are some useful utilities which can be handy during the testing
- Vlc. Video playback application to test live stream or playback a pre-recorded file
```
$ sudo apt-get install vlc
```
- ffmpeg. A command line tool which can convert between different video formats and codecs
```
$ sudo apt-get install ffmpeg
```
- kafkacat. This command line tool can be used to dump kafka streams
```
$ sudo apt-get install kafkacat
```

### Docker
The UVAP uses a containerized solution provided by Docker. This also has to be extended with an nvidia driver related addon.

1. Install curl to be able to download files from command line
```
$ sudo apt install curl
```
2. Add docker source to the apt repositories
```
$ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
$ sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
$ sudo apt-get install docker-ce
```
3. Enable nvidia-persistenced to prevent the sleep state of the GPU (only on Server machine)
```
$ cd /etc/systemd/system/
$ sudo mkdir nvidia-persistenced.service.d
$ cd nvidia-persistenced.service.d/
$ cat | sudo tee override.conf <<EOF
[Service]
ExecStart=/usr/bin/nvidia-persistenced --user nvidia-persistenced --verbose
EOF
$ sudo systemctl daemon-reload
$ sudo systemctl restart nvidia-persistenced.service
```
4. Install NVIDIA docker
```
$ curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
$ distribution=$(. /etc/os-release; echo $ID$VERSION_ID)
$ curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
$ sudo apt-get update
$ sudo apt-get install nvidia-docker2
$ sudo systemctl restart docker
```
5. Test the docker environment
```
$ nvidia-docker run --rm nvidia/cuda:10.0-runtime-ubuntu18.04 nvidia-smi
```
You should see a similar output like the following:

```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 410.104      Driver Version: 410.104      CUDA Version: 10.0     |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|===============================+======================+======================|
|   0  GeForce GTX 106...  On   | 00000000:01:00.0 Off |                  N/A |
| N/A   47C    P8     5W /  N/A |    250MiB /  6078MiB |      6%      Default |
+-------------------------------+----------------------+----------------------+

+-----------------------------------------------------------------------------+
| Processes:                                                       GPU Memory |
|  GPU       PID   Type   Process name                             Usage      |
|=============================================================================|
+-----------------------------------------------------------------------------+
```

6. Log in to your docker account
You need to have an account on the hub.docker.com which has permission to pull the Ultinous SDK. This permission should be requested from your sales contact.
```
$ docker login
```
7. Pull the following docker images
```
$ docker pull ultinous/mgr_sdk
```

### Installing Zookeeper and Kafka

The UVAP provides several sample stream over Kafka where the integrator can connect to and implement some custom solution based on the stream coming out

1. Create a separate internal network for the dockerized environment
```
$ docker network create sdk
```
2. Install a Zookeeper container
```
$ docker run --net=sdk -d --name=zookeeper -e ZOOKEEPER_CLIENT_PORT=2181 --restart always confluentinc/cp-zookeeper:4.1.0
```
3. Install Kafka
```
$ docker run --net=sdk -d -p 9092:9092 --name=kafka -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092 -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 -e ZOOKEEPER_CLIENT_PORT=2181 confluentinc/cp-kafka:4.1.0
```
4. Wait for 30 seconds, then check if the containers are still running:
```
$ docker ps
CONTAINER ID        IMAGE                             COMMAND ...
8fb5f2fdce1a        confluentinc/cp-kafka:4.1.0       "/etc/confluent/dock…"...
0e15ea1ebb01        confluentinc/cp-zookeeper:4.1.0   "/etc/confluent/dock…"...
```
5. Edit your /etc/hosts file
```
$ sed -i 's/^127.0.0.1.*/127.0.0.1\tlocalhost zookeeper kafka/' /etc/hosts
```
6. Test your kafka configuration
 - Create a kafka topic
```
$ docker exec -it kafka /bin/bash -c 'kafka-topics --create --zookeeper zookeeper:2181 --replication-factor 1 --partitions 1 --topic test'
```
It should display:
```
Created topic "test".
```
 - Test the stream
```
$ docker exec -it kafka /bin/bash -c 'RND="${RANDOM}${RANDOM}${RANDOM}"; echo $RND | kafka-console-producer --broker-list localhost:9092 --topic test > /dev/null && kafka-console-consumer --bootstrap-server localhost:9092 --topic test --from-beginning --timeout-ms 1000 2> /dev/null | fgrep -q $RND; if [ $? -eq 0 ]; then echo OK; else echo ERROR; fi'
```
It should print “OK”



## Installing UVAP

### Download helper scripts

You have to download a few helper scripts which makes it easier to download and configure the UVAP related data files.
```
$ git clone https://github.com/Ultinous/sdk.git
```
You may check the README.md file for a brief overview of this repository.

### Install the UVAP data for RTSP stream
Before the next step you have to receive a download URL from your sales representative. This URL is valid only for a period of time. You have to use it in the following command replacing the `<DOWNLOAD_URL>` with the URL you get.
The `<RTSP_URL>` should be replaced with a URL which points to a valid RTSP stream, for example an IP camera. This should look like this: `rtsp://192.168.0.1/`
This URL also can contain username and password if the stream is protected, for example: `rtsp://username:password@192.168.0.1/`

Run the install script:
```
$ /home/ultinous/sdk/scripts/install.sh --download-url '<DOWNLOAD_URL>' --configuration-directory '/home/ultinous/config' --stream-url '<RTSP_URL>'
```
If you want to change stream url later just need to run this install script again.

Finally you have to start up the framework:
```
$ /home/ultinous/sdk/scripts/run.sh --configuration-directory '/home/ultinous/config' --license-data-file-path '<ABSOLUTE_FILE_PATH_OF_LICENSE_TXT_FILE>' --license-key-file-path '<ABSOLUTE_FILE_PATH_OF_LICENSE_KEY_FILE>' -- --net sdk
```
Check if the container is running:
```
$ docker ps -a
CONTAINER ID        IMAGE                             COMMAND                  
8fa8c7e07d81        ultinous/mgr_sdk                  "/bin/bash -c 'exec …"   
8fb5f2fdce1a        confluentinc/cp-kafka:4.1.0       "/etc/confluent/dock…"...
0e15ea1ebb01        confluentinc/cp-zookeeper:4.1.0   "/etc/confluent/dock…"...
```
If the status of mgr_sdk container is not running then send the output of the following command to your sales representative.
```
$ docker logs mgr_sdk
```
You can also manage these docker containers with standard docker commands.
Details: https://docs.docker.com/engine/reference/commandline/docker/

Check if the kafka topics are created:
```
$ docker exec -it kafka /bin/bash -c 'kafka-topics --list --zookeeper zookeeper:2181'
```
Try to fetch data from a kafka topic:
```
$ kafkacat -b zookeeper -t mgr.dets.ObjectDetectionRecord.json
```
The `‘mgr.lowres.Image.jpg’` topic required a huge storage, because it contains every frame image in JPG format. We can change the lifetime of topic, for example 15 minutes:
```
$ docker exec -it kafka /bin/bash -c ' kafka-configs --zookeeper zookeeper:2181 --alter --entity-type topics --entity-name mgr.lowres.Image.jpg --add-config retention.ms=900000’

Completed Updating config for entity: topic 'mgr.lowres.Image.jpg'.
```
Checker:
```
$ docker exec -it kafka /bin/bash -c ' kafka-topics --describe --zookeeper  zookeeper:2181 --topic mgr.lowres.Image.jpg’

Topic:mgr.lowres.Image.jpg    PartitionCount:1    ReplicationFactor:1    Configs:retention.ms=900000
    Topic: mgr.lowres.Image.jpg    Partition: 0    Leader: 0    Replicas: 0    Isr: 0
```
### Example of the UVAP usage
The following python code merge the image from the camera and the detection’s result (blue frame of heads) and show it on the window.
Requirements for python example
```
$ sudo apt install python3-pip
$ pip3 install numpy
$ pip3 install opencv-contrib-python
$ pip3 install confluent-kafka
```
Run python code
```
$ cd /home/ultinous/sdk/example
$ python3 example.py
```
