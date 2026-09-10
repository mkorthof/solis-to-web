#!/bin/sh

GHCR="ghcr.io/mkorthof/solis-mqtt-to-web"
COMMIT="$(git rev-parse --short HEAD)"

docker build --tag "${GHCR}:${COMMIT:-head}" --tag "${GHCR}:latest" .
