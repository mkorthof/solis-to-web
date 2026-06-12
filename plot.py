import config
import helper
import message

from operator import ge
import plotly.express as px
import re


def plot(period):
    ''' Create plot and export to html file

        alternative export methods:
            plotly.offline.plot(fig, filename=f'{config.WEBDIR}/plot_{period}.html', auto_open=False)
            fig.write_html(f'{config.WEBDIR}/plot.html', include_plotlyjs='cdn')    
            fig.to_html(include_plotlyjs='directory', full_html=False)
 '''
    #print(f'DEBUG: plot pattern={pattern} period={period}')
    if not period:
        print('ERROR: plot - missing "period" parameter')
        return
    data = message.previous(period)
    for pt_key, pt_val in config.PLOT_TYPES.items():
        plot_fn = f'plot_{pt_key}_{period}.html'
        if not helper.is_valid_filename(plot_fn):
            continue
        try:
            fig = px.line(px.data.stocks(),
                            x=list(data.keys()),
                            y=[v[pt_key] for k, v in data.items()],
                            title=f'{pt_val['name']} - {period.capitalize()}')
            fig.update_layout(xaxis_title='',
                            yaxis_title=pt_val['unit'],
                            font_size=10,
                            paper_bgcolor='rgba(255,255,255, 0)')
            fig.update_traces(line_color=pt_val['color'])
            fig.write_html(f'{config.WEBDIR}/{plot_fn}', include_plotlyjs='static/plotly.min.js', full_html=False)
        except Exception as e:
            print(f'ERROR: generating {pt_key} plot "{period.capitalize()}" - "{e}"') 
            with open(f'{config.WEBDIR}/{plot_fn}', 'w', encoding='utf-8', errors='ignore') as f_plot:
                f_plot.write(f'❌ Error occurred while generating {pt_key} plot for "{period.capitalize()}"') 
