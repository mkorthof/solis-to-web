import config
import message
import helper

import shutil
import os


''' HTML Templates '''


def plot_html(period, plot_type):
    ''' Get plot.html contents to include in template '''
    data = None
    try:
        with open(f'{config.WEBDIR}/plot_{plot_type}_{period}.html', 'r', encoding='utf-8', errors='ignore') as f_plot:
            data = f_plot.read()
    except Exception as e:
        print(f'ERROR: reading {plot_type} plot HTML file for "{plot_type}" "{period}" - "{e}"')
        data = f'<p>❌ Plot {plot_type} "{period.capitalize()}" is not available</p>'
    return(data)


def index_html(payload):
    ''' Template for index.html '''
    data = message.today(payload)
    if config.WEBSTATIC:
        if not os.path.isdir(f'{config.WEBDIR}/static'):
            os.mkdir(f'{config.WEBDIR}/static') 
        for file in config.WEBSTATIC_FILES:
            shutil.copyfile(file, f'{config.WEBDIR}/static/{file}')
    return(f'''
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link rel="stylesheet" href="static/simple.css">
                <link rel="stylesheet" href="static/custom.css">
                <script type="text/javascript" src="static/helper.js"></script>
                <title>{config.INDEX_TITLE}</title>
            </head>
            <body>
                <header>
                    <h1><a href="index.html" style="text-decoration:none;color:var(--text)">{config.INDEX_TITLE}</a></h1>
                </header>
                <main>
                    <h4>Status</h4>
                    <p>Subscription Topic: "{helper.mask(config.TOPIC)}"</p>
                    <p>Last updated: <span id="updated">0 seconds ago</span></p>
                    <ul>
                        <li>Date: {data['date']} Time: {data['time']}</li>
                        <li>Temperature: {data['temp']} °C</li>
                        <li>Current State: {data['state']}</li>
                        <li>Warning Info Data: {data['warning']} ({"NORMAL" if data['warning'] == 0 else "⚠️ NOK"})</li>
                    </ul>
                    <h4>Information</h4>
                    <p>⚡ Current Power: <strong>{data['power']} W</strong></p>
                    <p>🌞 Energy Yield Today: <strong>{data['e_today']} kWh</strong></p>
                    <ul>
                        <li>Yesterday: {data['e_yesterday']} kWh</li>
                        <li>Month: {data['e_month']} kWh</li>
                        <li>Year: {data['e_year']} kWh</li>
                        <li>Total: {data['e_total']} kWh</li>
                    </ul>
                    {plot_html('today', 'yield')}
                    {plot_html('today', 'power')}
                    <div id="message"></div>
                    <p></p>
                    <details>
                        <summary>View more graphs</summary>
                        {''.join(f'{plot_html(period, 'yield')} \
                                   {plot_html(period, 'power')}' for period in config.SHOW_PERIODS)}
                        {''.join(f'<p><a href="plot_yield_{period}.html">View "Energy Yield - {period.capitalize()}"</a></p>  \
                                   <p><a href="plot_power_{period}.html">View "Power - {period.capitalize()}"</a></p>' for period in config.LINK_PERIODS)}
                    </details>
                    <p>&nbsp;</p>
                    <details>
                        <summary>Todays messages</summary>
                        <table>
                            <tr>
                                <th>Datetime</th>
                                <th>Yield (kWh)</th>
                                <th>Power (W)</th>
                                <th>Message</th>
                            </tr>
                            { ''.join(f' \
                                <tr>\n \
                                    <td>{k}</td>\n \
                                    <td>{v['yield']}</td>\n \
                                    <td>{v['power']}</td>\n \
                                    <td>\n \
                                        <a href="#" onclick=\'fetchJSONData("{v['fn']}", "html", true)\'> html</a> | \n \
                                        <a href="#" onclick=\'document.getElementById("message").innerHTML = `<pre>${{fetchJSONData("{v['fn']}", "pretty", {str(config.MASK).lower()})}}</pre>`\'>json</a>\n \
                                    </td>\n \
                                </tr>\n' \
                                for k,v in message.previous('today').items()) }
                        </table>
                    </details>
                    <details>
                        <summary>Previous messages</summary>
                        {''.join(f' <p><a href="messages_{period}.html">View "{period.capitalize()}"</a></p><p></p>' for period in config.SHOW_PERIODS + config.LINK_PERIODS)}
                    </details>
                </main>
                <footer>
                    <p>Page generated on {helper.fmt_date()}</p>
                    <p>
                        <a href="https://mqtt.org">MQTT</a> | 
                        <a href="https://mosquitto.org">Mosquitto</a> | 
                        <a href="https://eclipse.dev/paho">Paho</a> | 
                        <a href="https://plotly.com/python">Plotly</a> | 
                        <a href="https://github.com/kevquirk/simple.css">Simple.css</a>
                    </p>
                </footer>
                <script type="text/javascript">
                    updated("{data['timestamp']}")
                </script>
            </body>
        </html>
    ''')


def history_html(period):
    return(f'''
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link rel="stylesheet" href="static/simple.css">
                <link rel="stylesheet" href="static/custom.css">
                <script type="text/javascript" src="static/helper.js"></script>
                <title>Solis Inverter</title>
            </head>
            <body>
                <header>
                    <h1><a href="index.html" style="text-decoration:none;color:var(--text)">☀️ Solis 4G Mini Inverter</a></h1>
                </header>
                <main>
                    <h3>Message history '{period}' </h3>
                    <table>
                        <tr>
                            <th>Datetime</th>
                            <th>Yield (kwh)</th>
                            <th>Power (W)</th>    
                            <th>Message</th>
                        </tr>
                        { ''.join(f' \
                            <tr>\n \
                                <td>{k}</td><td>{v['yield']}</td>\n \
                                <td>{v['power']}</td>\n \
                                <td>\n \
                                    <a href="#" onclick=\'fetchJSONData("{v['fn']}", "html", {str(config.MASK).lower()})\'> html</a> | \n \
                                    <a href="#" onclick=\'document.getElementById("message").innerHTML = `<pre>${{fetchJSONData("{v['fn']}", "pretty", {str(config.MASK).lower()})}}</pre>`\'>json</a>\n \
                                </td>\n \
                            </tr>\n' \
                            for k,v in message.previous(period).items()) }
                    </table>
                    <div id="message"></div>
                </main>
                <footer>
                    <p>Page generated on {helper.fmt_date()}</p>
                    <p>
                        <a href="https://mqtt.org">MQTT</a> | 
                        <a href="https://mosquitto.org">Mosquitto</a> | 
                        <a href="https://eclipse.dev/paho">Paho</a> | 
                        <a href="https://plotly.com/python">Plotly</a> | 
                        <a href="https://github.com/kevquirk/simple.css">Simple.css</a>
                    </p>
                </footer>
            </body>
        </html>
    ''')
