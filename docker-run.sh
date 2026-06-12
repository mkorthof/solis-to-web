#!/bin/sh

docker run \
    --detach \
    --name mosquitto \
    eclipse-mosquitto

docker run \
    --detach \
    --name solis-mqtt-to-web-client \
    --volume "$PWD/config.py:/app/config.py" \
    --volume "$PWD/web:/app/web" \
    --link "mosquitto:mqtt-broker" \
    ghcr.io/mkorthof/solis-mqtt-to-web-client:latest

