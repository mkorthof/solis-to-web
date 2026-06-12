#!/bin/sh

GHCR="ghcr.io/mkorthof/solis-mqtt-to-web-client"
COMMIT="$(git rev-parse --short HEAD)"

docker build --tag "${GHCR}:${COMMIT:-head}" --tag "${GHCR}:latest" . 

