#!/bin/sh

set -eu

docker_binary_path="$(which docker)"
docker_json_path="${HOME}/.docker/config.json"

while test "${#}" -gt 0 ; do
	case "${1}" in
		--docker-binary-path)
			shift
			docker_binary_path="${1}"
		;;
		--docker-json-path)
			shift
			docker_json_path="${1}"
		;;
		*)
			echo "ERROR: unrecognized option: ${1}"
			exit 1
		;;
	esac
	shift
done

if test -z "${docker_binary_path:-}"; then
	echo "docker-binary-path is unset! Specify with --docker-binary-path"
	exit 1
elif test ! -f "${docker_binary_path}"; then
	echo "${docker_binary_path} not found! Override with --docker-binary-path"
	exit 1
elif test -z "${docker_json_path:-}"; then
	echo "docker-json-path is unset! Specify with --docker-json-path"
	exit 1
elif test ! -f "${docker_json_path}"; then
	echo "${docker_json_path} not found! Override with --docker-json-path"
	exit 1
fi

uvap_components_list_file_path="$(dirname "$(realpath "${0}")")/uvap_components_list.txt"
cat "${uvap_components_list_file_path}" > "/dev/null"

release_tag="$(git -C "$(dirname "$(realpath "${0}")")" tag --list --sort=-creatordate --merged HEAD 'release/*' | head -n1 | cut -f2 -d/)"
for component_name in $(cat "${uvap_components_list_file_path}"); do
    ${docker_binary_path} pull "ultinous/uvap:${component_name}_latest"
    ${docker_binary_path} pull "ultinous/uvap:${component_name}_${release_tag}"
done
