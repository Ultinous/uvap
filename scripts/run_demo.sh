#!/bin/bash

set -eu
source "$(dirname "$(realpath "$0")")/uvap_bash_functions"

current_directory="${current_directory}" # the above source declares it - this just clears IDE warnings
container_name="${container_name}" # the above source declares it - this just clears IDE warnings
set -a
config_file_name="_not_used_"
image_name="_auto_detected_"
demo_applications_dir="${current_directory}/../demo_applications"
extra_demo_flags="-o"
run_mode="background"
set +a

parse_all_arguments "${@}"
parse_argument_with_value "demo_name" "the name of the demo to run - see the Quick Start Guide for details"
parse_argument_with_value "demo_mode" "<base|skeleton|fve>"
parse_argument_with_value "demo_applications_dir" "path of the demo applications scripts - default: ${demo_applications_dir}"
parse_argument_with_value "config_file_name" "path of configuration file - default:"
parse_argument_with_value "extra_demo_flags" "extra demo flags (e.g.: -d, -o, -v) - default: -o"
parse_argument_with_value "image_name" "tag of docker image to use - default: will be determined by git tags"
parse_argument_with_value "run_mode" "<background|foreground> - default: ${run_mode}"
validate_remaining_cli_arguments

test_executable "docker"
test_executable "tar"

extra_demo_flags="${extra_demo_flags}" # parse_argument_with_value declares it - this just clears IDE warnings
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

x11_arguments=()
if echo "${extra_demo_flags}" | tr '-' '_' | grep -qF -e '_o' -e '__output'; then
	x11_arguments+=(\
		"--mount" "type=bind,readonly,source=/tmp/.X11-unix,destination=/tmp/.X11-unix" \
		"--env" "DISPLAY=${DISPLAY:-}" \
		"--env" "QT_X11_NO_MITSHM=1"
	)
fi

# TODO: if no symlinks found in demo_applications_dir, mount it.

docker container create \
	--name ${container_name} \
	--user="$(id -u)" \
	${mount_param:-} \
	"${x11_arguments[@]}" \
	"${not_our_args[@]/#/}" \
	"${image_name}" \
	python3.7 "apps/uvap/${demo_name}_DEMO.py" \
		kafka:9092 \
		"${demo_mode}" \
		${extra_demo_flags} \
		${config_file_in_container:-}

tar -c -C "${demo_applications_dir}" -h -f - . | docker container cp --archive - "${container_name}:/ultinous_app/"

docker container start $(test "${run_mode:-}" = "foreground" && echo "--attach") ${container_name}
