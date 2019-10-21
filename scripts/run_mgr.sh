#!/bin/bash

set -eu
source "$(dirname "$(realpath "$0")")/uvap_bash_functions"

current_directory="${current_directory}" # the above source declares it - this just clears IDE warnings
container_name="${container_name}" # the above source declares it - this just clears IDE warnings
set -a
models_dir="${current_directory}/../models"
config_dir="${current_directory}/../config/${container_name}"
image_name="_auto_detected_"
license_data_file="${current_directory}/../license/license.txt"
license_key_file="${current_directory}/../license/license.key"
run_mode="background"
set +a

parse_all_arguments "${@}"
parse_argument_with_value "models_dir" "directory path of AI models - default: ${models_dir}"
parse_argument_with_value "config_dir" "directory path of configuration files - default: ${config_dir}"
parse_argument_with_value "image_name" "tag of docker image to use - default: will be determined by git tags"
parse_argument_with_value "license_data_file" "data file of your UVAP license - default: ${license_data_file}"
parse_argument_with_value "license_key_file" "key file of your UVAP license - default: ${license_key_file}"
parse_argument_with_value "run_mode" "<background|foreground> - default: ${run_mode}"
validate_remaining_cli_arguments

docker_container_run
