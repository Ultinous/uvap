#!/bin/sh

set -eu

topics="$(docker exec kafka kafka-topics --list --zookeeper zookeeper:2181 | grep -F Image.jpg)"
echo "These topics will be changed: \n${topics}"
for topic in ${topics}; do
    topic=$(echo -n "${topic}" | sed -r "s/\r//g")
    docker exec kafka kafka-configs --zookeeper zookeeper:2181 --alter --entity-type topics --entity-name "${topic}" --add-config retention.ms=900000
    docker exec kafka kafka-topics --describe --zookeeper zookeeper:2181 --topic "${topic}"
done
