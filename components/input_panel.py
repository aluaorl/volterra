from dash import dcc, html

# Примеры и подсказки для пользователя
KERNEL_EXAMPLES = {
    "Экспоненциальное": "0.2 * exp(-(x - t))",
    "Косинусоидальное": "0.3 * cos(x - t)",
    "Параболическое": "0.1 * (x - t)^2",
    "Синусоидальное": "0.25 * sin(x + t)",
    "Модифицированное экспоненциальное": "0.15 * exp(-abs(x - t))"
}

RHS_EXAMPLES = {
    "Синус": "sin(x)",
    "Косинус двойного аргумента": "cos(2*x)",
    "Парабола": "x * (1-x)",
    "Экспонента": "exp(-x)",
    "Синусоида": "sin(pi*x)"
}

def create_input_panel():
    """Создает панель ввода параметров"""
    return html.Div([
        html.Div([
            html.Div([
                html.Label('Ядро K(x,t):', style={'fontWeight': 'bold', 'fontSize': '1.1em'}),
                dcc.Textarea(
                    id='kernel-input',
                    placeholder='Введите выражение для ядра K(x,t) (используйте x и t как переменные)\nНапример: 0.2 * exp(-(x - t)) или 0.2*exp(-(x-t))',
                    value='0.2 * exp(-(x - t))',
                    n_blur=0,
                    style={
                        'width': '100%',
                        'height': '100px',
                        'fontFamily': 'monospace',
                        'fontSize': '14px',
                        'padding': '10px',
                        'borderRadius': '5px',
                        'border': '2px solid #bdc3c7'
                    }
                ),
                html.Div(id='kernel-validation', style={'color': '#e74c3c', 'fontSize': '0.85em', 'marginTop': '5px'}),
                html.Div([
                    html.Span('Примеры: ', style={'fontWeight': 'bold', 'marginRight': '10px'}),
                    html.Div([
                        html.Button(name, id={'type': 'kernel-example', 'index': i}, 
                                   style={'margin': '2px', 'padding': '5px 10px', 
                                          'backgroundColor': '#ecf0f1', 'border': 'none',
                                          'borderRadius': '3px', 'cursor': 'pointer'})
                        for i, name in enumerate(KERNEL_EXAMPLES.keys())
                    ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '5px'})
                ], style={'marginTop': '10px', 'padding': '10px', 'backgroundColor': '#f8f9fa', 
                         'borderRadius': '5px'})
            ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),
            
            html.Div([
                html.Label('Правая часть f(x):', style={'fontWeight': 'bold', 'fontSize': '1.1em'}),
                dcc.Textarea(
                    id='rhs-input',
                    placeholder='Введите выражение для правой части f(x) (используйте x как переменную)\nНапример: sin(x) или sinx',
                    value='sin(x)',
                    n_blur=0,
                    style={
                        'width': '100%',
                        'height': '100px',
                        'fontFamily': 'monospace',
                        'fontSize': '14px',
                        'padding': '10px',
                        'borderRadius': '5px',
                        'border': '2px solid #bdc3c7'
                    }
                ),
                html.Div(id='rhs-validation', style={'color': '#e74c3c', 'fontSize': '0.85em', 'marginTop': '5px'}),
                html.Div([
                    html.Span('Примеры: ', style={'fontWeight': 'bold', 'marginRight': '10px'}),
                    html.Div([
                        html.Button(name, id={'type': 'rhs-example', 'index': i},
                                   style={'margin': '2px', 'padding': '5px 10px',
                                          'backgroundColor': '#ecf0f1', 'border': 'none',
                                          'borderRadius': '3px', 'cursor': 'pointer'})
                        for i, name in enumerate(RHS_EXAMPLES.keys())
                    ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '5px'})
                ], style={'marginTop': '10px', 'padding': '10px', 'backgroundColor': '#f8f9fa',
                         'borderRadius': '5px'})
            ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        ], style={'padding': '20px'}),
        
        html.Div([
            html.Label('Количество точек N:', style={'fontWeight': 'bold'}),
            dcc.Slider(
                id='n-slider',
                min=50,
                max=500,
                step=50,
                value=200,
                marks={i: str(i) for i in range(50, 501, 50)},
                tooltip={"placement": "bottom", "always_visible": True}
            ),
        ], style={'padding': '20px'}),
        
        # Красивое отображение уравнения
        html.Div([
            html.H4('📝 Решаемое уравнение:', style={'color': '#2c3e50', 'marginBottom': '10px'}),
            html.Div(id='equation-display', 
                     style={'padding': '15px', 'backgroundColor': '#e8f4f8', 
                            'borderRadius': '8px', 'fontFamily': 'monospace', 
                            'fontSize': '1.2em', 'textAlign': 'center',
                            'borderLeft': '4px solid #3498db'}),
        ], style={'padding': '20px', 'marginTop': '10px'}),
        
        # Легенда функций
        html.Div([
            html.Div([
                html.H5('📖 Поддерживаемые функции и константы:', 
                        style={'color': '#2c3e50', 'marginBottom': '10px', 'cursor': 'pointer'},
                        id='legend-toggle'),
                html.Div([
                    html.Div([
                        html.Div([
                            html.H6('Тригонометрические:', style={'color': '#e74c3c', 'marginBottom': '5px'}),
                            html.P('sin, cos, tg/tan, ctg/cot, sec, csc/cosec', style={'margin': '0 0 10px 0'}),
                            html.H6('Обратные тригонометрические:', style={'color': '#e74c3c', 'marginBottom': '5px'}),
                            html.P('arcsin/asin/sin^-1, arccos/acos/cos^-1, arctg/atan/tg^-1, arcctg/acot/ctg^-1', 
                                   style={'margin': '0 0 10px 0'}),
                            html.H6('Гиперболические:', style={'color': '#e74c3c', 'marginBottom': '5px'}),
                            html.P('sh/sinh, ch/cosh, th/tanh, cth/coth, sch, csch', style={'margin': '0 0 10px 0'}),
                        ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                        
                        html.Div([
                            html.H6('Обратные гиперболические:', style={'color': '#e74c3c', 'marginBottom': '5px'}),
                            html.P('arsh/asinh, arch/acosh, arth/atanh, arcth', style={'margin': '0 0 10px 0'}),
                            html.H6('Логарифмы и степени:', style={'color': '#e74c3c', 'marginBottom': '5px'}),
                            html.P('ln, lg, log, log2, exp, sqrt/root, abs', style={'margin': '0 0 10px 0'}),
                            html.H6('Константы:', style={'color': '#e74c3c', 'marginBottom': '5px'}),
                            html.P('pi/π, e, α, β, γ, δ, ε, μ, φ, π', style={'margin': '0 0 10px 0'}),
                        ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                        
                        html.Div([
                            html.H6('Особенности ввода:', style={'color': '#e74c3c', 'marginBottom': '5px'}),
                            html.P('• 2sinx → 2*sin(x) - умножение автоматическое', style={'margin': '0 0 5px 0'}),
                            html.P('• sinx → sin(x) - скобки автоматические', style={'margin': '0 0 5px 0'}),
                            html.P('• x^2 или x**2 - степень', style={'margin': '0 0 5px 0'}),
                            html.P('• Регистр не важен - SiNx = sinx', style={'margin': '0 0 5px 0'}),
                        ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                    ])
                ], id='legend-content', style={'display': 'none', 'marginTop': '10px'}),
            ], style={'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '8px', 'marginTop': '20px'}),
        ]),
        
        html.Div([
            html.Button('Решить уравнение', id='solve-button', 
                       style={
                           'backgroundColor': '#3498db',
                           'color': 'white',
                           'padding': '10px 20px',
                           'fontSize': '16px',
                           'border': 'none',
                           'borderRadius': '5px',
                           'cursor': 'pointer',
                           'margin': '10px auto',
                           'display': 'block',
                           'width': '200px'
                       }),
            
            html.Div([
                html.Div(id='loading-indicator', children=[
                    html.Div(style={
                        'border': '4px solid #f3f3f3',
                        'borderTop': '4px solid #3498db',
                        'borderRadius': '50%',
                        'width': '30px',
                        'height': '30px',
                        'animation': 'spin 1s linear infinite',
                        'margin': '0 auto'
                    }),
                    html.P('Вычисление... Пожалуйста, подождите', 
                           style={'textAlign': 'center', 'marginTop': '10px', 'color': '#7f8c8d'})
                ], style={'display': 'none', 'marginTop': '20px'})
            ], style={'textAlign': 'center'})
        ]),
    ])