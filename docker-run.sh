#!/bin/sh

#cp --update=none ./config.py.dist ./config.py

docker run \
    --detach \
    --name mosquitto \
    eclipse-mosquitto

docker run \
    --detach \
    --name solis-mqtt-to-web \
    --volume "./config.py:/app/config.py" \
    --volume "./www:/app/www" \
    --link "mosquitto:mqtt-broker" \
    ghcr.io/mkorthof/solis-mqtt-to-web:latest

