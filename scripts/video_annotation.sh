#!/bin/bash

set -eu
source "$(dirname "$(realpath "$0")")/uvap_bash_functions"

current_directory="${current_directory}" # the above source declares it - this just clears IDE warnings
set -a
demo_applications_dir="${current_directory}/../demo_applications"
templates_dir="${current_directory}/../templates"
config_ac_dir="${current_directory}/../config"
video_dir="${current_directory}/../videos"
models_dir="${current_directory}/../models"
license_data_file="${current_directory}/../license/license.txt"
license_key_file="${current_directory}/../license/license.key"
verbose=false

uvap_mgr_docker_image_name="_auto_detected_"
uvap_demo_applications_docker_image_name="_auto_detected_"
uvap_kafka_tracker_docker_image_name="_auto_detected_"
uvap_kafka_reid_docker_image_name="_auto_detected_"
set +a

parse_all_arguments "${@}"
parse_argument_with_value "demo_name" "<head_detection|head_pose|demography|tracker|skeleton|basic_reidentification>"
parse_argument_with_value "video_dir" "directory path of the input and output videos - default: ${video_dir}"
parse_argument_with_value "video_file_name" "basename of the input video file inside the --video-dir directory"
parse_argument_with_value "fps_number" "the FPS number of the input video"
parse_argument_with_value "width_number" "the width in pixels of the input video"
parse_argument_with_value "height_number" "the height in pixels of the input video"
parse_argument_with_value "demo_applications_dir" "directory path of demo applications scripts - default: ${demo_applications_dir}"
parse_argument_with_value "templates_dir" "directory path of configuration templates - default: ${templates_dir}"
parse_argument_with_value "config_ac_dir" "directory path of configuration files - will be created if not existent - default: ${config_ac_dir}"
parse_argument_with_value "models_dir" "directory path of AI models - default: ${models_dir}"
parse_argument_with_value "license_data_file" "data file of your UVAP license - default: ${license_data_file}"
parse_argument_with_value "license_key_file" "key file of your UVAP license - default: ${license_key_file}"
parse_argument_with_value "uvap_mgr_docker_image_name" "tag of docker image to use - default: will be determined by git tags"
parse_argument_with_value "uvap_demo_applications_docker_image_name" "tag of docker image to use - default: will be determined by git tags"
parse_argument_with_value "uvap_kafka_tracker_docker_image_name" "tag of docker image to use - default: will be determined by git tags"
parse_argument_with_value "uvap_kafka_reid_docker_image_name" "tag of docker image to use - default: will be determined by git tags"
parse_argument_without_value "verbose"
validate_remaining_cli_arguments

ms_log_output="/dev/null"
if test "${verbose}" = "true"; then
	ms_log_output="/dev/stdout"
fi

video_file_name="${video_file_name}" # parse_argument_with_value declares it - this just clears IDE warnings
fps_number="${fps_number}" # parse_argument_with_value declares it - this just clears IDE warnings
width_number="${width_number}" # parse_argument_with_value declares it - this just clears IDE warnings
height_number="${height_number}" # parse_argument_with_value declares it - this just clears IDE warnings
demo_name="${demo_name}" # parse_argument_with_value declares it - this just clears IDE warnings
if ! [[ "${demo_name}" =~ ^(head_detection|head_pose|demography|tracker|skeleton|basic_reidentification)$ ]]; then
	echo "ERROR: unrecognized demo name: ${demo_name}" >&2
	echo "ERROR: override with --demo-name" >&2
	print_help
fi

if test "basic_reidentification" = "${demo_name}"; then
	demo_mode="fve"
elif test "skeleton" = "${demo_name}"; then
	demo_mode="skeleton"
else
	demo_mode="base"
fi

stream_uri="${video_dir}/${video_file_name}"
if ! test -r "${stream_uri}"; then
	echo "ERROR: video file '${stream_uri}' does not exist or not readable" >&2
	exit 1
fi
stream_uri="/videos/${video_file_name}"

