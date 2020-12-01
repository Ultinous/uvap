#!/bin/bash

set -eu

# For both Zookeeper and Kafka containers do the following
for container_name in kafka zookeeper; do
	if test "$(docker container ls --filter name="^${container_name}\$" --all --quiet | wc -l)" -eq 1; then
		# Stop the container
		docker container stop "${container_name}" > /dev/null
		# Collect the volumes of the container
		docker container inspect --format '{{json .Mounts}}' "${container_name}" \
			| jq --raw-output '.[].Name' > /tmp/volumes_list.txt
		# Remove the container
		docker container rm "${container_name}"
		# Remove the volumes
		for volume in $(cat /tmp/volumes_list.txt); do
			docker volume rm ${volume}
		done
		rm /tmp/volumes_list.txt
	fi
done

# Start Zookeeper and Kafka containers
docker run --net=uvap -d --name=zookeeper \
	-e ZOOKEEPER_CLIENT_PORT=2181 ultinous/cp-zookeeper:5.4.0

docker run --net=uvap -d -p 9092:9092 --name=kafka \
	-e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 \
	-e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092 \
	-e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
	-e KAFKA_MESSAGE_MAX_BYTES=10485760 \
	-e ZOOKEEPER_CLIENT_PORT=2181 ultinous/cp-kafka:5.4.0
