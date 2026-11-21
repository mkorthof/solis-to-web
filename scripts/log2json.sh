#!/bin/bash

LOG="solis.log"
if [ -n "$1" ]; then
  LOG="$1"
fi

OUTDIR="./export"

while read -r json; do
  ts="$(echo "$json" | jq .NOTIFICATION.INVERTER1.INVERTER_TIME)"
  fpath="$(date  -d@"${ts}" +'%Y/%m/%d')"
  if [ -s "${OUTDIR}/${fpath}/${ts}.json" ]; then 
    echo "ERROR: ${OUTDIR}/${fpath}/${ts}.json already exists, skipping.." 
  else
    mkdir -p "${OUTDIR}/${fpath}"
    echo "$json" > "${OUTDIR}/${fpath}/${ts}.json"
  fi
done < <(grep -Pow "Received \K\S+" "$LOG")
