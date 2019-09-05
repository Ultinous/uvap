#!/bin/bash

set -eu
source "$(dirname "$(realpath "$0")")/uvap_bash_functions"

current_directory="${current_directory}" # the above source declares it - this just clears IDE warnings
container_name="${container_name}" # the above source declares it - this just clears IDE warnings
set -a
config_dir="${current_directory}/../config/${container_name}"
image_name="_auto_detected_"
set +a

parse_all_arguments "${@}"
parse_argument_with_value "config_dir" "directory path of configuration files - default: ${config_dir}"
parse_argument_with_value "image_name" "tag of docker image to use - default: will be determined by git tags"
validate_remaining_cli_arguments

docker_container_run
