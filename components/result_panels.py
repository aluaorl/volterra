from dash import dcc, html

def create_result_panels():
    """Создает панели для отображения результатов с дополнительными графиками"""
    return html.Div([
        # Сообщение о статусе вычислений
        html.Div(id='status-message', style={'textAlign': 'center', 'margin': '10px', 'fontFamily': "'Roboto', 'Segoe UI', sans-serif"}),
        
        # Сообщение об ошибке
        html.Div(id='error-message', style={'textAlign': 'center', 'color': '#E74C3C', 'fontSize': '1.1em', 'margin': '10px', 'fontFamily': "'Roboto', 'Segoe UI', sans-serif"}),
        
        # Графики в 2 ряда
        html.Div([
            # Первый ряд графиков
            html.Div([
                html.Div([
                    html.H3('График решения φ(x)', style={'color': '#2C3E50', 'textAlign': 'center', 'fontFamily': "'Roboto', 'Segoe UI', sans-serif"}),
                    dcc.Graph(id='volterra-graph', config={'responsive': True}),
                ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px', 
                         'border': '2px solid #D1D9E6', 'borderRadius': '10px', 
                         'marginRight': '2%', 'verticalAlign': 'top', 'backgroundColor': '#FFFFFF'}),
                
                html.Div([
                    html.H3('Производная φ\'(x)', style={'color': '#2C3E50', 'textAlign': 'center', 'fontFamily': "'Roboto', 'Segoe UI', sans-serif"}),
                    dcc.Graph(id='derivative-plot', config={'responsive': True}),
                ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px', 
                         'border': '2px solid #D1D9E6', 'borderRadius': '10px', 
                         'verticalAlign': 'top', 'backgroundColor': '#FFFFFF'}),
            ], style={'marginBottom': '20px'}),
            
            # Второй ряд графиков
            html.Div([
                html.Div([
                    html.H3('Сечения ядра K(x,t)', style={'color': '#2C3E50', 'textAlign': 'center', 'fontFamily': "'Roboto', 'Segoe UI', sans-serif"}),
                    dcc.Graph(id='kernel-sections-plot', config={'responsive': True}),
                ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px', 
                         'border': '2px solid #D1D9E6', 'borderRadius': '10px', 
                         'marginRight': '2%', 'verticalAlign': 'top', 'backgroundColor': '#FFFFFF'}),
                
                html.Div([
                    html.H3('3D поверхность ядра', style={'color': '#2C3E50', 'textAlign': 'center', 'fontFamily': "'Roboto', 'Segoe UI', sans-serif"}),
                    dcc.Graph(id='kernel-3d-plot', config={'responsive': True}),
                ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px', 
                         'border': '2px solid #D1D9E6', 'borderRadius': '10px', 
                         'verticalAlign': 'top', 'backgroundColor': '#FFFFFF'}),
            ], style={'marginBottom': '20px'}),
        ]),
        
        # Информация об ошибке
        html.Div(id='error-output', style={'textAlign': 'center', 'fontSize': '1.1em', 'marginTop': '20px', 'color': '#E74C3C', 'fontFamily': "'Roboto', sans-serif"}),
        
        # Хранилище для времени вычислений
        dcc.Store(id='computation-time', data=0),
    ])