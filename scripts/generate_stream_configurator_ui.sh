#!/bin/bash

set -eu
source "$(dirname "$(realpath "$0")")/uvap_bash_functions"

current_directory="${current_directory}" # the above source declares it - this just clears IDE warnings
container_name="${container_name}" # the above source declares it - this just clears IDE warnings
set -a
config_ac_dir="${current_directory}/../config/${container_name}"
image_name="_auto_detected_"
output_ac_dir="${current_directory}/../ui/${container_name}"
set +a
parse_all_arguments "${@}"

parse_argument_with_value "config_ac_dir" "directory path of configuration files - default: ${config_ac_dir}"
parse_argument_with_value "image_name" "tag of docker image to use - default: will be determined by git tags"
parse_argument_with_value "output_ac_dir" "output directory path of the generated files - default: ${output_ac_dir}"
validate_remaining_cli_arguments

not_our_args+=("--rm" "--mount" "type=bind,source=${output_ac_dir},destination=/output" "--mount" "type=bind,source=${config_ac_dir},destination=/ultinous_app/${container_name}")

docker_container_run "--target-directory" "/output" "--properties-file" "/ultinous_app/${container_name}/${container_name}.properties"
