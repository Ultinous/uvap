#!/bin/sh

set -eu

current_directory="$(dirname "$(realpath ${0})")"
drop_rate=0

while test "${#}" -gt 0 ; do
	case "${1}" in
		--drop-rate)
			shift
			drop_rate="${1}"
		;;
		--demo-mode)
			shift
			demo_mode="${1}"
		;;
		--stream-url)
			shift
			stream_url="${1}"
		;;
		--models-directory)
			shift
			models_directory="${1}"
		;;
		*)
			echo "ERROR: unrecognized option: ${1}"
			exit 1
		;;
	esac
	shift
done

if test -z "${stream_url:-}"; then
	echo "stream-url is unset! Specify with --stream-url"
	exit 1
elif test -z "${models_directory:-}"; then
	echo "models-directory is unset! Specify with --models-directory"
	exit 1
elif test ! -d "${models_directory}"; then
	echo "${models_directory} does not exist! Override with --models-directory"
	exit 1
elif test -z "${demo_mode:-}"; then
	echo "demo_mode is unset! Choose one from: [base, skeleton] Specify with --demo-mode"
	exit 1
elif test -z "${drop_rate:-}"; then
	drop_rate = 1
fi

mkdir -p "${models_directory}/uvap-mgr/"

export ENGINES_FILE="/ultinous_app/models/engines/basic_detections.prototxt"
export KAFKA_BROKER_LIST="kafka"
export KAFKA_TOPIC_PREFIX="${demo_mode}"
export INPUT_STREAM="${stream_url}"
export DROP_RATE=${drop_rate}

cp -a "${current_directory}/../templates/uvap_mgr_TEMPLATE.properties" \
	"${models_directory}/uvap-mgr/uvap_mgr.properties"
envsubst < "${current_directory}/../templates/uvap_mgr_${demo_mode}_TEMPLATE.prototxt" \
	> "${models_directory}/uvap-mgr/multi-graph-runner.prototxt"
