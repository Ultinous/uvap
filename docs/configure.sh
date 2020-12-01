#!/bin/sh

set -eux

while test "$#" -gt 0; do
	case "${1}" in
		--properties-file)
			shift
			PROPERTIES_FILE="$1"
		;;
		--target-directory)
			shift
			TARGET_DIRECTORY="$1"
		;;
		*)
			echo "ERROR: unrecognized option: ${1}" >&2
			exit 1
		;;
	esac
	shift
done

if test -z "${PROPERTIES_FILE:-}"; then
	echo "Properties file is unset! Specify with --properties-file" >&2
	exit 1
fi

if test -z "${TARGET_DIRECTORY:-}"; then
	echo "Target directory is unset! Specify with --target-directory" >&2
	exit 1
fi

if ! test -e "${PROPERTIES_FILE}"; then
    echo "Properties file is not readable! Override with --properties-file" >&2
    exit 1
fi

if ! test -d "${TARGET_DIRECTORY}"; then
	echo "Target directory can not be found! Override with --target-directory" >&2
	exit 1
fi

PROPERTY_VAR_NAME_DELIMITER='@%%@'

cp -r ./app/* "${TARGET_DIRECTORY}/"

while read PROPERTY_LINE; do
	PROPERTY_KEY="$(echo ${PROPERTY_LINE} | cut -f1 -d=)"
	PROPERTY_VALUE="$(echo ${PROPERTY_LINE} | cut -f2- -d= | sed 's/\"/\\\\\"/g')"
	find "${TARGET_DIRECTORY}" -type f -exec sh -euxc "sed -i 's*${PROPERTY_VAR_NAME_DELIMITER}${PROPERTY_KEY}${PROPERTY_VAR_NAME_DELIMITER}*${PROPERTY_VALUE}*g' \$0" '{}' \;
done < ${PROPERTIES_FILE}

if grep -Erq "${PROPERTY_VAR_NAME_DELIMITER}[A-Za-z_-]+${PROPERTY_VAR_NAME_DELIMITER}" "${TARGET_DIRECTORY}"; then
#	grep -Ern "${PROPERTY_VAR_NAME_DELIMITER}[A-Za-z_-]+${PROPERTY_VAR_NAME_DELIMITER}" "${TARGET_DIRECTORY}" >&2 || true
	grep -Ern "${PROPERTY_VAR_NAME_DELIMITER}[A-Za-z_-]+${PROPERTY_VAR_NAME_DELIMITER}" "${TARGET_DIRECTORY}" | sed -e 's/{/\n/g' -e 's/}/\n/g' | grep "${PROPERTY_VAR_NAME_DELIMITER}" >&2 || true
	grep -Erl "${PROPERTY_VAR_NAME_DELIMITER}[A-Za-z_-]+${PROPERTY_VAR_NAME_DELIMITER}" "${TARGET_DIRECTORY}" >&2 || true
	echo "ERROR: there are some unset properties: see above." >&2
	exit 1
fi
