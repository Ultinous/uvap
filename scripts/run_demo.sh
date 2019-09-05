#!/bin/bash

set -eu
source "$(dirname "$(realpath "$0")")/uvap_bash_functions"

current_directory="${current_directory}" # the above source declares it - this just clears IDE warnings
container_name="${container_name}" # the above source declares it - this just clears IDE warnings
set -a
config_file_name="_not_used_"
image_name="_auto_detected_"
demo_applications_dir="${current_directory}/../demo_applications"
set +a

parse_all_arguments "${@}"
parse_argument_with_value "demo_name" "the name of the demo to run - see the Quick Start Guide for details"
parse_argument_with_value "demo_mode" "<base|skeleton|fve>"
parse_argument_with_value "demo_applications_dir" "path of the demo applications scripts - default: ${demo_applications_dir}"
parse_argument_with_value "config_file_name" "path of configuration file - default:"
parse_argument_with_value "image_name" "tag of docker image to use - default: will be determined by git tags"
validate_remaining_cli_arguments

test_executable "docker"
test_executable "tar"

demo_name="${demo_name}" # parse_argument_with_value declares it - this just clears IDE warnings
demo_mode="${demo_mode}" # parse_argument_with_value declares it - this just clears IDE warnings
if ! [[ "${demo_mode}" =~ ^(base|skeleton|fve)$ ]]; then
	echo "ERROR: unrecognized demo mode: ${demo_mode}" >&2
	echo "ERROR: override with --demo-mode" >&2
	print_help
fi

if test "${image_name:-}" = "_auto_detected_"; then
	image_name="$(get_docker_image_tag_for_component uvap_demo_applications)"
fi

if test "${config_file_name:-}" != "_not_used_"; then
	config_file_in_container="/ultinous_app/models/$(basename "${config_file_name}")"
	mount_param="--mount type=bind,readonly,source=$(realpath "${config_file_name}"),destination=${config_file_in_container}"
fi

docker pull "${image_name}"
container_name="uvap_demo_applications"
test "$(docker container ls --filter name="${container_name}" --all --quiet | wc -l)" -eq 1 \
	&& docker container stop "${container_name}" > /dev/null \
	&& docker container rm "${container_name}" > /dev/null

docker container create \
	--name ${container_name} \
	--user="$(id -u)" \
	${mount_param:-} \
	"${not_our_args[@]/#/}" \
	"${image_name}" \
	/usr/bin/python3.6 "apps/uvap/${demo_name}_DEMO.py" --output kafka:9092 "${demo_mode}" ${config_file_in_container:-}

tar -c -C "${demo_applications_dir}" -h -f - . | docker container cp --archive - "${container_name}:/ultinous_app/"

docker container start ${container_name}
