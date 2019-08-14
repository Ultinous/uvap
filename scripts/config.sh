#!/bin/bash

set -eu

docker_binary_path="$(which docker)"
current_directory="$(dirname "$(realpath "${0}")")"
demo_applications_directory=$HOME/uvap/demo_applications
templates_directory=$HOME/uvap/templates
keep_rate=1
stream_urls=()

while test "${#}" -gt 0 ; do
	case "${1}" in
	  --docker-binary-path)
  		shift
  		docker_binary_path="${1}"
  	;;
		--keep-rate)
			shift
			keep_rate="${1}"
		;;
		--demo-mode)
			shift
			demo_mode="${1}"
		;;
		--stream-url)
			shift
			stream_urls+=("${1}")
		;;
		--demo-applications-directory)
			shift
			demo_applications_directory="${1}"
		;;
		--templates-directory)
			shift
			templates_directory="${1}"
		;;
		--models-directory)
			shift
			models_directory="${1}"
		;;
		--image-name)
			shift
			image_name="${1}"
		;;
		*)
			echo "ERROR: unrecognized option: ${1}"
			exit 1
		;;
	esac
	shift
done

if test -z "${docker_binary_path:-}"; then
    echo "docker-binary-path is unset! Override with --docker-binary-path"
    exit 1
elif test ! -f "${docker_binary_path}"; then
    echo "${docker_binary_path} not found! Override with --docker-binary-path"
    exit 1
elif test -z "${stream_urls:-}"; then
	echo "stream-url is unset! Specify with --stream-url"
	exit 1
elif test -z "${demo_applications_directory:-}"; then
	echo "models-directory is unset! Specify with --demo-applications-directory"
	exit 1
elif test ! -d "${demo_applications_directory}"; then
	echo "${demo_applications_directory} does not exist! Override with --demo-applications-directory"
	exit 1
elif test -z "${templates_directory:-}"; then
	echo "models-directory is unset! Specify with --templates-directory"
	exit 1
elif test ! -d "${templates_directory}"; then
	echo "${templates_directory} does not exist! Override with --templates-directory"
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
elif ! [ "${keep_rate}" -eq "${keep_rate}" ];then
	echo "${keep_rate} is not a number"
	exit 1
fi

mkdir -p "${models_directory}/uvap-mgr/"
mkdir -p "${models_directory}/uvap-kafka-tracker/"
mkdir -p "${models_directory}/uvap-web_player/"
mkdir -p "${models_directory}/uvap-kafka-passdet/"

cp -a "${current_directory}/../templates/uvap_mgr.properties"        "${models_directory}/uvap-mgr/uvap_mgr.properties"
cp -a "${current_directory}/../templates/uvap_web_player.properties" "${models_directory}/uvap-web_player/uvap_web_player.properties"

# find latest release git hash if not set
if test -z "${image_name:-}"; then
  image_tag="$(git -C "$(dirname "$(realpath "${0}")")" tag --list --sort=-creatordate --merged HEAD 'release/*' | head -n1 | cut -f2 -d/)"
  echo ${image_tag}
  if test -z "${image_tag:-}"; then
    echo "finding image tag was failed"
    exit 1
  fi
  image_name="ultinous/uvap:uvap_demo_applications_${image_tag}"
fi

${docker_binary_path} pull ${image_name}

jinja_yaml_param_file_path="${models_directory}/params.yaml"

echo "\
ENGINES_FILE: /ultinous_app/models/engines/basic_detections.prototxt
KAFKA_BROKER_LIST: kafka
KAFKA_TOPIC_PREFIX: ${demo_mode}
INPUT_STREAMS:" > ${jinja_yaml_param_file_path}

for ELEMENT in ${stream_urls[@]}
do
echo "  - $ELEMENT" >> ${jinja_yaml_param_file_path}
done

echo "\
DROP_RATE: ${keep_rate}
" >> ${jinja_yaml_param_file_path}

MOUNTED_MODEL_DIR="/models"
MOUNTED_TEMPLATES_DIR="/templates"

JINJA_RUN="/usr/bin/python3.6 apps/uvap/run_jinja.py ${MOUNTED_MODEL_DIR}/params.yaml"

if [ "${demo_mode}" == "base" ]; then
JINJA_RUN_SCRIPT="
  ${JINJA_RUN} ${MOUNTED_TEMPLATES_DIR}/uvap_mgr_${demo_mode}_TEMPLATE.prototxt             ${MOUNTED_MODEL_DIR}/uvap-mgr/multi-graph-runner.prototxt
  ${JINJA_RUN} ${MOUNTED_TEMPLATES_DIR}/uvap_kafka_tracker_${demo_mode}_TEMPLATE.properties ${MOUNTED_MODEL_DIR}/uvap-kafka-tracker/uvap_kafka_tracker.properties
  ${JINJA_RUN} ${MOUNTED_TEMPLATES_DIR}/uvap_kafka_passdet_TEMPLATE.properties              ${MOUNTED_MODEL_DIR}/uvap-kafka-passdet/uvap_kafka_passdet.properties
"
elif [ "${demo_mode}" == "skeleton" ]; then
JINJA_RUN_SCRIPT="
  ${JINJA_RUN} ${MOUNTED_TEMPLATES_DIR}/uvap_mgr_${demo_mode}_TEMPLATE.prototxt             ${MOUNTED_MODEL_DIR}/uvap-mgr/multi-graph-runner.prototxt
"
fi


${docker_binary_path}  run \
    --rm \
    --interactive \
    --mount "type=bind,readonly,source=$(realpath "${demo_applications_directory}"),destination=/ultinous_app/" \
    --mount "type=bind,readonly,source=$(realpath "${templates_directory}"),destination=${MOUNTED_TEMPLATES_DIR}" \
    --mount "type=bind,source=$(realpath "${models_directory}"),destination=${MOUNTED_MODEL_DIR}" \
    --net=uvap \
    ${image_name} \
    /bin/bash \
    -c \
    "$JINJA_RUN_SCRIPT"
