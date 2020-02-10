#!/bin/sh

set -eu

BROKER="${1}"
SRC_ID="${2}"
DST_ID="${3}"

docker exec kafka /bin/sh -c "kafka-console-consumer --bootstrap-server ${BROKER} --topic 'detected.records.json' --from-beginning --timeout-ms 10 --property print.key=true 2>/dev/null | \\
	sed -nE 's/^([0-9]+_[0-9]+)[[:space:]]${SRC_ID};$/\1:${DST_ID}/p' | \\
	tail -n1 | \\
	kafka-console-producer --broker-list ${BROKER} --topic 'named.records.json' --property 'parse.key=true' --property 'key.separator=:' >/dev/null"