echo "Starting to configure..."
"${current_directory}/config.sh" \
	--demo-mode "${demo_mode}" \
	--stream-uri "${stream_uri}" \
	--demo-applications-dir "${demo_applications_dir}" \
	--templates-dir "${templates_dir}" \
	--config-ac-dir "${config_ac_dir}" \
	--demo-image-name "${uvap_demo_applications_docker_image_name}" \
	> "${ms_log_output}"
echo "Finished configuring."

sed -i -e 's/startTS=NOW/startTS=0/' -e 's/endTS=NEVER/endTS=END/' "${UVAP_HOME}"/config/uvap_*/*.properties

echo "Starting the core analysis..."
"${current_directory}/run_mgr.sh" \
	--models-dir "${models_dir}" \
	--config-dir "${config_ac_dir}/uvap_mgr" \
	--image-name "${uvap_mgr_docker_image_name}" \
	--license-data-file "${license_data_file}" \
	--license-key-file "${license_key_file}" \
	--run-mode "foreground" \
	-- \
	--rm \
	--net=uvap \
	--mount "type=bind,readonly,src=${video_dir},dst=/videos" \
	> "${ms_log_output}"
echo "Finished core analysing."

if test "tracker" = "${demo_name}"; then
	echo "Starting the tracker..."
	"${current_directory}/run_kafka_tracker.sh" \
		--config-dir "${config_ac_dir}/uvap_kafka_tracker" \
		--image-name "${uvap_kafka_tracker_docker_image_name}" \
		--run-mode "foreground" \
		-- \
		--rm \
		--net=uvap \
		> "${ms_log_output}"
	echo "Finished tracking."
fi

if test "basic_reidentification" = "${demo_name}"; then
	sed -i \
		-e 's/"start":"START_NOW"/"start":"START_BEGIN"/' \
		-e 's/"end":"END_NEVER"/"end":"END_END"/' \
		-e 's/"reid_max_count":1/"reid_max_count":10/' \
		"${UVAP_HOME}"/config/uvap_kafka_reid/uvap_kafka_reid.json
	echo "Starting the basic reidentification..."
	"${current_directory}/run_kafka_reid.sh" \
		--config-dir "${config_ac_dir}/uvap_kafka_reid" \
		--image-name "${uvap_kafka_reid_docker_image_name}" \
		--run-mode "foreground" \
		-- \
		--rm \
		--net=uvap \
		> "${ms_log_output}"
	echo "Finished basic reidentification."
fi

echo "Starting to annotate..."
"${current_directory}/run_demo.sh" \
	--demo-mode "${demo_mode}" \
	--demo-name "${demo_name}" \
	--demo-applications-dir "${demo_applications_dir}" \
	--extra-demo-flags "-d -o -v" \
	--image-name "${uvap_demo_applications_docker_image_name}" \
	--run-mode "foreground" \
	-- \
	--rm \
	--net=uvap \
	> "${ms_log_output}"
echo "Finished annotating."

if test "${uvap_demo_applications_docker_image_name:-}" = "_auto_detected_"; then
	uvap_demo_applications_docker_image_name="$(get_docker_image_tag_for_component uvap_demo_applications)"
fi

video_writer_container_name="uvap_video_writer"
echo "Starting to write video..."

# TODO: if no symlinks found in demo_applications_dir, mount it.

docker container create \
	--name "${video_writer_container_name}" \
	--rm \
	--user="$(id -u)" \
	--mount "type=bind,src=${video_dir},dst=/videos" \
	--net=uvap \
	"${uvap_demo_applications_docker_image_name}" \
	python3.7 "apps/uvap/write_video.py" \
		kafka:9092 \
		"${demo_mode}.cam.0.${demo_name}.Image.jpg" \
		-fps "${fps_number}" \
		-width "${width_number}" \
		-height "${height_number}" \
	> "${ms_log_output}"

tar -c -C "${demo_applications_dir}" -h -f - . | \
	docker container cp --archive - "${video_writer_container_name}:/ultinous_app/"

docker container start --attach ${video_writer_container_name} > /dev/null
echo "Finished writing video."
