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
    --name-of-demo)
            shift
      name_of_demo="${1}"
    ;;
    --demo-mode)
            shift
      demo_mode="${1}"
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
elif test -z "${name_of_demo:-}"; then
    echo "name-of-demo is unset! Override with --name-of-demo"
    exit 1
elif test -z "${demo_mode:-}"; then
    echo "demo-mode is unset! Override with --demo-mode"
    exit 1
fi

release_tag="$(git -C "$(dirname "$(realpath "${0}")")" tag --list --sort=-creatordate --merged HEAD 'release/*' | head -n1 | cut -f2 -d/)"
image="ultinous/uvap:uvap_demo_applications_${release_tag}"
${docker_binary_path} pull ${image}
name="uvap_demo_applications"


user_id="$(id -u)"
docker rm --force ${name} 2> /dev/null || true
# run image
xhost +
${nvidia_docker_binary_path}  run \
    --detach \
    --name ${name} \
    -v "/tmp/.X11-unix":"/tmp/.X11-unix" \
    -v "$HOME/uvap/demo_applications":"/ultinous_app" \
    -e DISPLAY=$DISPLAY \
    --net=uvap \
    --env="QT_X11_NO_MITSHM=1" \
    ${image} /usr/bin/python3.6 apps/uvap/${name_of_demo}_DEMO.py --output kafka:9092 ${demo_mode}
