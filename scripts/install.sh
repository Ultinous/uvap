#!/bin/sh

set -eu

docker_binary_path="$(which docker)"
docker_json_path="${HOME}/.docker/config.json"
nvidia_docker_binary_path="$(which nvidia-docker)"

while [ $# -gt 0 ]; do
        case "${1}" in
                --docker-binary-path)
                        shift
                        docker_binary_path="${1}"
                ;;
                --docker-json-path)
                        shift
                        docker_json_path="${1}"
                ;;
                --nvidia-docker-binary-path)
                        shift
                        nvidia_docker_binary_path="${1}"
                ;;
                --download-url)
                        shift
                        download_url="${1}"
                ;;
                --stream-url)
                        shift
                        stream_url="${1}"
                ;;
                --configuration-directory)
                        shift
                        configuration_directory="${1}"
                ;;
                *)
                        echo "ERROR: unrecognized option: ${1}"
                        exit 1
                ;;
        esac
        shift
done

if [ -z ${docker_binary_path:-} ]; then
        echo "docker-binary-path is unset! Override with --docker-binary-path"
        exit 1
elif [ ! -f "${docker_binary_path}" ]; then
        echo "${docker_binary_path} not found! Override with --docker-binary-path"
        exit 1
elif [ -z ${nvidia_docker_binary_path:-} ]; then
        echo "nvidia-docker-binary-path is unset! Override with --nvidia-docker-binary-path"
        exit 1
elif [ ! -f "${nvidia_docker_binary_path}" ]; then
        echo "${nvidia_docker_binary_path} not found! Override with --nvidia-docker-binary-path"
        exit 1
elif [ -z ${docker_json_path:-} ]; then
        echo "docker-json-path is unset! Override with --docker-json-path"
        exit 1
elif [ ! -f "${docker_json_path}" ]; then
        echo "${docker_json_path} not found! Override with --docker-json-path"
        exit 1
elif [ -z ${download_url:-} ]; then
        echo "download-url is unset! Override with --download-url"
        exit 1
elif [ -z ${stream_url:-} ]; then
        echo "stream-url is unset! Override with --stream-url"
        exit 1
elif [ -z ${configuration_directory:-} ]; then
        echo "configuration-directory is unset! Override with --configuration-directory"
        exit 1
elif [ ! -d "${configuration_directory}" ]; then
        mkdir "${configuration_directory}"
fi

${docker_binary_path} pull ultinous/mgr_sdk
mkdir -p "${configuration_directory}/models/mgr-sdk/"
cd "${configuration_directory}"
wget -O - "${download_url}" | tar xf -
cd ..
cp "${configuration_directory}/models/templates/multi-graph-runner_sdk_template.prototxt" \
"${configuration_directory}/models/mgr-sdk/multi-graph-runner_sdk.prototxt"

sed -i 's|engines_file.*|engines_file: "/ultinous_app/models/engines/basic_detections.prototxt"|' \
"${configuration_directory}/models/mgr-sdk/multi-graph-runner_sdk.prototxt"

sed -i 's|$KAFKA_BROKER_LIST|kafka|' \
"${configuration_directory}/models/mgr-sdk/multi-graph-runner_sdk.prototxt"

sed -i 's|$KAFKA_TOPIC_PREFIX|mgr|' \
"${configuration_directory}/models/mgr-sdk/multi-graph-runner_sdk.prototxt"

sed -i "s|\$INPUT_STREAM|${stream_url}|" \
"${configuration_directory}/models/mgr-sdk/multi-graph-runner_sdk.prototxt"
