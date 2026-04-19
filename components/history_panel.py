from dash import html, dcc

def create_history_panel():
    """Создает панель истории решений"""
    return html.Div([
        html.H3("История решений", style={
            'color': '#1a5276', 
            'marginTop': '30px',
            'marginBottom': '15px'
        }),
        
        html.Div([
            html.Button("Очистить историю", id='clear-history-btn',
                       style={
                           'padding': '8px 20px',
                           'backgroundColor': '#e74c3c', 
                           'color': 'white',
                           'border': 'none', 
                           'borderRadius': '5px',
                           'cursor': 'pointer',
                           'fontSize': '14px',
                           'marginBottom': '10px'
                       }),
        ], style={'textAlign': 'right'}),
        
        html.Div(id='history-list', style={
            'maxHeight': '300px',
            'overflowY': 'auto',
            'border': '1px solid #ddd',
            'borderRadius': '8px',
            'padding': '10px',
            'backgroundColor': '#fafafa',
            'marginTop': '10px'
        }),
        
        # Session storage: история сохраняется при обновлении страницы, пока открыта вкладка
        dcc.Store(id='solutions-history', storage_type='session', data=[]),
    ])