# Host or IP of MQTT broker
BROKER_HOST = "10.20.30.40"
BROKER_PORT = 1883

# Broker Auth (optional), default is "solis/solis"
BROKER_USERNAME = "solis"
BROKER_PW = "solis"

# Subscribe to topic '/ginlong/<serial>/update', where <serial>
# is the device serial number of the inverter (Ginglong Technologies is Solis)
TOPIC = "/ginlong/1A123456ABC0123F/update"

# Inverter ID, default is '1'
INVERTER_ID = "INVERTER1"

# Base directory for json and html files
WEBDIR = './web'

# Mask serial etc in output, e.g. when serving web dir publicly 
MASK = True

# Title index.html, default: "☀️ Solis Inverter"
INDEX_TITLE = "☀️ Solis 4G Mini Inverter"

# All available periods: 'yesterday', 'week', 'month', 'year', 'this_month', 'this_year'.

# Show messages and plot period (besides 'Today')
SHOW_PERIODS = ['yesterday', 'week']

# Add links to more messages and plot periods
LINK_PERIODS = ['month', 'year']

# Plot title, unit for yaxis and color
PLOT_TYPES = {
    'yield': { 'name': 'Plot Energy Yield', 'unit': 'kWh', 'color': 'blue' },
    'power': { 'name': 'Plot Power', 'unit': 'watt', 'color': 'red' }
}

# Offset hours to invertor timestamp
TS_OFFSET = 6

# Create static files in web dir
WEBSTATIC = True

# Files in {WEBDIR}/static. If you set WEBSTATIC to False you'll have manually copy them.
WEBSTATIC_FILES = [
    'helper.js',
    'simple.css',
    'custom.css',
    'plotly.min.js'
]
