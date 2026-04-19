from dash import dcc, html

def create_result_panels():
    """Создает панели для отображения результатов с дополнительными графиками"""
    return html.Div([
        # Сообщение о статусе вычислений
        html.Div(id='status-message', style={'textAlign': 'center', 'margin': '10px'}),
        
        # Сообщение об ошибке
        html.Div(id='error-message', style={'textAlign': 'center', 'color': '#c0392b', 'fontSize': '1.1em', 'margin': '10px'}),
        
        # Основной график решения
        html.Div([
            html.H3('График решения', style={'color': '#1a5276'}),
            dcc.Graph(id='volterra-graph'),
        ], style={'padding': '10px'}),
        
        # График ошибки
        html.Div([
            html.H3('Анализ ошибки', style={'color': '#1a5276'}),
            dcc.Graph(id='error-plot'),
        ], style={'padding': '10px', 'marginTop': '20px'}),
        
        # Информация об ошибке
        html.Div(id='error-output', style={'textAlign': 'center', 'fontSize': '1.1em', 'marginTop': '20px', 'color': '#333'}),
        
        # Секция: Анализ ядра
        html.Div([
            html.H3('Анализ ядра K(x,t)', style={'color': '#1a5276', 'marginBottom': '20px'}),
            
            # Сечения ядра при фиксированных t
            html.Div([
                html.H4('Сечения ядра K(x,t) при фиксированных t', style={'color': '#2980b9'}),
                dcc.Graph(id='kernel-sections-plot'),
            ], style={'marginBottom': '30px'}),
            
            # 3D поверхность ядра
            html.Div([
                html.H4('3D поверхность ядра', style={'color': '#2980b9'}),
                dcc.Graph(id='kernel-3d-plot'),
            ], style={'marginBottom': '30px'}),
        ], style={'padding': '20px', 'backgroundColor': '#f5f5f5', 'borderRadius': '10px', 'margin': '10px'}),
        
        # Секция: Разность φ(x) - f(x) (вклад интеграла)
        html.Div([
            html.H3('Разность φ(x) - f(x) (вклад интеграла)', style={'color': '#1a5276', 'marginBottom': '20px'}),
            dcc.Graph(id='difference-plot'),
        ], style={'padding': '20px', 'backgroundColor': '#f5f5f5', 'borderRadius': '10px', 'margin': '10px'}),
        
        # Хранилище для времени вычислений
        dcc.Store(id='computation-time', data=0),
    ])