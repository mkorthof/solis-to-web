import config
import message
import helper
import codes

import datetime
import json


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
    return data



def head():
    return(f'''
            <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="static/simple.css">
            <link rel="stylesheet" href="static/custom.css">
            <script type="text/javascript" src="static/helper.js"></script>
            <title>{config.TITLE}</title>
        </head>
    ''')


def footer():
    return(f'''
        <footer>
            <p>Page generated on {helper.fmt_date_time()} {'(with database)' if config.USE_DB else ''} </p>
            <p>
                <a href="https://mqtt.org">MQTT</a> | 
                <a href="https://mosquitto.org">Mosquitto</a> | 
                <a href="https://eclipse.dev/paho">Paho</a> | 
                <a href="https://plotly.com/python">Plotly</a> |  
                <a href="https://www.sqlite.org">SQLite</a> | 
                <a href="https://github.com/kevquirk/simple.css">Simple.css</a>
            </p>
        </footer>
    ''')


def messages_table(payload):        
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
                    <td>{helper.divide(message.inverter_notification(v)['E_TODAY'], config.PLOTS['E_TODAY']['div'], 0) if message.inverter_notification(v) else None}</td>\n \
                    <td>{helper.divide(message.inverter_notification(v)['DC_TOTALPOWER'], config.PLOTS['DC_TOTALPOWER']['div'], 0) if message.inverter_notification(v) else None}</td>\n \
                    {'<td>-</td>' if not config.USE_FILES else \
                        f'<td>\n \
                            <a href="#" onclick=\'fetchJSONData("{v.get('fn')}", "html", true)\'> html</a> | \n \
                            <a href="#" onclick=\'document.getElementById("message").innerHTML = \
                                `<pre>${{fetchJSONData("{v.get('fn')}", "pretty", {str(config.MASK).lower()})}}</pre>`\'>json</a>\n \
                        </td>\n' \
                    } \
                </tr>\n' \
                for k, v in payload.items()) } \
        </table>\n
    ''')


# TODO: inverter fields: 'INVERTER_SN' 'INVERTER_VER'
#       collector fields: 'TOTAL_WTIME' 'CURRENT_WTIME' 'WORKMODE' 'COLLECTOR_VER' 'PRODUCT_MODEL'

def index_html(payload, data):
    ''' Template for index.html '''
    inverter = message.inverter_notification(payload)
    data_yesterday = list(data['yesterday'].values())[1] if data.get('yesterday') else {}
    inverter_yesterday = message.inverter_notification(data_yesterday)
    inverter_timestamp = helper.dt_obj(message.inverter_timestamp(payload), True) if inverter else None
    inverter_date = inverter_timestamp.strftime("%Y-%m-%d") if inverter_timestamp else None
    inverter_time = inverter_timestamp.strftime("%H:%M:%S") if inverter_timestamp else None
    collector = message.collector_notification(payload)
    collector_work_time = format(datetime.timedelta(seconds=collector.get('CURRENT_WTIME', 0)).seconds/3600, ".0f") if collector else None
    collector_total_time = datetime.timedelta(seconds=collector.get('TOTAL_WTIME', 0)) if collector else None
    # test: inverter['WARNING_INFO_DATA'] = '3F2'
    inverter_warning = codes.get_error(inverter.get('WARNING_INFO_DATA'))
    inverter_warning_html = f'<p class="notice">⚠️ <mark><strong>WARNING:</strong></mark> {inverter_warning}</p>' if inverter_warning else ''

    return(f'''
        <!DOCTYPE html>
        <html lang="en">
            {head()}
            <body>
                <header>
                    <h1>
                        <a href="index.html">
                            {config.HEADER}
                        </a>
                    </h1>
                </header>
                <main>
                    <h4>Status</h4>
                    <p>Last updated: <span id="updated">0 seconds ago</span></p>
                    <article>
                        <p></p>
                        {'' if 'collector' not in locals() else
                        f'<img src="static/collector.svg" class="icon" /> Collector \
                            <ul> \
                                <li>Current Work Time: {collector_work_time} hours</li> \
                                <li>Total Work Time: {collector_total_time}</li> \
                            </ul> \
                        '}
                        {'' if 'inverter' not in locals() else
                        f'<img src="static/inverter.svg" class="icon" />  Inverter \
                            <ul> \
                                <li>Time: {inverter_date} {inverter_time}</li> \
                                <li>Temperature: {helper.divide(inverter.get('INVERTER_TEMP'), 10, 0)} °C</li> \
                                <li>Current State: {codes.get_status(inverter.get('CURRENT_STATE'))}</li> \
                                {inverter_warning_html} \
                            </ul> \
                        '}  
                    </article>
                    <h4>Real-time Information</h4>
                    <article>
                        <p>
                            <img src="static/electricity.svg" class="icon" />DC Total Power:
                            <strong>
                                {helper.divide(inverter.get('DC_TOTALPOWER'), config.PLOTS['DC_TOTALPOWER']['div'], 0)} {config.PLOTS['DC_TOTALPOWER']['unit']}
                            </strong>
                        </p>
                        <p>
                            <img src="static/apower.svg" class="icon" />Apparent Power:
                            <strong>
                                {helper.divide(inverter.get('APPARENT_POWER'), config.PLOTS['APPARENT_POWER']['div'], 0)} {config.PLOTS['APPARENT_POWER']['unit']}
                            </strong>
                        </p>
                        <p>
                            <img src="static/happy.svg" class="icon" /> Energy Yield Today: <strong>{helper.divide(inverter.get('E_TODAY'), config.PLOTS['E_TODAY']['div'], 0)} {config.PLOTS['E_TODAY']['unit']}</strong>
                        </p>
                        <p></p> 
                    </article>
                    <h4>Energy Yield Totals</h4>
                    <article>
                        <ul>
                            <li>Yesterday: {helper.divide(inverter_yesterday.get('E_TODAY'), config.PLOTS['E_TODAY']['div'], 0)} {config.PLOTS['E_TODAY']['unit']}</li>
                            <li>This Month: {inverter.get('E_MONTH')} kWh</li>
                            <li>This Year: {inverter.get('E_YEAR')} kWh</li>
                            <li>Total: {inverter.get('E_TOTAL')} kWh</li>
                        </ul>
                    </article>
                    <p>&nbsp;</p>
                    <h4>Graphs</h4>
                    <details open> 
                        <summary><span id="plot_period">Today</span></summary>
                        {''.join(f'{plot_html('today', plot)}' for plot in config.INDEX_PLOT_TYPES)}
                    </details>
                    <details> 
                        <summary><span id="plot_period">Yesterday</span></summary>
                        {''.join(plot_html('yesterday', plot) for plot in config.INDEX_PLOT_TYPES)}
                    </details>
                    <article>
                        {''.join(f' \
                                <p>📈 <a href="plot/{period}_{plot}.html">{period.capitalize()} - {config.PLOTS[plot]['name']}</a></p>\n' \
                                for period in config.LINK_PLOT_PERIODS \
                            for plot in config.LINK_PLOT_TYPES) }
                        <p>&nbsp;</p>
                        <p><a class="button" href="plots_all.html">Show All</a></p>
                    </article>
                    {'' if config.MASK else \
                        '<p>&nbsp;</p>'
                        '<div id="message"></div>\n' \
                        '<h4>Messages</h4>\n' \
                        f'{''.join(f' \
                            <details>\n \
                                <summary>\n \
                                    <span id="message_period">{period.capitalize()}</span>\n \
                                </summary>\n \
                                {messages_table(data.get(period))} \
                            </details>\n' \
                            for period in ['today', 'yesterday'])}' \
                        '<article>\n' \
                        f'{''.join(f' \
                            <p> 🔗 <a href="messages_{period}.html">Show {period.capitalize()} </a></p>\n' \
                            for period in config.LINK_PREVIOUS_MESSAGES)}' \
                        '</article>\n' }

                </main>
                {footer()}
                <script type="text/javascript">
                    lastUpdated("{inverter.get('timestamp')}")
                </script>
            </body>
            <script type="text/javascript">
                document.querySelectorAll('.modebar').forEach(el => {{
                    el.style.visibility = 'hidden';
                }});
            </script>
        </html>
    ''')

def messages_html(period, data):
    ''' Template for previous messages_<period>.html '''
    return(f'''
        <!DOCTYPE html>
        <html lang="en">
            {head()}
            <body>
                <header>
                    <h1><a href="index.html">{config.HEADER}</a></h1>
                </header>
                <main>
                    <h3>Message history '{period}'</h3>
                    {messages_table(data)}
                    <div id="message"></div>
                </main>
                {footer()}
            </body>
        </html>
    ''')


def plots_all_html(periods):
    ''' Template for all_plots.html '''
    return(f'''
        <!DOCTYPE html>
        <html lang="en">
            {head()}
            <body>
                <header>
                    <h1><a href="index.html">{config.HEADER}</a></h1>
                </header>
                <main>
                    <h3>All Plots</h3>
                    {''.join(f' \
                            {f'<details><summary>{period.capitalize()}</summary>' if period != period[i-1] else ''} \
                            {''.join(f' \
                                <p><a href="plot/{period}_{plot}.html">{period.capitalize()} - {config.PLOTS[plot]['name']}</a></p>\n' \
                                    for j, plot in enumerate(config.PLOTS))} \
                            {'</details>' if i != period[i-1] else ''}' \
                        for i, period in enumerate(periods)) }
                </main>
                {footer()}
            </body>
        </html>
    ''')


def _plot_types_index():
    return {''.join(f'<p>{plot_html('today', plot)}</p>' \
        for plot in config.INDEX_PLOT_TYPES) }

def _plot_link_yesterday():
    return {''.join(f' \
        <details> \
            <summary><span id="plot_period">Yesterday</span></summary> \
            {''.join(plot_html('yesterday', plot) for plot in config.LINK_PLOT_TYPES)} \
        </details>') }

def _plot_link_period():
    return {''.join(f' \
        {'\n' if i == len(config.LINK_PLOT_PERIODS)-1 and j == 0 else ''} \
                <p><a href="plot/{period}_{plot}.html">{period.capitalize()} - {config.PLOTS[plot]['name']}</a></p>\n' \
            for i, period in enumerate(config.LINK_PLOT_PERIODS) \
        for j, plot in enumerate(config.LINK_PLOT_TYPES)) }

def _plot_num():
    return {''.join(f' \
            {'<article>' if j==0 else ''} \
            <p><a href="plot/{period}_{plot}.html">{period.capitalize()} - {config.PLOTS[plot]['name']}</a></p>\n \
            {'</article>' if j==len(config.LINK_PLOT_TYPES)-1 else ''}' \
            for i, period in enumerate(config.LINK_PLOT_PERIODS) \
            for j, plot in enumerate(config.LINK_PLOT_TYPES)) }
