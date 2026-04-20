from dash import dcc, html

def create_result_panels():
    """Создает панели для отображения результатов с дополнительными графиками"""
    return html.Div([
        # Сообщение о статусе вычислений
        html.Div(id='status-message', style={'textAlign': 'center', 'margin': '10px'}),
        
        # Сообщение об ошибке
        html.Div(id='error-message', style={'textAlign': 'center', 'color': '#c0392b', 'fontSize': '1.1em', 'margin': '10px'}),
        
        # Графики в 2 ряда
        html.Div([
            # Первый ряд графиков
            html.Div([
                html.Div([
                    html.H3('График решения φ(x)', style={'color': '#1a5276', 'textAlign': 'center'}),
                    dcc.Graph(id='volterra-graph', config={'responsive': True}),
                ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px', 
                         'border': '2px solid #a8d5e8', 'borderRadius': '10px', 
                         'marginRight': '2%', 'verticalAlign': 'top', 'backgroundColor': '#fff'}),
                
                html.Div([
                    html.H3('Производная φ\'(x)', style={'color': '#1a5276', 'textAlign': 'center'}),
                    dcc.Graph(id='derivative-plot', config={'responsive': True}),
                ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px', 
                         'border': '2px solid #a8d5e8', 'borderRadius': '10px', 
                         'verticalAlign': 'top', 'backgroundColor': '#fff'}),
            ], style={'marginBottom': '20px'}),
            
            # Второй ряд графиков
            html.Div([
                html.Div([
                    html.H3('Сечения ядра K(x,t)', style={'color': '#1a5276', 'textAlign': 'center'}),
                    dcc.Graph(id='kernel-sections-plot', config={'responsive': True}),
                ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px', 
                         'border': '2px solid #a8d5e8', 'borderRadius': '10px', 
                         'marginRight': '2%', 'verticalAlign': 'top', 'backgroundColor': '#fff'}),
                
                html.Div([
                    html.H3('3D поверхность ядра', style={'color': '#1a5276', 'textAlign': 'center'}),
                    dcc.Graph(id='kernel-3d-plot', config={'responsive': True}),
                ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px', 
                         'border': '2px solid #a8d5e8', 'borderRadius': '10px', 
                         'verticalAlign': 'top', 'backgroundColor': '#fff'}),
            ], style={'marginBottom': '20px'}),
        ]),
        
        # Информация об ошибке
        html.Div(id='error-output', style={'textAlign': 'center', 'fontSize': '1.1em', 'marginTop': '20px', 'color': '#333'}),
        
        # Хранилище для времени вычислений
        dcc.Store(id='computation-time', data=0),
    ])