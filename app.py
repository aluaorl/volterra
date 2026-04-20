import dash
from dash import html, dcc
from components.input_panel import create_input_panel
from components.result_panels import create_result_panels
from components.history_panel import create_history_panel
from components.callbacks import register_callbacks

# Инициализация Dash приложения с suppress_callback_exceptions=True
app = dash.Dash(__name__, external_stylesheets=['/assets/custom.css'], suppress_callback_exceptions=True)

# Компоновка приложения
app.layout = html.Div(children=[
    html.H1(children='Решатель интегро-дифференциального уравнения Вольтерра II рода', 
            style={'textAlign': 'center', 'color': '#1a5276'}),
    
    html.Div(
        "φ'(x) = f(x) + ∫₀ˣ K(x,t)·φ(t) dt",
        style={'textAlign': 'center', 'fontSize': '1.2em', 'color': '#2980b9', 'marginBottom': '20px', 'fontFamily': 'monospace'}
    ),
    
    create_input_panel(),
    create_result_panels(),
    create_history_panel(),
], id='main-container')

# Регистрация всех callbacks
register_callbacks(app)

if __name__ == '__main__':
    app.run(debug=True)