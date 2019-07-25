#!/bin/sh

set -eu

usage() {
	echo "usage: $0 (--retention-ms|--retention-minute|--retention-second|--retention-hour|--retention-day) number"
	exit 1
}

if ! [ -z  ${1:-} ]; then
	    if ! [ ${2?"parameter 2 is not defined"} -eq ${2} ];then
	      echo "${2} is not a number"
	      usage
	    fi
fi
while test "${#}" -gt 0 ; do
    case "${1}" in
	--retention-ms)
	    shift
	    retention_ms="${1}"
	;;
	--retention-second)
	    shift
	    retention_ms=$(( ${1} * 1000 ))
	;;
	--retention-minute)
	    shift
	    retention_ms=$(( ${1} * 60000 ))
	;;
	--retention-hour)
	    shift
	    retention_ms=$(( ${1} * 60000 * 60 ))
	;;
	--retention-day)
	    shift
	    retention_ms=$(( ${1} * 60000 * 60 * 24 ))
	;;
	*)
	    echo "ERROR: unrecognized option: ${1}"
	    usage
	;;
    esac
    shift
done

if test -z "${retention_ms:-}"; then
    echo "The retention time is unset!"
    usage
fi


topics="$(docker exec kafka kafka-topics --list --zookeeper zookeeper:2181 | grep -F Image.jpg)"
echo "These topics will be changed: \n${topics}"
for topic in ${topics}; do
    topic=$(echo -n "${topic}" | sed -r "s/\r//g")
    docker exec kafka kafka-configs --zookeeper zookeeper:2181 --alter --entity-type topics --entity-name "${topic}" --add-config retention.ms=${retention_ms}
    docker exec kafka kafka-topics --describe --zookeeper zookeeper:2181 --topic "${topic}"
done
