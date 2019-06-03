#!/bin/sh

set -eu

docker_binary_path="$(which docker)"
docker_json_path="${HOME}/.docker/config.json"
nvidia_docker_binary_path="$(which nvidia-docker)"

# process given arguments
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
		--configuration-directory)
			shift
			configuration_directory="${1}"
		;;
		--license-data-file-path)
			shift
		license_data_file_path="${1}"
		;;
		--license-key-file-path)
			shift
		license_key_file_path="${1}"
		;;
		--)
			shift
			break
		;;
		*)
			echo "ERROR: unrecognized option: ${1}"
			exit 1
		;;
	esac
	shift
done

# check given arguments
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
elif [ -z ${configuration_directory:-} ]; then
	echo "configuration-directory is unset! Override with --configuration-directory"
	exit 1
elif [ ! -d "${configuration_directory}" ]; then
	echo "${configuration_directory} not found! Override with --configuration-directory"
	exit 1
elif [ -z ${license_data_file_path:-} ]; then
  echo "license-data-file-path is unset! Override with --license-data-file-path"
  exit 1
elif [ ! -f "${license_data_file_path}" ]; then
  echo "${license_data_file_path} not found! Override with --license-data-file_path"
  exit 1
elif [ -z ${license_key_file_path:-} ]; then
  echo "license-key-file-path is unset! Override with --license-key-file-path"
  exit 1
elif [ ! -f "${license_key_file_path}" ]; then
  echo "${license_key_file_path} not found! Override with --license-key-file_path"
  exit 1
fi

user_id="$(id -u)"
${docker_binary_path} pull ultinous/mgr_sdk
mgr_property_file_path="/ultinous_app/mgr.properties"

docker rm --force "mgr_sdk" 2> /dev/null || true

# run image
${nvidia_docker_binary_path} run \
	--name mgr_sdk \
	--detach \
	--user "${user_id}" \
	--env MGR_PROPERTY_FILE_PATHS="${mgr_property_file_path}" \
	--mount "type=bind,readonly,source=${configuration_directory}/models,destination=/ultinous_app/models/" \
	--mount "type=bind,readonly,source=${configuration_directory}/mgr.properties,destination=${mgr_property_file_path}" \
	--mount "type=bind,readonly,source=${license_data_file_path},destination=/ultinous_app/license_data.txt" \
	--mount "type=bind,readonly,source=${license_key_file_path},destination=/ultinous_app/licence.key" \
	${@} \
	ultinous/mgr_sdk
