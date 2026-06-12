#!/bin/sh

SERVICE="Solis MQTT to Web Client"

if ! command -v uv >/dev/null 2>&1; then
    echo "Error: could not find \"uv\", exiting..."
    exit 1
fi

if [ "$1" = "restart" ]; then
  echo "Restarting \"$SERVICE\""
  pkill -F solis.pid  || "ERROR: could not kill service"
fi

printf "PID: " 
if ! pgrep -F solis.pid 2>/dev/null; then
    { PYTHONUNBUFFERED=1 nohup uv run main.py >solis.log 2>&1 & } && echo $! | tee solis.pid
else
    echo "\"${SERVICE}\" is already running, skipping uv run.."
    exit 0
fi

sleep 1

if pgrep -F solis.pid >/dev/null 2>&1; then
    echo "Started \"${SERVICE}\", saved solis.pid and logging to solis.log.."
    exit 0
else
    echo "ERROR: \"${SERVICE}\" failed to start, exiting.."
    exit 1
fi
