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
            # Блок для ядра K(x,t) - объединен в одну карточку
            html.Div([
                html.Div([
                    html.Label('Ядро K(x,t):', style={'fontWeight': 'bold', 'fontSize': '1.1em', 'color': '#1a5276', 'marginBottom': '10px', 'display': 'block'}),
                    dcc.Textarea(
                        id='kernel-input',
                        placeholder='Введите выражение для ядра K(x,t) (используйте x и t как переменные)',
                        value='0.2 * exp(-(x - t))',
                        n_blur=0,
                        style={
                            'width': '100%',
                            'height': '60px',
                            'fontFamily': 'monospace',
                            'fontSize': '13px',
                            'padding': '8px',
                            'borderRadius': '5px',
                            'border': '2px solid #a8d5e8',
                            'backgroundColor': '#fff',
                            'transition': 'border-color 0.3s ease'
                        }
                    ),
                    html.Div(id='kernel-validation', style={'color': '#c0392b', 'fontSize': '0.85em', 'marginTop': '5px'}),
                ], style={'marginBottom': '15px'}),
                
                html.Div([
                    html.Div('📋 Примеры ядер K(x,t):', 
                            style={'fontWeight': 'bold', 'marginBottom': '10px', 'color': '#1a5276'}),
                    html.Div([
                        html.Button(
                            name, 
                            id={'type': 'kernel-example', 'index': i},
                            style={
                                'width': '50%',
                                'textAlign': 'left',
                                'margin': '4px 0',
                                'padding': '6px 12px',
                                'fontSize': '12px',
                                'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                'color': 'white',
                                'border': 'none',
                                'borderRadius': '20px',
                                'cursor': 'pointer',
                                'transition': 'transform 0.2s ease, box-shadow 0.2s ease'
                            }
                        )
                        for i, name in enumerate(KERNEL_EXAMPLES.keys())
                    ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'flex-start', 'gap': '6px'})
                ], style={'padding': '12px', 'backgroundColor': '#f8f9fa', 
                         'borderRadius': '10px', 'border': '1px solid #e0e0e0'})
            ], style={
                'width': '48%', 
                'display': 'inline-flex',
                'flexDirection': 'column',
                'marginRight': '2%', 
                'verticalAlign': 'top',
                'padding': '20px',
                'border': '2px solid #a8d5e8',
                'borderRadius': '12px',
                'backgroundColor': '#ffffff',
                'boxShadow': '0 2px 8px rgba(0,0,0,0.05)',
                'minHeight': '400px'
            }),
            
            # Блок для правой части f(x) - объединен в одну карточку
            html.Div([
                html.Div([
                    html.Label('Правая часть f(x):', style={'fontWeight': 'bold', 'fontSize': '1.1em', 'color': '#1a5276', 'marginBottom': '10px', 'display': 'block'}),
                    dcc.Textarea(
                        id='rhs-input',
                        placeholder='Введите выражение для правой части f(x) (используйте x как переменную)',
                        value='sin(x)',
                        n_blur=0,
                        style={
                            'width': '100%',
                            'height': '60px',
                            'fontFamily': 'monospace',
                            'fontSize': '13px',
                            'padding': '8px',
                            'borderRadius': '5px',
                            'border': '2px solid #a8d5e8',
                            'backgroundColor': '#fff',
                            'transition': 'border-color 0.3s ease'
                        }
                    ),
                    html.Div(id='rhs-validation', style={'color': '#c0392b', 'fontSize': '0.85em', 'marginTop': '5px'}),
                ], style={'marginBottom': '15px'}),
                
                html.Div([
                    html.Div('📋 Примеры правых частей f(x):', 
                            style={'fontWeight': 'bold', 'marginBottom': '10px', 'color': '#1a5276'}),
                    html.Div([
                        html.Button(
                            name, 
                            id={'type': 'rhs-example', 'index': i},
                            style={
                                'width': '50%',
                                'textAlign': 'left',
                                'margin': '4px 0',
                                'padding': '6px 12px',
                                'fontSize': '12px',
                                'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                'color': 'white',
                                'border': 'none',
                                'borderRadius': '20px',
                                'cursor': 'pointer',
                                'transition': 'transform 0.2s ease, box-shadow 0.2s ease'
                            }
                        )
                        for i, name in enumerate(RHS_EXAMPLES.keys())
                    ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'flex-start', 'gap': '6px'})
                ], style={'padding': '12px', 'backgroundColor': '#f8f9fa',
                         'borderRadius': '10px', 'border': '1px solid #e0e0e0'})
            ], style={
                'width': '48%', 
                'display': 'inline-flex',
                'flexDirection': 'column',
                'verticalAlign': 'top',
                'padding': '20px',
                'border': '2px solid #a8d5e8',
                'borderRadius': '12px',
                'backgroundColor': '#ffffff',
                'boxShadow': '0 2px 8px rgba(0,0,0,0.05)',
                'minHeight': '400px'
            }),
        ], style={'padding': '20px', 'display': 'flex', 'justifyContent': 'space-between'}),
        
        # Начальное условие
        html.Div([
            html.Label('Начальное условие φ(0):', style={'fontWeight': 'bold', 'color': '#333', 'marginBottom': '10px', 'display': 'block'}),
            dcc.Input(
                id='initial-condition',
                type='number',
                value=0.0,
                step=0.1,
                style={
                    'width': '150px',
                    'padding': '8px',
                    'borderRadius': '5px',
                    'border': '2px solid #a8d5e8',
                    'fontSize': '14px',
                    'textAlign': 'center',
                    'margin': '0 auto',
                    'display': 'block'
                }
            ),
        ], style={'padding': '20px', 'textAlign': 'center'}),
        
        # Красивое отображение уравнения
        html.Div([
            html.Div(id='equation-display', 
                     style={'padding': '12px', 'backgroundColor': '#e8eef2', 
                            'borderRadius': '8px', 'fontFamily': 'monospace', 
                            'fontSize': '1.1em', 'textAlign': 'center',
                            'color': '#333', 'border': '2px solid #a8d5e8'}),
        ], style={'padding': '20px', 'marginTop': '10px'}),
        
        # Легенда функций
        html.Div([
            html.Div([
                html.H5('📖 Поддерживаемые функции и константы:', 
                        style={'color': '#1a5276', 'marginBottom': '10px', 'cursor': 'pointer'},
                        id='legend-toggle'),
                html.Div([
                    html.Div([
                        html.Div([
                            html.H6('Тригонометрические:', style={'color': '#2980b9', 'marginBottom': '5px'}),
                            html.P('sin, cos, tan, cot, sec, csc', style={'margin': '0 0 10px 0', 'color': '#333'}),
                            html.H6('Обратные тригонометрические:', style={'color': '#2980b9', 'marginBottom': '5px'}),
                            html.P('arcsin, arccos, arctan, arccot', 
                                   style={'margin': '0 0 10px 0', 'color': '#333'}),
                            html.H6('Гиперболические:', style={'color': '#2980b9', 'marginBottom': '5px'}),
                            html.P('sinh, cosh, tanh, coth', style={'margin': '0 0 10px 0', 'color': '#333'}),
                        ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                        
                        html.Div([
                            html.H6('Обратные гиперболические:', style={'color': '#2980b9', 'marginBottom': '5px'}),
                            html.P('asinh, acosh, atanh', style={'margin': '0 0 10px 0', 'color': '#333'}),
                            html.H6('Логарифмы и степени:', style={'color': '#2980b9', 'marginBottom': '5px'}),
                            html.P('ln, lg, log, log2, exp, sqrt, abs', style={'margin': '0 0 10px 0', 'color': '#333'}),
                            html.H6('Константы:', style={'color': '#2980b9', 'marginBottom': '5px'}),
                            html.P('pi, e', style={'margin': '0 0 10px 0', 'color': '#333'}),
                        ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                        
                        html.Div([
                            html.H6('Особенности ввода:', style={'color': '#2980b9', 'marginBottom': '5px'}),
                            html.P('2sinx → 2*sin(x) - умножение автоматическое', style={'margin': '0 0 5px 0', 'color': '#333'}),
                            html.P('sinx → sin(x) - скобки автоматические', style={'margin': '0 0 5px 0', 'color': '#333'}),
                            html.P('x^2 или x**2 - степень', style={'margin': '0 0 5px 0', 'color': '#333'}),
                            html.P('Регистр не важен', style={'margin': '0 0 5px 0', 'color': '#333'}),
                        ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                    ])
                ], id='legend-content', style={'display': 'none', 'marginTop': '10px'}),
            ], style={'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px', 'marginTop': '20px', 'border': '1px solid #e0e0e0'}),
        ]),
        
        html.Div([
            html.Button('Решить уравнение', id='solve-button',  disabled=True,
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
                        'border': '4px solid #e0e0e0',
                        'borderTop': '4px solid #3498db',
                        'borderRadius': '50%',
                        'width': '30px',
                        'height': '30px',
                        'animation': 'spin 1s linear infinite',
                        'margin': '0 auto'
                    }),
                    html.P('Вычисление... Пожалуйста, подождите', 
                           style={'textAlign': 'center', 'marginTop': '10px', 'color': '#666'})
                ], style={'display': 'none', 'marginTop': '20px'})
            ], style={'textAlign': 'center'})
        ]),
    ])