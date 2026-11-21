# Docker

## Run Client

Use github image to start container swith env vars, e.g.:

`docker run --env BROKER_HOST=1.2.3.4 --env BROKER_PORT=321 --env TOPIC="/ginlong/ABCDEF1234/update" --volume "$PWD/web:/app/web"  ghcr.io/mkorthof/solis-mqtt-to-web:latest`


## Server and Client

To run both Mosquitto and Client (detached), use wrapper script:

`cd docker && /docker-run.sh`

## Compose

Run Mosquitto and Client using docker compose (detached):

`cd docker && ./docker compose up -d`

## Build

`cd docker && ./docker-build.sh`
