#!/bin/sh

set -eu

docker_binary_path="$(which docker)"
docker_json_path="${HOME}/.docker/config.json"
nvidia_docker_binary_path="$(which nvidia-docker)"

# process given arguments
while test "${#}" -gt 0; do
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
		--models-directory)
			shift
			models_directory="${1}"
		;;
		--license-data-file-path)
			shift
			license_data_file_path="${1}"
		;;
		--license-key-file-path)
			shift
			license_key_file_path="${1}"
		;;
    --image-tag)
			shift
			image_tag="${1}"
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
if test -z "${docker_binary_path:-}"; then
    echo "docker-binary-path is unset! Override with --docker-binary-path"
    exit 1
elif test ! -f "${docker_binary_path}"; then
    echo "${docker_binary_path} not found! Override with --docker-binary-path"
    exit 1
elif test -z "${nvidia_docker_binary_path:-}"; then
    echo "nvidia-docker-binary-path is unset! Override with --nvidia-docker-binary-path"
    exit 1
elif test ! -f "${nvidia_docker_binary_path}"; then
    echo "${nvidia_docker_binary_path} not found! Override with --nvidia-docker-binary-path"
    exit 1
elif test -z "${docker_json_path:-}"; then
    echo "docker-json-path is unset! Override with --docker-json-path"
    exit 1
elif test ! -f "${docker_json_path}"; then
    echo "${docker_json_path} not found! Override with --docker-json-path"
    exit 1
elif test -z "${models_directory:-}"; then
    echo "models-directory is unset! Override with --models-directory"
    exit 1
elif test ! -d "${models_directory}"; then
    echo "${models_directory} not found! Override with --models-directory"
    exit 1
elif test -z "${license_data_file_path:-}"; then
    echo "license-data-file-path is unset! Override with --license-data-file-path"
    exit 1
elif test ! -f "${license_data_file_path}"; then
    echo "${license_data_file_path} not found! Override with --license-data-file_path"
    exit 1
elif test -z "${license_key_file_path:-}"; then
    echo "license-key-file-path is unset! Override with --license-key-file-path"
    exit 1
elif test ! -f "${license_key_file_path}"; then
    echo "${license_key_file_path} not found! Override with --license-key-file_path"
    exit 1
fi


if test -z "${image_tag:-}"; then
  image_tag="ultinous/uvap:mgr_$(git -C "$(dirname "$(realpath "${0}")")" tag --list --sort=-creatordate --merged HEAD 'release/*' | head -n1 | cut -f2 -d/)"
  if test -z "${image_tag:-}"; then
    echo "finding image tag was failed"
    exit 1
  fi
fi

${docker_binary_path} pull ${image_tag}
mgr_property_file_path="/ultinous_app/models/uvap-mgr/uvap_mgr.properties"

user_id="$(id -u)"
docker rm --force "uvap_mgr" 2> /dev/null || true
# run image
${nvidia_docker_binary_path} run \
    --name "uvap_mgr" \
    --detach \
    --user "${user_id}" \
    --env MGR_PROPERTY_FILE_PATHS="${mgr_property_file_path}" \
    --mount "type=bind,readonly,source=$(realpath "${models_directory}"),destination=/ultinous_app/models/" \
    --mount "type=bind,readonly,source=$(realpath "${license_data_file_path}"),destination=/ultinous_app/license_data.txt" \
    --mount "type=bind,readonly,source=$(realpath "${license_key_file_path}"),destination=/ultinous_app/licence.key" \
    ${@} \
    ${image_tag}
