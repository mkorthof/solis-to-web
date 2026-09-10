import config
import helper

import plotly.express as px


def values(period, plot_key, data):
    ''' Calc values x and y axis '''
    plot_params = config.PLOTS[plot_key]
    if not data:
        print(f'ERROR: plot - missing data for "{period}"')
        return
    # Example:
    #   plot_x = timestamps, plot_y = field values from data (json) e.g.
    #     2026-01-01 12:00:01 {'e_today': '5.5' ... }
    #     2026-01-01 12:05:01 {'e_today': '5.6' ... }
    #plot_x = list(data.keys())
    #plot_y = [vals.get(plot_key) for _, vals in data.items()]
    #plot_x = list(data.keys())
    #vals = [vals.get(plot_key) for _, vals in data.items()]
    # check y for list
    #plot_y = [(y[0]/10 if isinstance(y, list) else y/10) if y else 0 for y in vals]

    # TODO: improve performance / test with with actual pandas dataframe
    # values dict: list
    '''
    values = {
        'x': [],
        'y': []
    }
    for k, v in data.items():
        values['x'].append(datetime.datetime.strptime(k, "%Y-%m-%d %H:%M:%S"))
        values['y'].append(helper.divide(v[plot], 10) if v.get(plot) else 0)
    '''
    # values dict: list (div 10)
    '''
    values = {
        'x': [],
        'y': []
    }
    for k, v in data.items():
        values['x'].append(k)
        values['y'].append(helper.divide(v[plot_key], plot_params.get('div', 10)) if v.get(plot_key) else 0)
    '''

    # values list of dict + sort

    values = []
    for k, v in data.items():
        if v.get(plot_key):
            #v = v[plot_key][0] if isinstance(v[plot_key], list) else v[plot_key]
            #v = helper.divide(v, plot_params.get('div', 10))
            v = helper.divide(
                v[plot_key],
                plot_params.get('div', 10),
                plot_params.get('num', 0)
            )
        else:
            v = 0
        values.append({'x': k, 'y': v})
    # TOOD: sort on ts?
    #if config.STORE == 'files':
    #    values.sort(key=lambda x_date: datetime.datetime.strptime(x_date.get('x', 0), "%Y-%m-%d %H:%M:%S"))
    return values


def write_plot(period, plot_key, values):
    ''' Create plot and export to html file '''
    # Alternative export methods:
    #   plotly.offline.plot(fig, filename=f'{config.WEBDIR}/plot_{period}.html', auto_open=False)
    #   fig.write_html(f'{config.WEBDIR}/plot.html', include_plotlyjs='cdn')    
    #   fig.to_html(include_plotlyjs='directory', full_html=False    
    if not period:
        print('ERROR: plot - missing "period" parameter, skip ')
        return
    plot_params = config.PLOTS[plot_key]
    if plot_params.get('disabled'):
        return
    plot_fn = f'{period}_{plot_key}.html'
    if not helper.is_valid_filename(plot_fn):
        print('ERROR: generating plot (invalid filename)')
        return
    try:
        fig = px.line(
            #x=plot_x,
            #y=plot_y,
            #values,
            # XXX: x needs to be datetime obj or iso date str
            # TODO: convert ts to date time
            # isinstance(k, str) 
            # isinstance(k, datetime.datetime.date):
            # isinstance(k, int): 
            #k = [datetime.datetime.fromtimestamp(v['x']) for v in values],
            x=[v['x'] for v in values],
            y=[v['y'] for v in values],
            title=f'📈 {period.capitalize()} - {plot_params['name']}'
        )
        fig.update_layout(
            xaxis_title='',
            yaxis_title=plot_params['unit'],
            font_size=10,
            paper_bgcolor='rgba(255,255,255, 0)'
        )
        fig.update_traces(connectgaps=False, line_color=plot_params['color'])
        fig.write_html(f'{config.WEBDIR}/plot/{plot_fn}', include_plotlyjs='plotly.min.js', full_html=False)
    except Exception as e:
        print(f'ERROR: plot - "{period} {plot_key}" {e}') 
        with open(f'{config.WEBDIR}/plot/{plot_fn}', 'w', encoding='utf-8', errors='ignore') as f_plot:
            f_plot.write(f'<p>❌ Error occurred while plotting "{period.capitalize()} - {plot_key}"</p>') 
