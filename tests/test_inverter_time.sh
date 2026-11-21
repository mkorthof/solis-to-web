#!/bin/bash

# Show inverter time 

jsondir="./htdocs/json"

if [ -n "$1" ]; then
    jsondir="$1"
fi

for i in $(find "$jsondir" -type f -print0 | xargs -0 jq '.NOTIFICATION.INVERTER1.INVERTER_TIME'); do
    printf "DEBUG: jsondir=%s ts=%s inverter_time=%s\n"  "$jsondir" "$i" "$(date -d@"${i}" +'%F %T')"
done
