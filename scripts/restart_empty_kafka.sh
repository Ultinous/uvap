#!/bin/bash

set -eu

# Stop Zookeeper and Kafka containers
docker container stop zookeeper kafka

# Collect docker volumes
docker container inspect --format '{{json .Mounts}}' kafka zookeeper \
	| jq --raw-output '.[].Name' > /tmp/kafka_volumes_list.txt

# Remove Zookeeper and Kafka containers
docker container rm zookeeper kafka

# Remove docker volumes
for volume in $(cat /tmp/kafka_volumes_list.txt); do
	docker volume rm ${volume}
done
rm /tmp/kafka_volumes_list.txt

# Start Zookeeper and Kafka containers
docker run --net=uvap -d --name=zookeeper \
	-e ZOOKEEPER_CLIENT_PORT=2181 confluentinc/cp-zookeeper:4.1.0

docker run --net=uvap -d -p 9092:9092 --name=kafka \
	-e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 \
	-e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092 \
	-e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
	-e KAFKA_MESSAGE_MAX_BYTES=10485760 \
	-e ZOOKEEPER_CLIENT_PORT=2181 confluentinc/cp-kafka:4.1.0
