from dash import dcc, html

def create_history_panel():
    return html.Div([
        # Кнопка истории
        html.Div(
            html.Div(
                html.Img(src='/assets/history-icon.png', style={'width': '32px', 'height': '32px', 'display': 'block'}),
                id='history-toggle-btn',
                style={
                    'position': 'fixed', 'top': '20px', 'right': '20px', 'cursor': 'pointer',
                    'backgroundColor': '#FFFFFF', 'width': '50px', 'height': '50px',
                    'borderRadius': '50%', 'display': 'flex', 'alignItems': 'center',
                    'justifyContent': 'center', 'boxShadow': '0 4px 12px rgba(0,0,0,0.08)',
                    'zIndex': '999'
                },
                title="История решений"
            ),
            style={'position': 'fixed', 'top': '20px', 'right': '20px', 'zIndex': '999'}
        ),
        
        # Модальное окно истории
        html.Div(
            id='history-modal',
            style={
                'position': 'fixed', 'top': '0', 'left': '0', 'width': '100%', 'height': '100%',
                'backgroundColor': 'rgba(0,0,0,0.5)', 'zIndex': '1000', 'display': 'none',
                'alignItems': 'center', 'justifyContent': 'center'
            },
            children=[
                html.Div(
                    style={
                        'backgroundColor': '#FFFFFF', 'borderRadius': '15px', 'maxWidth': '600px',
                        'width': '90%', 'margin': '20px auto', 'boxShadow': '0 10px 40px rgba(0,0,0,0.1)',
                        'overflow': 'hidden', 'border': '1px solid #D1D9E6'
                    },
                    children=[
                        html.Div(
                            style={
                                'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center',
                                'padding': '15px 20px', 'borderBottom': '2px solid #D1D9E6',
                                'backgroundColor': '#FFFFFF'
                            },
                            children=[
                                html.H3("История решений", style={'margin': '0', 'color': '#2C3E50'}),
                                html.Span("✕", id='close-history-modal', 
                                         style={'fontSize': '24px', 'cursor': 'pointer', 'color': '#E74C3C',
                                                'fontWeight': 'bold'})
                            ]
                        ),
                        html.Div(id='history-list', style={
                            'maxHeight': '500px', 'overflowY': 'auto', 'padding': '15px',
                            'backgroundColor': '#F5F7FA'
                        }),
                        html.Div(
                            style={
                                'borderTop': '1px solid #D1D9E6', 'padding': '15px',
                                'backgroundColor': '#FFFFFF', 'textAlign': 'center'
                            },
                            children=[
                                html.Button("Очистить Историю", id='clear-history-btn',
                                           style={
                                               'background': 'linear-gradient(135deg, #2C3E50 0%, #1a2a3a 100%)',
                                               'color': '#FFFFFF', 'border': 'none', 'borderRadius': '5px',
                                               'padding': '10px 20px', 'cursor': 'pointer'
                                           }),
                                html.Div(
                                    style={'fontSize': '10px', 'color': '#7F8C8D', 'marginTop': '10px'},
                                    children=[
                                        html.Span("Иконки: "),
                                        html.A("Perpixel", href="https://icon-icons.com/ru/authors/770-perpixel", 
                                               target="_blank", style={'color': '#7F8C8D', 'textDecoration': 'none'})
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        ),
        
        dcc.Store(id='solutions-history', storage_type='session', data=[]),
    ])