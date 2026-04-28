from dash import dcc, html

def create_result_panels():
    return html.Div([
        html.Div(id='status-message', className='status-message'),
        html.Div(id='error-message', className='error-message', style={'display': 'none'}),
        
        # Блок аналитической формулы решения
        html.Div([
            html.Div([
                html.H3('Аналитическое представление решения φ(x)', 
                       className='text-center',
                       style={'marginBottom': '15px', 'color': '#2C3E50'}),
                
                html.Div(id='analytical-solution-display',
                        style={
                            'background': 'linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%)',
                            'border': '2px solid #2C3E50',
                            'borderRadius': '12px',
                            'padding': '20px',
                            'margin': '10px auto',
                            'textAlign': 'center',
                            'fontFamily': 'monospace',
                            'fontSize': '1.2em',
                            'boxShadow': '0 4px 12px rgba(0,0,0,0.1)',
                            'overflowX': 'auto'
                        }),
                
                html.Div(id='guess-accuracy',
                        style={
                            'textAlign': 'center',
                            'marginTop': '10px',
                            'color': '#7F8C8D',
                            'fontSize': '0.9em',
                            'fontStyle': 'italic'
                        }),
            ], className='graph-card', style={'marginBottom': '20px', 'padding': '20px'})
        ]),
        
        html.Div([
            html.Div([
                html.H3('График решения φ(x)', className='text-center'),
                dcc.Graph(id='volterra-graph', config={'responsive': True, 'displayModeBar': True}, 
                         style={'height': '400px', 'width': '100%'}),
                html.Div(id='solution-error-info', style={'textAlign': 'center', 'marginTop': '10px'})
            ], className='graph-card', style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),
            
            html.Div([
                html.H3('Производная φ\'(x)', className='text-center'),
                dcc.Graph(id='derivative-plot', config={'responsive': True, 'displayModeBar': True}, 
                         style={'height': '400px', 'width': '100%'}),
            ], className='graph-card', style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        ], style={'marginBottom': '30px', 'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-between'}),
        
        html.Div([
            html.Div([
                html.H3('Сечения ядра K(x,t)', className='text-center', 
                       style={'marginBottom': '15px', 'color': '#2C3E50'}),
                
                html.Div([
                    html.Div([
                        html.Label('x:', style={'fontWeight': 'bold', 'fontSize': '0.85em'}),
                        html.Div([
                            dcc.Input(
                                id='sections-x-min',
                                type='number',
                                value=0,
                                step=0.1,
                                style={'width': '50px', 'marginRight': '5px', 'padding': '4px', 'borderRadius': '4px', 'border': '1px solid #D1D9E6'}
                            ),
                            html.Span('—'),
                            dcc.Input(
                                id='sections-x-max',
                                type='number',
                                value=1,
                                step=0.1,
                                style={'width': '50px', 'marginLeft': '5px', 'padding': '4px', 'borderRadius': '4px', 'border': '1px solid #D1D9E6'}
                            ),
                        ], style={'display': 'inline-flex', 'alignItems': 'center', 'flexWrap': 'wrap', 'gap': '5px'})
                    ], style={'display': 'inline-block', 'marginRight': '15px', 'marginBottom': '10px'}),
                    
                    html.Button(
                        html.Img(
                            src='/assets/load-icon.png',
                            style={
                                'width': '20px',
                                'height': '20px',
                                'display': 'block',
                            }
                        ),
                        id='update-sections-btn',
                        style={
                           'background': '#FFFFFF',
                            'padding': '6px 10px',
                            'border': 'none',
                            'borderRadius': '5px',
                            'cursor': 'pointer',
                            'verticalAlign': 'top',
                            'display': 'inline-flex',
                            'alignItems': 'center',
                            'justifyContent': 'center'
                        },
                        title="Обновить график сечений"
                    ),
                ], style={'textAlign': 'center', 'padding': '8px', 'backgroundColor': '#F8FAFC', 'borderRadius': '8px', 'marginBottom': '15px'}),
                
                dcc.Graph(id='kernel-sections-plot', config={'responsive': True, 'displayModeBar': True}, 
                         style={'height': '450px', 'width': '100%'}),
                
            ], className='graph-card', style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),
            
            html.Div([
                html.H3('3D поверхность ядра K(x,t)', className='text-center', 
                       style={'marginBottom': '15px', 'color': '#2C3E50'}),
                
                html.Div([
                    html.Div([
                        html.Label('x:', style={'fontWeight': 'bold', 'fontSize': '0.85em'}),
                        html.Div([
                            dcc.Input(
                                id='surf-x-min',
                                type='number',
                                value=0,
                                step=0.1,
                                style={'width': '50px', 'marginLeft': '5px', 'marginRight': '5px', 'padding': '4px', 'borderRadius': '4px', 'border': '1px solid #D1D9E6'}
                            ),
                            html.Span('—'),
                            dcc.Input(
                                id='surf-x-max',
                                type='number',
                                value=1,
                                step=0.1,
                                style={'width': '50px', 'marginLeft': '5px', 'marginRight': '15px', 'padding': '4px', 'borderRadius': '4px', 'border': '1px solid #D1D9E6'}
                            ),
                        ], style={'display': 'inline-flex', 'alignItems': 'center', 'flexWrap': 'wrap', 'gap': '5px'})
                    ], style={'display': 'inline-block', 'marginBottom': '10px'}),
                    
                    html.Div([
                        html.Label('t:', style={'fontWeight': 'bold', 'fontSize': '0.85em'}),
                        html.Div([
                            dcc.Input(
                                id='surf-t-min',
                                type='number',
                                value=0,
                                step=0.1,
                                style={'width': '50px', 'marginLeft': '5px', 'marginRight': '5px', 'padding': '4px', 'borderRadius': '4px', 'border': '1px solid #D1D9E6'}
                            ),
                            html.Span('—'),
                            dcc.Input(
                                id='surf-t-max',
                                type='number',
                                value=1,
                                step=0.1,
                                style={'width': '50px', 'marginLeft': '5px', 'marginRight': '15px', 'padding': '4px', 'borderRadius': '4px', 'border': '1px solid #D1D9E6'}
                            ),
                        ], style={'display': 'inline-flex', 'alignItems': 'center', 'flexWrap': 'wrap', 'gap': '5px'})
                    ], style={'display': 'inline-block', 'marginBottom': '10px'}),
                    
                    html.Button(
                        html.Img(
                            src='/assets/load-icon.png',
                            style={
                                'width': '20px',
                                'height': '20px',
                                'display': 'block',
                            }
                        ),
                        id='update-surf-btn',
                        style={
                            'background': '#FFFFFF',
                            'padding': '6px 10px',
                            'border': 'none',
                            'borderRadius': '5px',
                            'cursor': 'pointer',
                            'verticalAlign': 'top',
                            'display': 'inline-flex',
                            'alignItems': 'center',
                            'justifyContent': 'center'
                        },
                        title="Обновить 3D график"
                    ),
                ], style={'textAlign': 'center', 'padding': '8px', 'backgroundColor': '#F8FAFC', 'borderRadius': '8px', 'marginBottom': '15px'}),
                
                dcc.Graph(id='kernel-3d-plot', config={'responsive': True, 'displayModeBar': True}, 
                         style={'height': '450px', 'width': '100%'}),
                
            ], className='graph-card', style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        ], style={'marginBottom': '20px', 'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-between'}),
        
        html.Div(id='max-error-display', style={'clear': 'both', 'paddingTop': '20px'}),
        
        html.Div(id='error-output', className='error-text', style={'display': 'none'}),
        dcc.Store(id='computation-time', data=0),
        dcc.Store(id='numerical-solution-data', data={}),
    ])