#!/bin/bash

set -eu
set -o pipefail

realpath=$(realpath "$0")
dirname=$(dirname "$realpath")
source "$dirname""/uvap_bash_functions"

test_executable docker
test_executable git

uvap_flavour=$(get_current_uvap_flavour)
release_tag=$(get_current_release_git_tag)

suffix=""
if [ "$uvap_flavour" != "" ]; then
  suffix="_""$uvap_flavour"
fi

ldc_image="ultinous/uvap_licence_data_collector""$suffix"":""$release_tag"
echo "Licence data collector docker image: ""$ldc_image" 1>&2

docker run --rm -u $(id -u) --runtime nvidia \
  -v /sys/firmware/:/host_sys/firmware/:ro \
  "$ldc_image"
