#!/bin/bash

set -eu
source "$(dirname "$(realpath "$0")")/uvap_bash_functions"

current_directory="${current_directory}" # the above source declares it - this just clears IDE warnings
set -a
demo_applications_dir="${current_directory}/../demo_applications"
templates_dir="${current_directory}/../templates"
config_ac_dir="${current_directory}/../config"
image_name="_auto_detected_"
set +a

parse_all_arguments "${@}"
parse_argument_with_value "demo_mode" "<base|skeleton|fve>"
parse_argument_with_multi_value "stream_uri" "file name / device name / RTSP URL of a stream to analyze - may be specified multiple times"
parse_argument_with_value "demo_applications_dir" "directory path of demo applications scripts - default: ${demo_applications_dir}"
parse_argument_with_value "templates_dir" "directory path of configuration templates - default: ${templates_dir}"
parse_argument_with_value "config_ac_dir" "directory path of configuration files - will be created if not existent - default: ${config_ac_dir}"
parse_argument_with_value "image_name" "tag of docker image to use - default: will be determined by git tags"
validate_remaining_cli_arguments

test_executable "docker"
test_executable "tar"

demo_mode="${demo_mode}" # parse_argument_with_value declares it - this just clears IDE warnings
if ! [[ "${demo_mode}" =~ ^(base|skeleton|fve)$ ]]; then
	echo "ERROR: unrecognized demo mode: ${demo_mode}" >&2
	echo "ERROR: override with --demo-mode" >&2
	print_help
fi
config_ac_dir="${config_ac_dir}" # parse_argument_with_value declares it - this just clears IDE warnings
stream_uris="${stream_uris}" # parse_argument_with_value declares it - this just clears IDE warnings

if test "${image_name:-}" = "_auto_detected_"; then
	image_name="$(get_docker_image_tag_for_component uvap_demo_applications)"
fi

jinja_yaml_param_file_path="${config_ac_dir}/params.yaml"
trap "rm -f ${jinja_yaml_param_file_path}" TERM INT EXIT

echo "ENGINES_FILE: /ultinous_app/models/engines/basic_detections.prototxt
KAFKA_BROKER_LIST: kafka
KAFKA_TOPIC_PREFIX: ${demo_mode}
INPUT_STREAMS:" > "${jinja_yaml_param_file_path}"

found_realtime_stream="false"
found_recorded_stream="false"
for stream_url in ${stream_uris}; do
	echo "  - ${stream_url}" >> "${jinja_yaml_param_file_path}"
	if test_string_starts_with "${stream_url}" "/"; then
		if test_string_starts_with "${stream_url}" "/dev/video"; then
			found_realtime_stream="true"
		else
			found_recorded_stream="true"
		fi
	else
		if echo "${stream_url}" | grep -qE '^[a-z]+://.*$'; then
			found_realtime_stream="true"
		else
			found_recorded_stream="true"
		fi
	fi
done
if test "true" = "${found_realtime_stream}" -a "true" = "${found_recorded_stream}"; then
	echo "ERROR: UVAP is not able to work with real-time video streams and with pre-recorded video files at the same time" >&2
	exit 1
fi
if test "true" = "${found_recorded_stream}"; then
	echo 'DROP: "off"' >> "${jinja_yaml_param_file_path}"
else
	echo 'DROP: "on"' >> "${jinja_yaml_param_file_path}"
fi

mounted_config_dir="/config"
mounted_templates_dir="/templates"

jinja_run_script_path="${config_ac_dir}/run_jinja.sh"
trap "rm -f ${jinja_yaml_param_file_path} ${jinja_run_script_path}" TERM INT EXIT
echo "#!/bin/sh" > "${jinja_run_script_path}"
echo "set -eu" >> "${jinja_run_script_path}"
chmod +x "${jinja_run_script_path}"

jinja_run="/usr/bin/python3.6 utils/jinja_template_filler.py ${mounted_config_dir}/params.yaml"

for uvap_component in $(get_uvap_components_list AND "properties" "${demo_mode}" | force_uvap_prefix); do
	mkdir -p "${config_ac_dir}/${uvap_component}/"
	echo "${jinja_run} ${mounted_templates_dir}/${uvap_component}_${demo_mode}_TEMPLATE.properties ${mounted_config_dir}/${uvap_component}/${uvap_component}.properties" >> "${jinja_run_script_path}"
	test -e "${templates_dir}/${uvap_component}_${demo_mode}_TEMPLATE.json" &&
		echo "${jinja_run} ${mounted_templates_dir}/${uvap_component}_${demo_mode}_TEMPLATE.json ${mounted_config_dir}/${uvap_component}/${uvap_component}.json" >> "${jinja_run_script_path}"
done
for uvap_component in $(get_uvap_components_list AND "data_flow" "${demo_mode}" | force_uvap_prefix); do
	mkdir -p "${config_ac_dir}/${uvap_component}/"
	echo "${jinja_run} ${mounted_templates_dir}/${uvap_component}_${demo_mode}_TEMPLATE.prototxt ${mounted_config_dir}/${uvap_component}/${uvap_component}.prototxt" >> "${jinja_run_script_path}"
done

docker pull "${image_name}" > /dev/null
container_name="uvap_config"
test "$(docker container ls --filter name="${container_name}" --all --quiet | wc -l)" -eq 1 \
	&& docker container stop "${container_name}" > /dev/null \
	&& docker container rm "${container_name}" > /dev/null

docker container create \
	--rm \
	--name "${container_name}" \
	--user "$(id -u)" \
	--mount "type=bind,readonly,source=${templates_dir},destination=${mounted_templates_dir}" \
	--mount "type=bind,source=${config_ac_dir},destination=${mounted_config_dir}" \
	--net=none \
	"${image_name}" \
	"${mounted_config_dir}/run_jinja.sh" \
	> /dev/null

tar -c -C "${demo_applications_dir}" -h -f - . | docker container cp --archive - "${container_name}:/ultinous_app/"

docker container start --attach "${container_name}" > /dev/null
