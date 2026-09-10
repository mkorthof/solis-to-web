# Solis to Web

*Gets Solis Inverter data and stores as web pages*

Tested with [Solis 4G Mini Inverter](https://www.solisinverters.au/product_detail/Solis-mini-(700-3600)-4G)

- Uses [MQTT](https://mqtt.org), subscribes to inverters 'update' topic and gets messages with [Paho](https://eclipse.dev/paho)
- Messages are stored as json files
- Creates index.html showing yield, power, etc and graphs with [Plotly](https://plotly.com/python)
- SolisCloud not needed, data stays local 

## Requirements

A Solis Data Logger stick ([Solis-S2-WL-ST](https://www.solisinverters.com/global/accessories9/S2_WL_ST_gl.html)), a [MQTT broker](https://mqtt.org) (Eclipse [Mosquitto](https://mosquitto.org)) and optionally a web server.

To run Mosquitto with Docker, see [here](https://hub.docker.com/_/eclipse-mosquitto#how-to-use-this-image).

Make sure Data Stick is inserted in the Inverter and can connect to the MQTT broker (Mosquitto).

Goto webadmin page of Data stick:

- Set MQTT Broker under to "Advanced > Mqtt Settings"
- Check "Status > Remote Server Information", it should say "Connected"
- Also get your "Device serial number"

## Configuration

If config\.py does not exist yet, copy defaults from config.py.dist to config\.py first.

Edit config\.py:

- set `BROKER_HOST`
- (optionally) set auth with `BROKER_USERNAME` and `BROKER_PW`, remove settings to disable
- change `TOPIC` to your device serial number

Remeber check for config changes after updating (see [commits](https://github.com/mkorthof/solis-to-web/commits/master/))

*NOTE: Environment vars will overwrite config settings*

## Running

Either use uv or Docker.

If you do not have uv, check [installation](https://docs.astral.sh/uv/getting-started/installation). It will take care of depedencies (e.g. Paho and Plotly modules).

Output html and json files are stored in 'www' dir (optionally use e.g. NGINX to serve).

## uv

Run in background and log to solis.log: `./run.sh`

To run in foreground: `uv run main.py`

## docker

Run latest image from GitHub:

`docker run --volume "$PWD/config.py:/app/config.py" --volume "$PWD/web:/app/web"  ghcr.io/mkorthof/solis-mqtt-to-web:latest`

Or use env vars e.g.:

`docker run --env BROKER_HOST=1.2.3.4 --env BROKER_PORT=321 --env TOPIC="/ginlong/ABCDEF1234/update" --volume "$PWD/web:/app/web"  ghcr.io/mkorthof/solis-mqtt-to-web:latest`

To run both Mosquitto and Client (detached):

`./docker-run.sh`

## docker compose

Run Mosquitto and Client using compose (detached):

`./docker compose up -d`
