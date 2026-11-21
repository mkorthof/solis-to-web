#!/bin/sh

GHCR="ghcr.io/mkorthof/solis-to-web"
COMMIT="$(git rev-parse --short HEAD)"

cd .. || exit 1
test -d docker || { echo "Run this script from 'docker' dir"; exit 1; }
docker build \
    --file docker/Dockerfile \
    --tag "${GHCR}:${COMMIT:-head}" \
    --tag "${GHCR}:latest" \
    .
