#!/bin/bash

set -eu
source "$(dirname "$(realpath "$0")")/uvap_bash_functions"

current_directory="${current_directory}" # the above source declares it - this just clears IDE warnings

parse_all_arguments "${@}"
validate_remaining_cli_arguments
test_executable docker
test_executable git

release_tag="$(get_current_release_git_tag)"

for component_name in $(get_uvap_components_list); do
		docker pull "ultinous/uvap:${component_name}_latest"
		docker pull "ultinous/uvap:${component_name}_${release_tag}"
done
