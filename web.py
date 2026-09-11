import config
import message
import helper
import codes

import datetime


''' HTML Templates '''


def plot_html(period, plot):
    ''' Get plot.html contents to include in template '''
    data = None
    try:
        with open(f'{config.WEBDIR}/plot/{period}_{plot}.html', 'r', encoding='utf-8', errors='ignore') as f_plot:
            data = f_plot.read()
    except Exception as e:
        print(f'ERROR: reading {plot} plot HTML file for "{plot}" "{period}" - "{e}"')
        data = f'<p>❌ Plot "{period.capitalize()} - {plot}" is not available</p>'
    return(data)


def messages_table(period):
    return(f'''
        <table>\n\
            <tr>\n \
                <th>Datetime</th>\n \
                <th>Yield (kWh)</th>\n \
                <th>Power (kW)</th>\n \
                <th>Message</th>\n \
            </tr>\n \
            {''.join(f' \
                <tr>\n \
                    <td>{k}</td>\n \
                    <td>{helper.divide(v['E_TODAY'], 10, 0) if v.get('E_TODAY') else None}</td>\n \
                    <td>{helper.divide(v['APPARENT_POWER'], 1000, 0) if v.get('APPARENT_POWER') else None}</td>\n \
                    {'<td>-</td>' if config.STORE == 'database' else \
                        f'<td>\n \
                            <a href="#" onclick=\'fetchJSONData("{v.get('fn')}", "html", true)\'> html</a> | \n \
                            <a href="#" onclick=\'document.getElementById("message").innerHTML = \
                                `<pre>${{fetchJSONData("{v.get('fn')}", "pretty", {str(config.MASK).lower()})}}</pre>`\'>json</a>\n \
                        </td>\n' \
                    } \
                </tr>\n' for k, v in message.history(period).items()) } \
        </table>\n
    ''')


# TODO: inverter fields: 'INVERTER_SN' 'INVERTER_VER'
#       collector fields: 'TOTAL_WTIME' 'CURRENT_WTIME' 'WORKMODE' 'COLLECTOR_VER' 'PRODUCT_MODEL'

def index_html(payload):
    ''' Template for index.html '''
    data = message.last(payload)
    collector = data['payload']['NOTIFICATION'][config.COLLECTOR_ID] if data.get('payload') else {}
    inverter = data['payload']['NOTIFICATION'][config.INVERTER_ID] if data.get('payload') else {}
    #inverter['WARNING_INFO_DATA'] = '3F2'

    def inverter_warning():
        if 'inverter' in locals() and codes.get_error(inverter.get('WARNING_INFO_DATA')):
            return(f'<p class="notice">⚠️ <mark><strong>WARNING:</strong></mark> {codes.get_error(inverter['WARNING_INFO_DATA'])}</p> ')
        return('')

    def link_plots():
        return(f'''{''.join(f' \
            {'\n' if i == len(config.LINK_PLOT_PERIODS)-1 and j == 0 else ''} \
                    <p><a href="plot/{period}_{plot}.html">{period.capitalize()} - {config.PLOTS[plot]['name']}</a></p>\n' \
                for i, period in enumerate(config.LINK_PLOT_PERIODS) \
            for j, plot in enumerate(config.LINK_PLOT_TYPES)) }
        ''')

    return(f'''
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link rel="stylesheet" href="static/simple.css">
                <link rel="stylesheet" href="static/custom.css">
            <script type="text/javascript" src="static/helper.js"></script>
                <title>{config.TITLE}</title>
            </head>
            <body>
                <header>
                    <h1>
                        <a href="index.html" style="text-decoration:none;color:var(--text)">
                            {config.HEADER}
                        </a>
                    </h1>
                </header>
                <main>
                    <h4>Status</h4>
                    <p>Last updated: <span id="updated">0 seconds ago</span></p>

                    {'' if 'collector' not in locals() else
                     f'<img src="static/collector.svg" class="icon" /> Collector \
                        <ul> \
                            <li>Current Work Time: {format(datetime.timedelta(seconds=collector.get('CURRENT_WTIME', 0)).seconds/3600, ".0f")} hours</li> \
                            <li>Total Work Time: {datetime.timedelta(seconds=collector.get('TOTAL_WTIME', 0))}</li> \
                        </ul> \
                    '}

                    {'' if 'inverter' not in locals() else
                     f'<img src="static/inverter.svg" class="icon" />  Inverter \
                        <ul> \
                            <li>Time: {data.get('date')} {data.get('time')}</li> \
                            <li>Temperature: {helper.divide(inverter.get('INVERTER_TEMP'), 10, 0)} °C</li> \
                            <li>Current State: {codes.get_status(inverter.get('CURRENT_STATE'))}</li> \
                            {inverter_warning()} \
                        </ul> \
                    '}
                    
                    <h4>Real-time Information</h4>
                    <p><img src="static/electricity.svg" class="icon" />Total Inverter Power: <strong>{helper.divide(data.get('APPARENT_POWER'), 1000, 0)} kW</strong></p>
                    <p><img src="static/happy.svg" class="icon" /> Energy Yield: <strong>{helper.divide(data.get('E_TODAY'), 10, 0)} kWh</strong></p>
                    <ul>
                        <li>Yesterday: {helper.divide(data.get('e_yesterday'), 10, 0)} kWh</li>
                        <li>Month: {data.get('E_MONTH')} kWh</li>
                        <li>Year: {data.get('E_YEAR')} kWh</li>
                        <li>Total: {data.get('E_TOTAL')} kWh</li>
                    </ul>
                    <p></p> 
                     <h4>Graphs</h4>

                    {''.join(f'<p>{plot_html('today', plot)}</p>' \
                        for plot in config.INDEX_PLOT_TYPES) }

                    {''.join(f' \
                        <details> \
                            <summary><span id="plot_period">Yesterday</span></summary> \
                            {''.join(plot_html('yesterday', plot) for plot in config.LINK_PLOT_TYPES)} \
                        </details>') }

                    <article>
                    {link_plots()}
                    </article>
                    
                    {'' if config.MASK else \
                        '<div id="message"></div>' \
                        '<h4>Messages</h4>\n' \
                        f'{''.join(f' \
                            <details>\n \
                                <summary>\n \
                                    <span id="message_period">{period.capitalize()}</span>\n \
                                </summary>\n \
                                {messages_table(period)} \
                            </details>\n' \
                            for period in ['today', 'yesterday'])}' \
                        f'{''.join(f'<article> \
                                <a href="messages_{period}.html">{period.capitalize()}</a> \
                            </article>\n' \
                            for period in config.LINK_PREVIOUS_MESSAGES)}' }
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
                    lastUpdated("{data.get('timestamp')}")
                </script>
            </body>
        </html>
    ''')


def messages_html(period):
    ''' Template for previous messages_<period>.html '''
    return(f'''
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link rel="stylesheet" href="static/simple.css">
                <link rel="stylesheet" href="static/custom.css">
            <script type="text/javascript" src="static/helper.js"></script>
                <title>{config.TITLE} - Messages</title>
            </head>
            <body>
            <header>
                    <h1><a href="index.html" style="text-decoration:none;color:var(--text)">{config.HEADER}</a></h1>
                </header>
                <main>
                    <h3>Message history '{period}'</h3>
                    {messages_table(period)}
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

