from dash import Input, Output, State, callback_context, no_update
from dash.exceptions import PreventUpdate
from dash.dependencies import ALL
import plotly.graph_objs as go
import numpy as np
import time
import json
import uuid
from dash import html
from functools import lru_cache

from utils import (run_volterra_solution, validate_expression_detailed, 
                   format_equation_beautifully, fit_analytical_formula,
                   create_empty_figure, build_sections_plot, build_surface_plot)
from config import KERNEL_EXAMPLES, RHS_EXAMPLES

def _pattern_button_index(ctx):
    """Извлекает индекс из triggered_id"""
    if not ctx.triggered:
        return None
    
    triggered = ctx.triggered[0]
    prop_id = triggered['prop_id']
    
    # Парсим JSON из prop_id
    try:
        # Убираем ".n_clicks" в конце
        if '.n_clicks' in prop_id:
            json_str = prop_id.rsplit('.', 1)[0]
        else:
            json_str = prop_id
        
        # Парсим JSON
        if json_str.startswith('{') and json_str.endswith('}'):
            data = json.loads(json_str)
            return data.get('index')
    except:
        pass
    
    return None

def register_callbacks(app):
    
    # Callback для сброса результатов при изменении входных данных
    @app.callback(
        [Output('analytical-solution-display', 'children'),
         Output('guess-accuracy', 'children'),
         Output('status-message', 'children'),
         Output('status-message', 'style'),
         Output('max-error-display', 'children'),
         Output('max-error-display', 'style'),
         Output('volterra-graph', 'figure'),
         Output('derivative-plot', 'figure'),
         Output('error-output', 'children')],
        [Input('kernel-input', 'value'),
         Input('rhs-input', 'value'),
         Input({'type': 'kernel-example', 'index': ALL}, 'n_clicks'),
         Input({'type': 'rhs-example', 'index': ALL}, 'n_clicks')],
        prevent_initial_call=True
    )
    def clear_results(kernel_val, rhs_val, *args):
        ctx = callback_context
        if not ctx.triggered:
            return [no_update] * 9
        
        triggered_id = ctx.triggered[0]['prop_id']
        empty_display = html.Div("Нажмите 'Решить уравнение'", style={'color': '#7F8C8D'})
        empty_fig = create_empty_figure()
        
        if 'kernel-example' in triggered_id or 'rhs-example' in triggered_id:
            return (empty_display, "", "", {'display': 'none'}, 
                    html.Div(""), {'display': 'none'}, empty_fig, empty_fig, "")
        
        if 'kernel-input' in triggered_id or 'rhs-input' in triggered_id:
            if kernel_val and rhs_val and kernel_val.strip() and rhs_val.strip():
                kernel_valid, _ = validate_expression_detailed(kernel_val, ['x', 't'])
                rhs_valid, _ = validate_expression_detailed(rhs_val, ['x'])
                if kernel_valid and rhs_valid:
                    waiting = html.Div("Нажмите 'Решить уравнение'", style={'color': '#7F8C8D'})
                    return (waiting, "", "", {'display': 'none'}, 
                            html.Div(""), {'display': 'none'}, empty_fig, empty_fig, "")
        
        return (empty_display, "", "", {'display': 'none'}, 
                html.Div(""), {'display': 'none'}, empty_fig, empty_fig, "")
    
    # Callback для модального окна истории
    @app.callback(
        Output('history-modal', 'style'),
        [Input('history-toggle-btn', 'n_clicks'),
         Input('close-history-modal', 'n_clicks')],
        prevent_initial_call=False
    )
    def toggle_modal(open_clicks, close_clicks):
        ctx = callback_context
        if not ctx.triggered:
            return {'display': 'none'}
        
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if triggered_id == 'history-toggle-btn' and open_clicks:
            return {
                'position': 'fixed', 'top': '0', 'left': '0', 'width': '100%', 'height': '100%',
                'backgroundColor': 'rgba(0,0,0,0.5)', 'zIndex': '1000', 'display': 'flex',
                'alignItems': 'center', 'justifyContent': 'center', 'backdropFilter': 'blur(5px)'
            }
        return {'display': 'none'}
    
    # Callback для переключения примеров ядер
    @app.callback(
        [Output('kernel-examples-content', 'style'),
         Output('kernel-examples-toggle', 'children'),
         Output('kernel-examples-state', 'data')],
        Input('kernel-examples-toggle', 'n_clicks'),
        State('kernel-examples-state', 'data'),
        prevent_initial_call=True
    )
    def toggle_kernel_examples(n_clicks, state):
        if n_clicks is None:
            return {'display': 'none'}, '▼ Примеры ядер K(x,t):', {'expanded': False}
        if state and state.get('expanded', False):
            return {'display': 'none'}, '▼ Примеры ядер K(x,t):', {'expanded': False}
        return {'display': 'block'}, '▲ Примеры ядер K(x,t):', {'expanded': True}

    # Callback для переключения примеров правых частей
    @app.callback(
        [Output('rhs-examples-content', 'style'),
         Output('rhs-examples-toggle', 'children'),
         Output('rhs-examples-state', 'data')],
        Input('rhs-examples-toggle', 'n_clicks'),
        State('rhs-examples-state', 'data'),
        prevent_initial_call=True
    )
    def toggle_rhs_examples(n_clicks, state):
        if n_clicks is None:
            return {'display': 'none'}, '▼ Примеры правых частей f(x):', {'expanded': False}
        if state and state.get('expanded', False):
            return {'display': 'none'}, '▼ Примеры правых частей f(x):', {'expanded': False}
        return {'display': 'block'}, '▲ Примеры правых частей f(x):', {'expanded': True}
    
    # Callback для заполнения примеров
    @app.callback(
        [Output('kernel-input', 'value'),
         Output('rhs-input', 'value')],
        [Input({'type': 'kernel-example', 'index': ALL}, 'n_clicks'),
         Input({'type': 'rhs-example', 'index': ALL}, 'n_clicks')],
        prevent_initial_call=True
    )
    def fill_example(kernel_clicks, rhs_clicks):
        ctx = callback_context
        if not ctx.triggered:
            return no_update, no_update
        
        triggered_id = ctx.triggered[0]['prop_id']
        
        try:
            # Парсим JSON
            if '.n_clicks' in triggered_id:
                json_str = triggered_id.rsplit('.', 1)[0]
            else:
                json_str = triggered_id
            
            triggered_dict = json.loads(json_str)
            example_type = triggered_dict.get('type')
            example_index = triggered_dict.get('index')
            
            if example_type == 'kernel-example':
                example_name = list(KERNEL_EXAMPLES.keys())[example_index]
                return KERNEL_EXAMPLES[example_name], no_update
            elif example_type == 'rhs-example':
                example_name = list(RHS_EXAMPLES.keys())[example_index]
                return no_update, RHS_EXAMPLES[example_name]
        except Exception as e:
            print(f"Error in fill_example: {e}")
        
        return no_update, no_update
    
    # Callback для легенды
    @app.callback(
        [Output('legend-content', 'style'),
         Output('legend-state', 'data')],
        Input('legend-toggle', 'n_clicks'),
        State('legend-state', 'data'),
        prevent_initial_call=True
    )
    def toggle_legend(n_clicks, state):
        if n_clicks is None:
            return {'display': 'none'}, state or {'expanded': False}
        if state and state.get('expanded', False):
            return {'display': 'none'}, {'expanded': False}
        return {'display': 'block'}, {'expanded': True}
    
    # Callback для отображения уравнения
    @app.callback(
        Output('equation-display', 'children'),
        [Input('kernel-input', 'value'),
         Input('rhs-input', 'value')]
    )
    def update_equation_display(kernel_expr, rhs_expr):
        if not kernel_expr or not rhs_expr:
            return html.Div("Введите выражения для ядра K(x,t) и правой части f(x)", 
                           style={'color': '#7F8C8D', 'fontStyle': 'italic', 'textAlign': 'center'})
        return format_equation_beautifully(kernel_expr, rhs_expr)
    
    # Callback для валидации
    @app.callback(
        [Output('solve-button', 'disabled'),
         Output('solve-button', 'title'),
         Output('error-message', 'children'),
         Output('error-message', 'style')],
        [Input('kernel-input', 'value'),
         Input('rhs-input', 'value')],
        prevent_initial_call=False
    )
    def validate_inputs(kernel_expr, rhs_expr):
        kernel_valid = True
        rhs_valid = True
        kernel_error = ""
        rhs_error = ""
        
        if kernel_expr and kernel_expr.strip():
            valid, msg = validate_expression_detailed(kernel_expr, ['x', 't'])
            if not valid:
                kernel_valid = False
                kernel_error = msg
        else:
            kernel_valid = False
            kernel_error = "поле ядра пусто"
        
        if rhs_expr and rhs_expr.strip():
            valid, msg = validate_expression_detailed(rhs_expr, ['x'])
            if not valid:
                rhs_valid = False
                rhs_error = msg
        else:
            rhs_valid = False
            rhs_error = "поле правой части пусто"
        
        button_disabled = not (kernel_valid and rhs_valid)
        button_title = "Решить уравнение" if not button_disabled else "Исправьте ошибки"
        
        if not kernel_valid or not rhs_valid:
            error_text = f"Ошибки: K(x,t): {kernel_error}, f(x): {rhs_error}"
            return button_disabled, button_title, error_text, {'display': 'block'}
        
        return button_disabled, button_title, "", {"display": "none"}
    
    # Основной callback для вычислений
    @app.callback(
        [Output('analytical-solution-display', 'children', allow_duplicate=True),
         Output('guess-accuracy', 'children', allow_duplicate=True),
         Output('status-message', 'children', allow_duplicate=True),
         Output('status-message', 'style', allow_duplicate=True),
         Output('max-error-display', 'children', allow_duplicate=True),
         Output('max-error-display', 'style', allow_duplicate=True),
         Output('volterra-graph', 'figure', allow_duplicate=True),
         Output('derivative-plot', 'figure', allow_duplicate=True),
         Output('error-output', 'children', allow_duplicate=True),
         Output('kernel-sections-plot', 'figure', allow_duplicate=True),
         Output('kernel-3d-plot', 'figure', allow_duplicate=True)],
        [Input('solve-button', 'n_clicks')],
        [State('kernel-input', 'value'),
         State('rhs-input', 'value'),
         State('initial-condition', 'value'),
         State('sections-x-min', 'value'),
         State('sections-x-max', 'value'),
         State('surf-x-min', 'value'),
         State('surf-x-max', 'value'),
         State('surf-t-min', 'value'),
         State('surf-t-max', 'value')],
        prevent_initial_call=True
    )
    def compute_solution(n_clicks, kernel_expr, rhs_expr, initial_condition,
                         sec_x_min, sec_x_max, surf_x_min, surf_x_max, surf_t_min, surf_t_max):
        if not n_clicks:
            raise PreventUpdate
        
        if not kernel_expr or not rhs_expr:
            raise PreventUpdate
        
        try:
            (x_vals, phi_numerical, phi_reference, derivative_numerical, 
             derivative_exact, error_text, computation_time, _) = run_volterra_solution(
                kernel_expr, rhs_expr, initial_condition or 0, 1000, 200)
            
            fig_solution = go.Figure()
            fig_solution.add_trace(go.Scatter(x=x_vals, y=phi_reference, mode='lines', name='Эталон',
                                              line=dict(color='#E74C3C', width=2)))
            fig_solution.add_trace(go.Scatter(x=x_vals, y=phi_numerical, mode='lines', name='Численное',
                                              line=dict(color='#2C3E50', dash='dash', width=1.5)))
            fig_solution.update_layout(
                xaxis_title='x', yaxis_title='φ(x)', hovermode='x unified',
                template='plotly_white', height=400, showlegend=True,
                plot_bgcolor='white', paper_bgcolor='white',
                font=dict(family="Roboto, sans-serif", size=12, color="#2C3E50")
            )
            
            fig_derivative = go.Figure()
            fig_derivative.add_trace(go.Scatter(x=x_vals, y=derivative_numerical, mode='lines', name="φ'(x) (численная)",
                                                line=dict(color='#34495E', width=2)))
            fig_derivative.add_trace(go.Scatter(x=x_vals, y=derivative_exact, mode='lines', 
                                                name='f(x) + I(x) (точная)',
                                                line=dict(color='#E74C3C', dash='dash', width=1.5)))
            fig_derivative.update_layout(
                xaxis_title='x', yaxis_title="φ'(x)", hovermode='x unified',
                template='plotly_white', height=400, showlegend=True,
                plot_bgcolor='white', paper_bgcolor='white',
                font=dict(family="Roboto, sans-serif", size=12, color="#2C3E50")
            )
            
            fig_sections = build_sections_plot(kernel_expr, sec_x_min, sec_x_max)
            fig_surface = build_surface_plot(kernel_expr, surf_x_min, surf_x_max, surf_t_min, surf_t_max)
            
            formula = fit_analytical_formula(x_vals, phi_numerical)
            
            if formula:
                display_html = html.Div([
                    html.Span("φ(x) = ", style={'fontWeight': 'bold', 'color': '#2C3E50'}),
                    html.Span(formula, style={'color': '#2C3E50', 'fontFamily': 'monospace', 'fontWeight': 'bold'})
                ])
            else:
                points = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
                values = []
                for xp in points:
                    idx = int(xp * len(x_vals))
                    if idx < len(phi_numerical):
                        values.append(html.Div(f"φ({xp}) = {phi_numerical[idx]:.6f}"))
                display_html = html.Div([
                    html.Span("Численное решение:", style={'fontWeight': 'bold'}),
                    html.Div(values, style={'marginTop': '10px', 'padding': '10px', 
                                           'backgroundColor': '#F5F7FA', 'borderRadius': '8px'})
                ])
            
            max_error_display = html.Div(error_text, style={'fontWeight': 'bold', 'color': '#C0392B', 
                                                           'textAlign': 'center', 'padding': '12px'})
            status_message = html.Div([
                html.Span("Вычисление успешно завершено! ", style={'fontWeight': 'bold'}),
                html.Span(f"Время: {computation_time:.2f} с", style={'color': '#7F8C8D'})
            ], style={'color': '#27ae60', 'textAlign': 'center'})
            
            return (display_html, "", status_message, {'textAlign': 'center', 'margin': '10px'},
                    max_error_display, {'display': 'block'},
                    fig_solution, fig_derivative, error_text,
                    fig_sections, fig_surface)
            
        except Exception as e:
            error_msg = str(e)
            empty_fig = create_empty_figure()
            error_status = html.Div(f"Ошибка: {error_msg}", style={'color': '#E74C3C', 'textAlign': 'center'})
            return (html.Div(f"Ошибка: {error_msg}", style={'color': '#E74C3C'}), "", 
                    error_status, {'textAlign': 'center'}, html.Div(""), {'display': 'none'},
                    empty_fig, empty_fig, "Ошибка вычислений", empty_fig, empty_fig)
    
    # Callback для сохранения в историю (после успешного вычисления)
    @app.callback(
        Output('solutions-history', 'data', allow_duplicate=True),
        [Input('solve-button', 'n_clicks')],
        [State('kernel-input', 'value'), 
         State('rhs-input', 'value'),
         State('initial-condition', 'value'), 
         State('solutions-history', 'data')],
        prevent_initial_call=True
    )
    def save_to_history(n_clicks, kernel_expr, rhs_expr, initial_condition, history_data):
        print(f"save_to_history called with n_clicks={n_clicks}")
        
        if not n_clicks:
            raise PreventUpdate
        
        if not kernel_expr or not kernel_expr.strip():
            raise PreventUpdate
        if not rhs_expr or not rhs_expr.strip():
            raise PreventUpdate
        
        kernel_valid, _ = validate_expression_detailed(kernel_expr, ['x', 't'])
        rhs_valid, _ = validate_expression_detailed(rhs_expr, ['x'])
        
        if not kernel_valid or not rhs_valid:
            raise PreventUpdate
        
        new_record = {
            'id': str(uuid.uuid4()),
            'timestamp': time.strftime("%H:%M:%S"),
            'date': time.strftime("%d.%m.%Y"),
            'kernel': kernel_expr,
            'rhs': rhs_expr,
            'initial_condition': initial_condition or 0,
        }
        
        history = [r for r in (history_data or []) if isinstance(r, dict) and r.get('id')]
        new_history = [new_record] + history[:19]
        
        print(f"Saved to history, total records: {len(new_history)}")
        return new_history
    
    # Callback для обновления списка истории
    @app.callback(
        Output('history-list', 'children'),
        [Input('solutions-history', 'data'),
         Input('clear-history-btn', 'n_clicks')],
        prevent_initial_call=False
    )
    def update_history_list(history_data, clear_clicks):
        print(f"Updating history list, data: {history_data is not None}, clear_clicks: {clear_clicks}")
        
        if clear_clicks:
            return html.Div("История пуста", style={'color': '#95A5A6', 'textAlign': 'center', 'padding': '20px'})
        
        if not history_data or len(history_data) == 0:
            return html.Div("История пуста", style={'color': '#95A5A6', 'textAlign': 'center', 'padding': '20px'})
        
        items = []
        for record in history_data:
            if not isinstance(record, dict) or 'id' not in record:
                continue
            
            kernel_preview = record['kernel'][:50] + '...' if len(record['kernel']) > 50 else record['kernel']
            rhs_preview = record['rhs'][:50] + '...' if len(record['rhs']) > 50 else record['rhs']
            
            items.append(html.Div(
                style={
                    'padding': '12px', 'borderBottom': '1px solid #D1D9E6',
                    'backgroundColor': 'white', 'borderRadius': '8px', 'marginBottom': '8px',
                    'transition': 'all 0.3s ease'
                },
                children=[
                    html.Div(
                        style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'},
                        children=[
                            html.Div([
                                html.Span(f"{record.get('timestamp', '')} | {record.get('date', '')}",
                                         style={'fontWeight': 'bold', 'color': '#2C3E50', 'fontSize': '0.9em'}),
                                html.Span(f" | φ(0)={record.get('initial_condition', 0)}",
                                         style={'color': '#7F8C8D', 'fontSize': '0.85em', 'marginLeft': '10px'})
                            ]),
                        ]
                    ),
                    html.Div(
                        style={'marginLeft': '15px', 'marginTop': '8px', 'marginBottom': '8px'},
                        children=[
                            html.Small(f"K(x,t) = {kernel_preview}", 
                                      style={'color': '#34495E', 'fontFamily': 'monospace'}),
                            html.Br(),
                            html.Small(f"f(x) = {rhs_preview}", 
                                      style={'color': '#E74C3C', 'fontFamily': 'monospace'})
                        ]
                    ),
                    html.Div(
                        style={'marginTop': '10px', 'textAlign': 'right'},
                        children=[
                            html.Button(
                                html.Img(
                                    src='/assets/load-icon.png',
                                    style={'width': '20px', 'height': '20px', 'display': 'block'}
                                ),
                                id={'type': 'load-solution', 'index': record['id']},
                                style={
                                    'padding': '8px', 'marginRight': '8px',
                                    'backgroundColor': '#FFFFFF', 'border': '1px solid #D1D9E6',
                                    'borderRadius': '5px', 'cursor': 'pointer',
                                    'display': 'inline-flex', 'alignItems': 'center', 'justifyContent': 'center'
                                },
                                title="Загрузить решение"
                            ),
                            html.Button(
                                html.Img(
                                    src='/assets/delete-icon.png',
                                    style={'width': '20px', 'height': '20px', 'display': 'block'}
                                ),
                                id={'type': 'delete-solution', 'index': record['id']},
                                style={
                                    'padding': '8px', 'backgroundColor': '#FFFFFF',
                                    'border': '1px solid #D1D9E6', 'borderRadius': '5px',
                                    'cursor': 'pointer', 'display': 'inline-flex',
                                    'alignItems': 'center', 'justifyContent': 'center'
                                },
                                title="Удалить из истории"
                            )
                        ]
                    )
                ]
            ))
        
        return items
    
    # Callback для загрузки решения из истории
    @app.callback(
        [Output('kernel-input', 'value', allow_duplicate=True),
         Output('rhs-input', 'value', allow_duplicate=True),
         Output('initial-condition', 'value', allow_duplicate=True),
         Output('solve-button', 'n_clicks', allow_duplicate=True),
         Output('history-modal', 'style', allow_duplicate=True)],
        [Input({'type': 'load-solution', 'index': ALL}, 'n_clicks')],
        [State('solutions-history', 'data')],
        prevent_initial_call=True
    )
    def load_from_history(clicks, history_data):
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate
        
        triggered_value = ctx.triggered[0].get('value')
        if not triggered_value:
            raise PreventUpdate
        
        if not history_data:
            print("No history data")
            raise PreventUpdate
        
        solution_id = _pattern_button_index(ctx)
        print(f"Loading solution with id: {solution_id}")
        
        if not solution_id:
            raise PreventUpdate
        
        for record in history_data:
            if str(record.get('id')) == str(solution_id):
                print(f"Found record: {record.get('kernel')[:50]}...")
                modal_closed = {'display': 'none'}
                return (record.get('kernel'), record.get('rhs'), 
                       record.get('initial_condition', 0), 1, modal_closed)
        
        print(f"Record with id {solution_id} not found")
        raise PreventUpdate
    
    # Callback для удаления из истории
    @app.callback(
        Output('solutions-history', 'data', allow_duplicate=True),
        [Input({'type': 'delete-solution', 'index': ALL}, 'n_clicks')],
        [State('solutions-history', 'data')],
        prevent_initial_call=True
    )
    def delete_from_history(clicks, history_data):
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate
        
        triggered_value = ctx.triggered[0].get('value')
        if not triggered_value:
            raise PreventUpdate
        
        if not history_data:
            raise PreventUpdate
        
        solution_id = _pattern_button_index(ctx)
        print(f"Deleting solution with id: {solution_id}")
        
        if not solution_id:
            raise PreventUpdate
        
        new_history = [r for r in history_data if str(r.get('id')) != str(solution_id)]
        print(f"Deleted, remaining records: {len(new_history)}")
        
        return new_history
    
    # Callback для очистки всей истории
    @app.callback(
        Output('solutions-history', 'data', allow_duplicate=True),
        [Input('clear-history-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def clear_history(clicks):
        if clicks:
            print("Clearing all history")
            return []
        raise PreventUpdate
    
    # Callback для обновления графиков ядра
    @app.callback(
        Output('kernel-sections-plot', 'figure'),
        [Input('update-sections-btn', 'n_clicks'), 
         Input('kernel-input', 'value')],
        [State('sections-x-min', 'value'), 
         State('sections-x-max', 'value')],
        prevent_initial_call=True
    )
    def update_sections(n_clicks, kernel_expr, x_min, x_max):
        return build_sections_plot(kernel_expr, x_min, x_max)

    @app.callback(
        Output('kernel-3d-plot', 'figure'),
        [Input('update-surf-btn', 'n_clicks'), 
         Input('kernel-input', 'value')],
        [State('surf-x-min', 'value'), 
         State('surf-x-max', 'value'),
         State('surf-t-min', 'value'), 
         State('surf-t-max', 'value')],
        prevent_initial_call=True
    )
    def update_surface(n_clicks, kernel_expr, x_min, x_max, t_min, t_max):
        return build_surface_plot(kernel_expr, x_min, x_max, t_min, t_max)