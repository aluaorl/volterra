import dash
from dash import html
from components.input_panel import create_input_panel
from components.result_panels import create_result_panels
from components.history_panel import create_history_panel
from components.callbacks import register_callbacks

app = dash.Dash(__name__, suppress_callback_exceptions=True, assets_folder='assets')
server = app.server

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Решатель ИДУ Вольтерра</title>
        {%favicon%}
        {%css%}
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = html.Div(children=[
    html.H1(children='Решатель ИДУ Вольтерра', className='app-title'),
    create_input_panel(),
    create_result_panels(),
    create_history_panel(),
], id='main-container', className='app-container')

register_callbacks(app)

if __name__ == '__main__':
    app.run(debug=True)