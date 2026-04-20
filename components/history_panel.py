from dash import html, dcc

def create_history_panel():
    """Создает панель истории решений с модальным окном"""
    return html.Div([
        # Кнопка-иконка для открытия истории (теперь с картинкой)
        html.Div(
            html.Div(
                html.Img(
                    src='/assets/history-icon.png',  # путь к вашей иконке
                    style={
                        'width': '32px',
                        'height': '32px',
                        'display': 'block'
                    }
                ),
                id='history-toggle-btn',
                style={
                    'position': 'fixed',
                    'top': '20px',
                    'right': '20px',
                    'cursor': 'pointer',
                    'backgroundColor': 'transparent',  # убираем голубой фон
                    'width': '50px',
                    'height': '50px',
                    'borderRadius': '50%',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'boxShadow': '0 4px 12px rgba(0,0,0,0.15)',
                    'transition': 'transform 0.2s ease',
                    'zIndex': '999',
                    'background': 'white'  # белый фон вместо голубого
                },
                title="История решений"
            ),
            style={'position': 'fixed', 'top': '20px', 'right': '20px', 'zIndex': '999'}
        ),
        
        # Модальное окно истории
        html.Div(
            id='history-modal',
            children=[
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                html.H3("История решений", style={'margin': '0', 'color': '#1a5276'}),
                                html.Span(
                                    "✕",
                                    id='close-history-modal',
                                    style={
                                        'fontSize': '24px',
                                        'cursor': 'pointer',
                                        'color': '#e74c3c',
                                        'fontWeight': 'bold',
                                        'transition': 'transform 0.2s ease'
                                    },
                                    title="Закрыть"
                                )
                            ],
                            style={
                                'display': 'flex',
                                'justifyContent': 'space-between',
                                'alignItems': 'center',
                                'padding': '15px 20px',
                                'borderBottom': '2px solid #a8d5e8',
                                'backgroundColor': '#f0f8ff'
                            }
                        ),
                        html.Div(
                            id='history-list',
                            style={
                                'maxHeight': '500px',
                                'overflowY': 'auto',
                                'padding': '15px'
                            }
                        ),
                        html.Div(
                            [
                                html.Button(
                                    "Очистить Историю",
                                    id='clear-history-btn',
                                    style={
                                        'padding': '10px 20px',
                                        'backgroundColor': '#e74c3c',
                                        'color': 'white',
                                        'border': 'none',
                                        'borderRadius': '5px',
                                        'cursor': 'pointer',
                                        'fontSize': '14px',
                                        'margin': '15px auto',
                                        'display': 'block',
                                        'width': '150px'
                                    }
                                ),
                                # Блок с авторским правом
                                html.Div(
                                    [
                                        html.Span("Иконка истории: ", style={'fontSize': '11px', 'color': '#999'}),
                                        html.A(
                                            "назад часы истории отчет значок",
                                            href="https://icon-icons.com/ru/authors/770-perpixel",
                                            target="_blank",
                                            style={'fontSize': '11px', 'color': '#999', 'textDecoration': 'none'}
                                        ),
                                        html.Span(" by Perpixel on ", style={'fontSize': '11px', 'color': '#999'}),
                                        html.A(
                                            "Icon-Icons.com",
                                            href="https://icon-icons.com/ru/authors/770-perpixel",
                                            target="_blank",
                                            style={'fontSize': '11px', 'color': '#999', 'textDecoration': 'none'}
                                        )
                                    ],
                                    style={
                                        'textAlign': 'center',
                                        'padding': '10px',
                                        'borderTop': '1px solid #e0e0e0',
                                        'marginTop': '10px'
                                    }
                                )
                            ],
                            style={'borderTop': '1px solid #ddd', 'padding': '15px'}
                        )
                    ],
                    style={
                        'backgroundColor': '#f8fbff',
                        'borderRadius': '15px',
                        'maxWidth': '600px',
                        'width': '90%',
                        'margin': '50px auto',
                        'boxShadow': '0 10px 40px rgba(0,0,0,0.2)',
                        'overflow': 'hidden'
                    }
                )
            ],
            style={
                'position': 'fixed',
                'top': '0',
                'left': '0',
                'width': '100%',
                'height': '100%',
                'backgroundColor': 'rgba(0,0,0,0.5)',
                'zIndex': '1000',
                'display': 'none',
                'backdropFilter': 'blur(5px)'
            }
        ),
        
        # Session storage: история сохраняется при обновлении страницы
        dcc.Store(id='solutions-history', storage_type='session', data=[]),
    ])