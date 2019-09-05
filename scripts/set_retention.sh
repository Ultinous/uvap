#!/bin/bash

set -eu
source "$(dirname "$(realpath "$0")")/uvap_bash_functions"

current_directory="${current_directory}" # the above source declares it - this just clears IDE warnings

parse_all_arguments "${@}"
parse_argument_with_value "retention_unit" "<ms|second|minute|hour|day>"
parse_argument_with_value "retention_number" "a number that (together with the retention unit) defines the retention time to set"
validate_remaining_cli_arguments

test_executable "docker"

retention_unit="${retention_unit}" # parse_argument_with_value declares it - this just clears IDE warnings
retention_number="${retention_number}" # parse_argument_with_value declares it - this just clears IDE warnings

case "${retention_unit}" in
	"ms")
		retention_ms=$((retention_number))
	;;
	"second")
		retention_ms=$((retention_number * 1000))
	;;
	"minute")
		retention_ms=$((retention_number * 1000 * 60))
	;;
	"hour")
		retention_ms=$((retention_number * 1000 * 3600))
	;;
	"day")
		retention_ms=$((retention_number * 1000 * 3600 * 24))
	;;
	*)
		echo 'ERROR: invalid retention unit' >&2
		print_help
	;;
esac

topics="$(docker exec kafka kafka-topics --list --zookeeper zookeeper:2181 | grep -F Image.jpg)"
echo "INFO: These topics will be changed:
${topics}"

for topic in ${topics}; do
	topic=$(echo -n "${topic}" | sed -r "s/\r//g")
	docker exec kafka kafka-configs --zookeeper zookeeper:2181 --alter --entity-type topics --entity-name "${topic}" --add-config retention.ms=${retention_ms}
	docker exec kafka kafka-topics --describe --zookeeper zookeeper:2181 --topic "${topic}"
done
