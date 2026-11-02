import config
import message
import helper


''' HTML Templates '''


def index_html(data):
    ''' Template for index.html '''
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
                        {'' if not data.get('collector') else
                        f'<img src="static/collector.svg" class="icon" /> Collector \
                            <ul> \
                                <li>Current Work Time: {data.get('collector_work_time')} hours</li> \
                                <li>Total Work Time: {data.get('collector_total_time')}</li> \
                            </ul> \
                        '}
                        {'' if not data.get('inverter') else
                        f'<img src="static/inverter.svg" class="icon" /> Inverter \
                            <ul> \
                                <li>Time: {data.get('inverter_date_str')} {data.get('inverter_time_str')}</li> \
                                <li>Temperature: {data.get('inverter_temp')} °C</li> \
                                <li>Current State: {data.get('inverter_state')}</li> \
                                {_inverter_warning_notice(data.get('inverter_warning'))} \
                            </ul> \
                        '}  
                    </article>
                    <h4>Real-time Information</h4>
                    <article>
                        <p>
                            <img src="static/electricity.svg" class="icon" />DC Total Power:
                            <strong>
                                {data.get('inverter_dc_totalpower')}
                            </strong>
                        </p>
                        <p>
                            <img src="static/apower.svg" class="icon" />Apparent Power:
                            <strong>{data.get('inverter_apparent_power')}</strong>
                        </p>
                        <p>
                            <img src="static/happy.svg" class="icon" /> Energy Yield Today:
                            <strong>{data.get('inverter_e_today')}</strong>
                        </p>
                        <p></p> 
                    </article>
                    <h4>Energy Yield Totals</h4>
                    <article>
                        <ul>
                            <li>Yesterday: {data.get('inverter_e_yesterday')}</li>
                            <li>This Month: {data['inverter'].get('E_MONTH')} kWh</li>
                            <li>This Year: {data['inverter'].get('E_YEAR')} kWh</li>
                            <li>Total: {data['inverter'].get('E_TOTAL')} kWh</li>
                        </ul>
                    </article>
                    <p>&nbsp;</p>
                    <h4>Graphs</h4>
                    <details open> 
                        <summary><span id="plot_period">Today</span></summary>
                        {_plot_index()}
                    </details>
                    <article>
                        {_plot_links()}
                        <p><a class="button" href="plots_all.html">Show All</a></p>
                    </article>
                    <p>&nbsp;</p>
                        <h4>Messages</h4>
                        {''.join(f' \
                            <details>\n \
                                <summary>\n \
                                    <span>{period.capitalize()}</span>\n \
                                </summary>\n \
                                <table>\n \
                                    {message_table_header()} \
                                    {_message_table_rows(data.get(period, {}))} \
                                </table>\n \
                            </details>\n' \
                            for period in ['today'])}
                        <div id="message"></div>
                        <article>
                            {_message_links()}
                        </article>
                </main>
                {footer()}
                <script type="text/javascript">
                    lastUpdated("{data.get('inverter_dt_obj')}")
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
                    <table>
                        {message_table_header()}
                        {_message_table_rows(data)}
                    </table>
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
                    {_all_plots_links(periods)}
                </main>
                {footer()}
            </body>
        </html>
    ''')


''' HTML Elements '''


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
            <p>Page generated on {helper.fmt_date_time()} {'(db=1)' if config.USE_DATABASE else ''} </p>
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


def message_table_header():
    return('''
        <tr>
            <th>Datetime</th>
            <th>Yield (kWh)</th>
            <th>Power (kW)</th>
            <th>Message</th>
        </tr>
    ''')


''' HTML helper functions '''


def _message_table_rows(data):
    return(f''' 
        {''.join(f' \
            <tr>\n \
                <td>{k}</td>\n \
                {''.join( \
                    '<td>' \
                        f'{helper.divide(message.inverter_notification(v)[field], config.PLOTS[field]['div'], 0) \
                        if message.inverter_notification(v) else None}' \
                    '</td>\n' for field in config.PLOT_TYPES)} \
                {'<td>-</td>\n' if not config.STORE_FILES else \
                    f'<td>' \
                        f'<a href="#" onclick=\'fetchJSONData("{v.get('fn')}", "html", true)\'> html</a> | \n'
                        '<a href="#" onclick=\'document.getElementById("message").innerHTML =' \
                            f'`<pre>${{fetchJSONData("{v.get('fn')}", "pretty", false)}}</pre>`\'>json</a>' \
                    '</td>\n' } \
            </tr>\n' \
        for k, v in data.items()) }
    ''')

def _inverter_warning_notice(inverter_warning):
    return(f' \
            <p class="notice">⚠️ <mark><strong>WARNING:</strong></mark> {inverter_warning}</p>'
        if inverter_warning else ''
    )

def _plot_index():
    return ''.join(f' \
           {helper.plot_html('today', plot)}' \
        for plot in config.INDEX_PLOT_TYPES
    )

def _plot_links():
    return ''.join(f' \
        <p>📈 <a href="{config.PLOTDIR}/{period}_{plot}.html">{period.capitalize()} - {config.PLOTS[plot]['name']}</a></p>\n' \
            for period in [p for p in config.PERIODS if p != 'today'] \
        for plot in config.PLOT_TYPES
    )


def _message_links():
    return ''.join(f' \
        <p> 🔗 <a href="messages_{period}.html">Show {period.capitalize()} </a></p>' \
        for period in [p for p in config.PERIODS if p != 'today']
    )


def _all_plots_links(periods):
    return ''.join(f' \
        {f'<details><summary>{period.capitalize()}</summary>'} \
        {''.join(f' \
            <p><a href="{config.PLOTDIR}/{period}_{plot}.html">{period.capitalize()} - {config.PLOTS[plot]['name']}</a></p>\n' \
                for plot in config.PLOTS)} \
            </details>' \
        for period in periods
    )

#unused
def _plot_types_index():
    return {''.join(f' \
        <p>{helper.plot_html('today', plot)}</p>' for plot in config.INDEX_PLOT_TYPES)
    }

#unused
def _plot_link_yesterday():
    return {''.join(f' \
        <details> \
            <summary><span>Yesterday</span></summary> \
            {''.join(helper.plot_html('yesterday', plot) for plot in config.PLOT_TYPES)} \
        </details>')
    }

#unused
def _plot_link_period():
    return {''.join(f' \
        {'\n' if i == len(config.PERIODS)-1 and j == 0 else ''} \
                <p><a href="{config.PLOTDIR}/{period}_{plot}.html">{period.capitalize()} - {config.PLOTS[plot]['name']}</a></p>\n' \
            for i, period in enumerate(config.PERIODS) \
        for j, plot in enumerate(config.PLOT_TYPES))
}

def _plot_num():
    return {''.join(f' \
                {'<article>' if j==0 else ''} \
                    <p><a href="{config.PLOTDIR}/{period}_{plot}.html">{period.capitalize()} - {config.PLOTS[plot]['name']}</a></p>\n \
                {'</article>' if j==len(config.PLOT_TYPES)-1 else ''}' \
            for i, period in enumerate(config.PERIODS) \
        for j, plot in enumerate(config.PLOT_TYPES))
    }

