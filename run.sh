#!/bin/sh

# Run Solis To Web service

if ! command -v uv >/dev/null 2>&1; then
    echo "ERROR: could not find 'uv' (https://docs.astral.sh/uv), exiting..."
    exit 1
fi

SERVICE="Solis MQTT to Web Client"
PID="$(pgrep -F solis.pid 2>/dev/null)"

func_status() {
    if [ -n "$PID" ]; then
        printf "\"%s\" is running (pid:%s)\n" "$SERVICE" "$PID"
    else
        printf "\"%s\" is not running\n" "$SERVICE"
    fi
}

func_run() {
    if [ -z "$PID" ]; then
        rm -f solis.pid
        { PYTHONUNBUFFERED=1 nohup uv run main.py >solis.log 2>&1 & } && echo $! > solis.pid
        sleep 1
        PID="$(pgrep -F solis.pid 2>/dev/null)"
        if [ -n "$PID" ]; then
            printf "Saved pid %s as solis.pid, logging to solis.log\n" "$PID"
        else
            rm -f solis.pid
            echo "ERROR: failed to start, exiting.."
            exit 1
        fi
    else
        printf "Already running (pid:%s), to restart: '%s restart'\n" "$PID" "$0" 
    fi
}

func_kill() {
    pkill -F solis.pid  || { "ERROR: could not kill service"; exit 1; }
    rm -f solis.pid
    PID=""
}

case "$1" in
    status)
        func_status
    ;;
    start)
        printf "Starting \"%s\"..\n" "$SERVICE"
        func_run
    ;;
    stop)
        printf "Stopping \"%s\"..\n" "$SERVICE"
        func_kill
    ;;
    restart)
        printf "Restarting \"%s\"..\n" "$SERVICE"
        func_kill
        func_run
    ;;
    *)
        func_status
        printf "Usage: %s [start|stop|restart|status]\n" "$0"
    ;;
esac

exit 0
