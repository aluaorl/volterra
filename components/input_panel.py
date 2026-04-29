from dash import dcc, html
from config import KERNEL_EXAMPLES, RHS_EXAMPLES

def create_input_panel():
    return html.Div([
        dcc.Store(id='legend-state', data={'expanded': False}),
        dcc.Store(id='kernel-examples-state', data={'expanded': False}),
        dcc.Store(id='rhs-examples-state', data={'expanded': False}),
        
        html.Div([
            html.Div([
                html.Label('Ядро K(x,t):', style={'fontWeight': 'bold'}),
                dcc.Textarea(
                    id='kernel-input',
                    placeholder='Введите выражение для ядра K(x,t)',
                    value='0.2 * exp(-(x - t))',
                    style={'width': '100%', 'height': '60px', 'resize': 'vertical'}
                ),
                html.Div([
                    html.Div('▼ Примеры ядер K(x,t):', className='example-toggle', id='kernel-examples-toggle'),
                    html.Div(id='kernel-examples-content', style={'display': 'none'},
                        children=[html.Button(name, id={'type': 'kernel-example', 'index': i}, 
                                             className='example-button')
                                  for i, name in enumerate(KERNEL_EXAMPLES.keys())])
                ], style={'padding': '8px 12px', 'backgroundColor': '#FFFFFF', 'borderRadius': '8px', 
                         'border': '1px solid #D1D9E6', 'marginTop': '10px'})
            ], className='input-card', style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%'}),
            
            html.Div([
                html.Label('Правая часть f(x):', style={'fontWeight': 'bold'}),
                dcc.Textarea(
                    id='rhs-input',
                    placeholder='Введите выражение для правой части f(x)',
                    value='sin(x)',
                    style={'width': '100%', 'height': '60px', 'resize': 'vertical'}
                ),
                html.Div([
                    html.Div('▼ Примеры правых частей f(x):', className='example-toggle', id='rhs-examples-toggle'),
                    html.Div(id='rhs-examples-content', style={'display': 'none'},
                        children=[html.Button(name, id={'type': 'rhs-example', 'index': i}, 
                                             className='example-button')
                                  for i, name in enumerate(RHS_EXAMPLES.keys())])
                ], style={'padding': '8px 12px', 'backgroundColor': '#FFFFFF', 'borderRadius': '8px', 
                         'border': '1px solid #D1D9E6', 'marginTop': '10px'})
            ], className='input-card', style={'width': '48%', 'display': 'inline-block'})
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'padding': '15px', 'flexWrap': 'wrap'}),
        
        html.Div([
            html.Label('Начальное условие φ(0):'),
            dcc.Input(id='initial-condition', type='number', value=0.0, step=0.1,
                     style={'width': '120px', 'padding': '6px', 'textAlign': 'center'})
        ], style={'padding': '15px 20px', 'display': 'inline-block'}),

        html.Div(id='equation-display', style={'marginTop': '5px', 'overflowX': 'auto'}),
        
        html.Div([
            html.Div([
                html.H5('▼ Поддерживаемые функции и константы:', id='legend-toggle', 
                       style={'marginBottom': '8px', 'cursor': 'pointer'}),
                html.Div(id='legend-content', style={'display': 'none'}, children=[
                    html.P('✓ Ввод распознает синонимы функций, как asin, arsin, arcsin',
                          style={'margin': '0 0 10px 0', 'color': '#7F8C8D', 'fontSize': '0.8em'}),
                           html.Div([
                        html.Div([
                            html.H6('Тригонометрические и обратные:', 
                                   style={'color': '#34495E', 'marginBottom': '5px', 'fontSize': '0.85em', 'fontWeight': 'bold'}),
                            html.P('sin, cos, tan, tg, cot, ctg, sec, csc, cosec', 
                                   style={'margin': '0 0 8px 0', 'fontSize': '0.8em', 'color': '#2C3E50'}),
                            html.P('arcsin, arccos, arctan, arctg, arccot, arcsec, arccsc', 
                                   style={'margin': '0 0 12px 0', 'fontSize': '0.8em', 'color': '#2C3E50'}),
                            
                            html.H6('Гиперболические и обратные:', 
                                   style={'color': '#34495E', 'marginBottom': '5px', 'fontSize': '0.85em', 'fontWeight': 'bold'}),
                            html.P('sinh, sh, cosh, ch, tanh, th, coth, cth, sech, csch', 
                                   style={'margin': '0 0 8px 0', 'fontSize': '0.8em', 'color': '#2C3E50'}),
                            html.P('arsinh, arcosh, artanh, arcoth, arsech, arcsch', 
                                   style={'margin': '0 0 12px 0', 'fontSize': '0.8em', 'color': '#2C3E50'}),
                            
                            html.H6('Логарифмы:', 
                                   style={'color': '#34495E', 'marginBottom': '5px', 'fontSize': '0.85em', 'fontWeight': 'bold'}),
                            html.P('ln, lg, log, log(a, x)', 
                                   style={'margin': '0 0 12px 0', 'fontSize': '0.8em', 'color': '#2C3E50'}),
                        ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingRight': '10px'}),
                        
                        html.Div([
                            html.H6('Степени и корни:', 
                                   style={'color': '#34495E', 'marginBottom': '5px', 'fontSize': '0.85em', 'fontWeight': 'bold'}),
                            html.P('x^2, x**2, sqrt, sqrt(n, x)', 
                                   style={'margin': '0 0 12px 0', 'fontSize': '0.8em', 'color': '#2C3E50'}),
                            
                            html.H6('Модуль и экспонента:', 
                                   style={'color': '#34495E', 'marginBottom': '5px', 'fontSize': '0.85em', 'fontWeight': 'bold'}),
                            html.P('abs(x), exp(x), e^x', 
                                   style={'margin': '0 0 12px 0', 'fontSize': '0.8em', 'color': '#2C3E50'}),
                            
                            
                        ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingRight': '10px'}),
                        html.Div([
                            html.H6('Константы:', 
                                   style={'color': '#34495E', 'marginBottom': '5px', 'fontSize': '0.85em', 'fontWeight': 'bold'}),
                            html.P('pi, π, e', 
                                   style={'margin': '0 0 12px 0', 'fontSize': '0.8em', 'color': '#2C3E50'}),
                        ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                    ], style={'display': 'flex', 'flexWrap': 'wrap'})
                ]),
            ], style={'padding': '12px', 'backgroundColor': '#FFFFFF', 'borderRadius': '8px', 'marginTop': '15px', 'border': '1px solid #D1D9E6'})
        ]),
        
        html.Button('Решить уравнение', id='solve-button', disabled=True),
        
        html.Div([
            html.Div(className='loader'),
            html.P('Вычисление... Пожалуйста, подождите', style={'textAlign': 'center', 'marginTop': '10px'})
        ], id='loading-indicator', style={'display': 'none', 'marginTop': '20px', 'textAlign': 'center'})
    ])