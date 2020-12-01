#!/bin/sh

set -eu

BROKER="${1}"
SRC_ID="${2}"
DST_ID="${3}"

record=$(kafkacat -C -b "$BROKER" -t detected.records.json -o beginning -e -f "%o;%T;%k;%s\n" -u \
  | grep ';'"$SRC_ID"';$') || (echo "Not fond." >&2 && exit 1 )

key=$(echo "$record" | cut -d ";" -f 3)
out="$key"";""$SRC_ID"":""$DST_ID"

echo "$out" | kafkacat -P -b "$BROKER" -t named.records.json -K";"

echo "Updated."
