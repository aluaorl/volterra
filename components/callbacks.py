from dash import Input, Output, State, callback_context, no_update
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
import numpy as np
import time
import json
import uuid
from dash import html
import sys
import os
from functools import lru_cache 
from dash.dependencies import ALL

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calculation_engine import solve_volterra_RK4, get_reference_solution, create_function_from_string
from expression_parser import parse_user_input, format_for_display, validate_expression_detailed
from components.input_panel import KERNEL_EXAMPLES, RHS_EXAMPLES

# Расширенная функция для подбора аналитической формулы
def fit_analytical_formula(x_values, y_values):
    """
    Подбирает аналитическую формулу для численных данных.
    Поддерживает:
    - Константу
    - Линейную функцию
    - Квадратичную функцию
    - Экспоненциальную функцию
    - Синус/косинус
    - Сумму экспонент
    - Сумму экспоненты и синуса
    - Сумму синуса и косинуса
    - Полином 4-й степени
    """
    try:
        from scipy.optimize import curve_fit
        
        # 1. Константа
        const_val = np.mean(y_values)
        const_error = np.max(np.abs(y_values - const_val))
        if const_error < 1e-8:
            return f"{const_val:.6f}"
        
        # 2. Линейная: a*x + b
        def linear(x, a, b):
            return a * x + b
        
        try:
            popt, _ = curve_fit(linear, x_values, y_values, maxfev=10000)
            a, b = popt
            y_pred = linear(x_values, a, b)
            max_error = np.max(np.abs(y_values - y_pred))
            
            if max_error < 1e-6:
                if abs(b) < 1e-10:
                    return f"{a:.6f}*x"
                elif abs(a) < 1e-10:
                    return f"{b:.6f}"
                else:
                    sign = '+' if b > 0 else '-'
                    return f"{a:.6f}*x {sign} {abs(b):.6f}"
        except:
            pass
        
        # 3. Квадратичная: a*x^2 + b*x + c
        def quadratic(x, a, b, c):
            return a * x**2 + b * x + c
        
        try:
            popt, _ = curve_fit(quadratic, x_values, y_values, maxfev=10000)
            a, b, c = popt
            y_pred = quadratic(x_values, a, b, c)
            max_error = np.max(np.abs(y_values - y_pred))
            
            if max_error < 1e-6:
                terms = []
                if abs(a) > 1e-10:
                    if abs(a - 1.0) < 1e-10:
                        terms.append("x²")
                    else:
                        terms.append(f"{a:.6f}*x²")
                if abs(b) > 1e-10:
                    sign = '+' if b > 0 and terms else ''
                    if abs(b - 1.0) < 1e-10:
                        terms.append(f"{sign}x")
                    else:
                        terms.append(f"{sign}{b:.6f}*x")
                if abs(c) > 1e-10:
                    sign = '+' if c > 0 and terms else ''
                    terms.append(f"{sign}{c:.6f}")
                result = ''.join(terms)
                if result:
                    return result
        except:
            pass
        
        # 4. Экспоненциальная: a*exp(b*x) + c
        def exp_func(x, a, b, c):
            return a * np.exp(b * x) + c
        
        try:
            p0 = [y_values[-1] - y_values[0], -1, y_values[0]]
            popt, _ = curve_fit(exp_func, x_values, y_values, p0=p0, maxfev=10000)
            a, b, c = popt
            y_pred = exp_func(x_values, a, b, c)
            max_error = np.max(np.abs(y_values - y_pred))
            
            if max_error < 1e-6:
                if abs(c) < 1e-10:
                    return f"{a:.6f}*exp({b:.6f}*x)"
                return f"{a:.6f}*exp({b:.6f}*x) + {c:.6f}"
        except:
            pass
        
        # 5. Синус: a*sin(w*x + p) + c
        def sin_func(x, a, w, p, c):
            return a * np.sin(w * x + p) + c
        
        try:
            p0 = [np.std(y_values), 2*np.pi, 0, np.mean(y_values)]
            popt, _ = curve_fit(sin_func, x_values, y_values, p0=p0, maxfev=10000)
            a, w, p, c = popt
            y_pred = sin_func(x_values, a, w, p, c)
            max_error = np.max(np.abs(y_values - y_pred))
            
            if max_error < 1e-6:
                if abs(c) < 1e-10:
                    return f"{a:.6f}*sin({w:.6f}*x + {p:.6f})"
                return f"{a:.6f}*sin({w:.6f}*x + {p:.6f}) + {c:.6f}"
        except:
            pass
        
        # 6. Косинус: a*cos(w*x + p) + c
        def cos_func(x, a, w, p, c):
            return a * np.cos(w * x + p) + c
        
        try:
            p0 = [np.std(y_values), 2*np.pi, 0, np.mean(y_values)]
            popt, _ = curve_fit(cos_func, x_values, y_values, p0=p0, maxfev=10000)
            a, w, p, c = popt
            y_pred = cos_func(x_values, a, w, p, c)
            max_error = np.max(np.abs(y_values - y_pred))
            
            if max_error < 1e-6:
                if abs(c) < 1e-10:
                    return f"{a:.6f}*cos({w:.6f}*x + {p:.6f})"
                return f"{a:.6f}*cos({w:.6f}*x + {p:.6f}) + {c:.6f}"
        except:
            pass
        
        # 7. Сумма двух экспонент: A*exp(r1*x) + B*exp(r2*x) + C
        def double_exp(x, A, r1, B, r2, C):
            return A * np.exp(r1 * x) + B * np.exp(r2 * x) + C
        
        try:
            p0 = [1.0, -1.0, 1.0, -2.0, 0.0]
            popt, _ = curve_fit(double_exp, x_values, y_values, p0=p0, maxfev=10000)
            A, r1, B, r2, C = popt
            y_pred = double_exp(x_values, A, r1, B, r2, C)
            max_error = np.max(np.abs(y_values - y_pred))
            
            if max_error < 1e-5:
                terms = []
                if abs(A) > 1e-10:
                    terms.append(f"{A:.6f}*exp({r1:.6f}*x)")
                if abs(B) > 1e-10:
                    sign = '+' if B > 0 else ''
                    terms.append(f"{sign}{B:.6f}*exp({r2:.6f}*x)")
                if abs(C) > 1e-10:
                    sign = '+' if C > 0 else ''
                    terms.append(f"{sign}{C:.6f}")
                result = ''.join(terms)
                if result:
                    return result
        except:
            pass
        
        # 8. Сумма экспоненты и синуса: A*exp(r*x) + B*sin(w*x + p) + C
        def exp_sin(x, A, r, B, w, p, C):
            return A * np.exp(r * x) + B * np.sin(w * x + p) + C
        
        try:
            p0 = [1.0, -1.0, 0.5, 2*np.pi, 0, 0]
            popt, _ = curve_fit(exp_sin, x_values, y_values, p0=p0, maxfev=10000)
            A, r, B, w, p, C = popt
            y_pred = exp_sin(x_values, A, r, B, w, p, C)
            max_error = np.max(np.abs(y_values - y_pred))
            
            if max_error < 1e-5:
                terms = []
                if abs(A) > 1e-10:
                    terms.append(f"{A:.6f}*exp({r:.6f}*x)")
                if abs(B) > 1e-10:
                    sign = '+' if B > 0 and terms else ''
                    terms.append(f"{sign}{B:.6f}*sin({w:.6f}*x + {p:.6f})")
                if abs(C) > 1e-10:
                    sign = '+' if C > 0 and terms else ''
                    terms.append(f"{sign}{C:.6f}")
                result = ''.join(terms)
                if result:
                    return result
        except:
            pass
        
        # 9. Сумма синуса и косинуса: A*sin(w1*x) + B*cos(w2*x + p) + C
        def sin_cos_sum(x, A, w1, B, w2, p, C):
            return A * np.sin(w1 * x) + B * np.cos(w2 * x + p) + C
        
        try:
            p0 = [0.5, 2*np.pi, 0.5, 2*np.pi, 0, 0]
            popt, _ = curve_fit(sin_cos_sum, x_values, y_values, p0=p0, maxfev=10000)
            A, w1, B, w2, p, C = popt
            y_pred = sin_cos_sum(x_values, A, w1, B, w2, p, C)
            max_error = np.max(np.abs(y_values - y_pred))
            
            if max_error < 1e-5:
                terms = []
                if abs(A) > 1e-10:
                    terms.append(f"{A:.6f}*sin({w1:.6f}*x)")
                if abs(B) > 1e-10:
                    sign = '+' if B > 0 and terms else ''
                    terms.append(f"{sign}{B:.6f}*cos({w2:.6f}*x + {p:.6f})")
                if abs(C) > 1e-10:
                    sign = '+' if C > 0 and terms else ''
                    terms.append(f"{sign}{C:.6f}")
                result = ''.join(terms)
                if result:
                    return result
        except:
            pass
        
        # 10. Полином 4-й степени (для сложных функций)
        try:
            coeffs = np.polyfit(x_values, y_values, 4)
            terms = []
            for i, coef in enumerate(coeffs):
                if abs(coef) > 1e-8:
                    power = 4 - i
                    if power == 4:
                        terms.append(f"{coef:.6f}*x⁴")
                    elif power == 3:
                        sign = '+' if coef > 0 else ''
                        terms.append(f"{sign}{coef:.6f}*x³")
                    elif power == 2:
                        sign = '+' if coef > 0 else ''
                        terms.append(f"{sign}{coef:.6f}*x²")
                    elif power == 1:
                        sign = '+' if coef > 0 else ''
                        terms.append(f"{sign}{coef:.6f}*x")
                    else:
                        sign = '+' if coef > 0 else ''
                        terms.append(f"{sign}{coef:.6f}")
            if terms:
                result = ''.join(terms)
                result = result.replace('+-', '-')
                if result.startswith('+'):
                    result = result[1:]
                return result
        except:
            pass
        
        return None
        
    except Exception as e:
        print(f"Ошибка в fit_analytical_formula: {e}")
        return None

def _pattern_button_index(ctx):
    tid = getattr(ctx, 'triggered_id', None)
    if isinstance(tid, dict) and 'index' in tid:
        return tid['index']
    if not ctx.triggered:
        return None
    raw = ctx.triggered[0]['prop_id'].rsplit('.', 1)[0]
    try:
        return json.loads(raw.replace("'", '"')).get('index')
    except (json.JSONDecodeError, TypeError, ValueError, AttributeError):
        return None

def create_empty_figure(title=""):
    """Создает пустой график без ошибок"""
    fig = go.Figure()
    fig.update_layout(
        title=title,
        xaxis_title='x',
        yaxis_title='y',
        template='plotly_white',
        height=400,
        xaxis=dict(range=[0, 1]),
        yaxis=dict(range=[-1, 1]),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Roboto, sans-serif", size=12, color="#2C3E50")
    )
    return fig

def build_sections_plot(kernel_expr, x_min, x_max):
    """Строит график сечений ядра (автоматические t от min до max)"""
    if not kernel_expr or not kernel_expr.strip():
        return create_empty_figure("")
    
    kernel_valid, _ = validate_expression_detailed(kernel_expr, ['x', 't'])
    if not kernel_valid:
        return create_empty_figure("")
    
    if x_min is None:
        x_min = 0
    if x_max is None or x_max <= x_min:
        x_max = x_min + 1
    
    # Автоматически генерируем 5 значений t от x_min до x_max
    t_values = np.linspace(x_min, x_max, 5)
    
    try:
        K_func = create_function_from_string(kernel_expr, ['x', 't'])
    except Exception as e:
        return create_empty_figure("")
    
    n_points = 500
    x_vals = np.linspace(x_min, x_max, n_points)
    
    colors = ['#2C3E50', '#34495E', '#E74C3C', '#C0392B', '#7F8C8D']
    fig = go.Figure()
    
    for i, t_val in enumerate(t_values):
        color = colors[i % len(colors)]
        try:
            K_vals = [K_func(xi, t_val) for xi in x_vals]
            fig.add_trace(go.Scatter(
                x=x_vals, y=K_vals, 
                mode='lines', 
                name=f't = {t_val:.3f}', 
                line=dict(color=color, width=2)
            ))
        except Exception:
            pass
    
    fig.update_layout(
        title=f'x ∈ [{x_min:.2f}, {x_max:.2f}]',
        xaxis_title='x',
        yaxis_title='K(x,t)',
        hovermode='x unified',
        template='plotly_white',
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Roboto, sans-serif", size=12, color="#2C3E50"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def build_surface_plot(kernel_expr, x_min, x_max, t_min, t_max):
    """Строит 3D поверхность ядра"""
    if not kernel_expr or not kernel_expr.strip():
        return create_empty_figure("")
    
    kernel_valid, _ = validate_expression_detailed(kernel_expr, ['x', 't'])
    if not kernel_valid:
        return create_empty_figure("")
    
    if x_min is None:
        x_min = 0
    if x_max is None or x_max <= x_min:
        x_max = x_min + 1
    if t_min is None:
        t_min = 0
    if t_max is None or t_max <= t_min:
        t_max = t_min + 1
    
    try:
        K_func = create_function_from_string(kernel_expr, ['x', 't'])
    except Exception as e:
        return create_empty_figure("")
    
    n_points = 50
    x_vals = np.linspace(x_min, x_max, n_points)
    t_vals = np.linspace(t_min, t_max, n_points)
    
    X, T = np.meshgrid(x_vals, t_vals)
    K_vals = np.zeros_like(X)
    
    for i in range(len(X)):
        for j in range(len(T)):
            try:
                K_vals[i, j] = K_func(X[i, j], T[i, j])
            except Exception:
                K_vals[i, j] = np.nan
    
    fig = go.Figure(data=[go.Surface(
        z=K_vals, 
        x=X, 
        y=T, 
        colorscale='Blues',
        contours={
            "z": {"show": True, "usecolormap": True, "highlightcolor": "limegreen", "project": {"z": True}}
        }
    )])
    
    fig.update_layout(
        title=f'x ∈ [{x_min:.2f}, {x_max:.2f}], t ∈ [{t_min:.2f}, {t_max:.2f}]',
        scene=dict(
            xaxis_title='x',
            yaxis_title='t',
            zaxis_title='K(x,t)',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
        ),
        height=450,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Roboto, sans-serif", size=12, color="#2C3E50")
    )
    
    return fig

@lru_cache(maxsize=128) 
def get_cached_functions(kernel_expr, rhs_expr):
    K_current = create_function_from_string(kernel_expr, ['x', 't'])
    f_current = create_function_from_string(rhs_expr, ['x'])
    return K_current, f_current

def format_equation_beautifully(kernel_expr, rhs_expr):
    if not kernel_expr or not rhs_expr:
        return html.Div([
            html.Div("Введите выражения для ядра K(x,t) и правой части f(x)", 
                    style={'color': '#7F8C8D', 'fontStyle': 'italic', 'textAlign': 'center'})
        ])
    
    try:
        parsed_kernel = parse_user_input(kernel_expr, ['x', 't'])
        parsed_rhs = parse_user_input(rhs_expr, ['x'])
        
        kernel_display = format_for_display(parsed_kernel, is_kernel=True)
        rhs_display = format_for_display(parsed_rhs, is_kernel=False)
        
        kernel_display = kernel_display.replace('K(x,t) = ', '')
        rhs_display = rhs_display.replace('f(x) = ', '')
        
        kernel_display = kernel_display.replace('exp', 'e')
        rhs_display = rhs_display.replace('exp', 'e')
        
        import re
        kernel_display = re.sub(r'e\^\{([^}]+)\}', r'e^{\1}', kernel_display)
        rhs_display = re.sub(r'e\^\{([^}]+)\}', r'e^{\1}', rhs_display)
        
        return html.Div([
            html.Div([
                html.Span("φ'(x) = ", style={'fontWeight': 'bold', 'fontSize': '1.2em', 'color': '#2C3E50'}),
                html.Span(rhs_display, style={'color': '#E74C3C', 'fontWeight': 'bold', 'fontSize': '1.2em'}),
                html.Span(" + ", style={'fontWeight': 'bold', 'fontSize': '1.2em', 'color': '#2C3E50'}),
                html.Span("∫₀ˣ ", style={'fontSize': '1.2em', 'color': '#2C3E50'}),
                html.Span(kernel_display, style={'color': '#34495E', 'fontWeight': 'bold', 'fontSize': '1.2em'}),
                html.Span(" · φ(t) dt", style={'fontSize': '1.2em', 'color': '#2C3E50'}),
            ], style={'marginBottom': '15px', 'fontFamily': 'monospace', 'textAlign': 'center'}),
        ])
    except Exception as e:
        return html.Div([
            html.Div([
                html.Span("φ'(x) = ", style={'fontWeight': 'bold', 'fontSize': '1.1em', 'color': '#2C3E50'}),
                html.Span(rhs_expr, style={'color': '#E74C3C', 'fontFamily': 'monospace'}),
                html.Span(" + ∫₀ˣ ", style={'fontSize': '1.1em', 'color': '#2C3E50'}),
                html.Span(kernel_expr, style={'color': '#34495E', 'fontFamily': 'monospace'}),
                html.Span(" · φ(t) dt", style={'fontSize': '1.1em', 'color': '#2C3E50'}),
            ], style={'marginBottom': '10px', 'textAlign': 'center'}),
        ])

def run_volterra_solution(kernel_expr, rhs_expr, initial_condition, N_points=1000, N_ref=200):
    start_time = time.time()
    
    if not kernel_expr or not kernel_expr.strip():
        raise ValueError("Выражение для ядра K(x,t) не может быть пустым")
    if not rhs_expr or not rhs_expr.strip():
        raise ValueError("Выражение для правой части f(x) не может быть пустым")
    
    K_current, f_current = get_cached_functions(kernel_expr, rhs_expr) 
    
    try:
        test_K = K_current(0.5, 0.5)
        test_f = f_current(0.5)
    except Exception as e:
        raise ValueError(f"Ошибка при проверке функций: {str(e)}")

    a, b = 0, 1
    h = (b - a) / N_points
    x = np.linspace(a, b, N_points + 1)

    phi_numerical, integral_values = solve_volterra_RK4(x, h, K_current, f_current, initial_condition)
    phi_reference = get_reference_solution(x, K_current, f_current, initial_condition, N_ref)
    f_values = np.array([f_current(xi) for xi in x])
    
    derivative_numerical = np.gradient(phi_numerical, h)
    derivative_exact = f_values + integral_values 

    fig_solution = go.Figure()
    fig_solution.add_trace(go.Scatter(x=x, y=phi_reference, mode='lines', name='Эталон',
                                      line=dict(color='#E74C3C', width=2)))
    fig_solution.add_trace(go.Scatter(x=x, y=phi_numerical, mode='lines', name='Численное',
                                      line=dict(color='#2C3E50', dash='dash', width=1.5)))
    fig_solution.update_layout(
        title='', xaxis_title='x', yaxis_title='φ(x)', hovermode='x unified',
        template='plotly_white', height=400, showlegend=True,
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family="Roboto, sans-serif", size=12, color="#2C3E50")
    )
    
    fig_derivative = go.Figure()
    fig_derivative.add_trace(go.Scatter(x=x, y=derivative_numerical, mode='lines', name="φ'(x) (численная)",
                                        line=dict(color='#34495E', width=2)))
    fig_derivative.add_trace(go.Scatter(x=x, y=derivative_exact, mode='lines', 
                                        name='f(x) + I(x) (точная)', line=dict(color='#E74C3C', dash='dash', width=1.5)))
    fig_derivative.update_layout(
        title='', xaxis_title='x', yaxis_title="φ'(x)", hovermode='x unified',
        template='plotly_white', height=400, showlegend=True,
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family="Roboto, sans-serif", size=12, color="#2C3E50")
    )

    error = np.abs(phi_numerical - phi_reference)
    max_error = np.max(error)
    error_text = f'Глобальная погрешность в равномерной норме l_inf: {max_error:.2e}'

    computation_time = time.time() - start_time
    return (fig_solution, fig_derivative, error_text, computation_time, x, phi_numerical, phi_reference)

def register_callbacks(app):
    
    # Callback для сброса всех результатов при изменении входных данных
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
    def clear_all_results_on_input_change(kernel_val, rhs_val, kernel_clicks, rhs_clicks):
        """Очищает ВСЕ результаты при любом изменении полей ввода или выборе примера"""
        ctx = callback_context
        
        # Проверяем, что это не инициализация
        if not ctx.triggered:
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update
        
        triggered_id = ctx.triggered[0]['prop_id']
        
        # Если триггер от кнопок примеров - очищаем результаты
        if 'kernel-example' in triggered_id or 'rhs-example' in triggered_id:
            empty_display = html.Div("Выберите пример и нажмите 'Решить уравнение'", 
                                    style={'color': '#7F8C8D'})
            empty_fig = create_empty_figure()
            return (empty_display, "", "", {'display': 'none'}, 
                    html.Div(""), {'display': 'none'}, empty_fig, empty_fig, "")
        
        # Если изменились поля ввода
        if 'kernel-input' in triggered_id or 'rhs-input' in triggered_id:
            # Проверяем, что поля не пустые и валидные
            if kernel_val and rhs_val and kernel_val.strip() and rhs_val.strip():
                kernel_valid, _ = validate_expression_detailed(kernel_val, ['x', 't'])
                rhs_valid, _ = validate_expression_detailed(rhs_val, ['x'])
                
                if kernel_valid and rhs_valid:
                    # Если выражения валидны, показываем сообщение что нужно нажать кнопку
                    waiting_display = html.Div("--- Нажмите 'Решить уравнение' для вычислений ---", 
                                              style={'color': '#7F8C8D'})
                    waiting_fig = create_empty_figure()
                    return (waiting_display, "", "", {'display': 'none'}, 
                            html.Div(""), {'display': 'none'}, waiting_fig, waiting_fig, "")
        
        # Для любых других изменений - полная очистка
        empty_display = html.Div("--- Нажмите 'Решить уравнение' ---", style={'color': '#7F8C8D'})
        empty_fig = create_empty_figure()
        return (empty_display, "", "", {'display': 'none'}, 
                html.Div(""), {'display': 'none'}, empty_fig, empty_fig, "")
    
    @app.callback(
        Output('history-modal', 'style'),
        [Input('history-toggle-btn', 'n_clicks'),
         Input('close-history-modal', 'n_clicks')],
        prevent_initial_call=False
    )
    def toggle_history_modal(open_clicks, close_clicks):
        ctx = callback_context
        if not ctx.triggered:
            return {'position': 'fixed', 'top': '0', 'left': '0', 'width': '100%', 'height': '100%',
                    'backgroundColor': 'rgba(0,0,0,0.5)', 'zIndex': '1000', 'display': 'none',
                    'backdropFilter': 'blur(5px)'}
        
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if triggered_id == 'history-toggle-btn' and open_clicks:
            return {'position': 'fixed', 'top': '0', 'left': '0', 'width': '100%', 'height': '100%',
                    'backgroundColor': 'rgba(0,0,0,0.5)', 'zIndex': '1000', 'display': 'flex',
                    'alignItems': 'center', 'justifyContent': 'center', 'backdropFilter': 'blur(5px)'}
        else:
            return {'position': 'fixed', 'top': '0', 'left': '0', 'width': '100%', 'height': '100%',
                    'backgroundColor': 'rgba(0,0,0,0.5)', 'zIndex': '1000', 'display': 'none',
                    'backdropFilter': 'blur(5px)'}
    
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
            return {'display': 'none', 'marginTop': '10px'}, '▼ Примеры ядер K(x,t):', {'expanded': False}
        
        if state.get('expanded', False):
            return {'display': 'none', 'marginTop': '10px'}, '▼ Примеры ядер K(x,t):', {'expanded': False}
        else:
            return {'display': 'block', 'marginTop': '10px', 'animation': 'fadeIn 0.3s ease-in'}, '▲ Примеры ядер K(x,t):', {'expanded': True}

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
            return {'display': 'none', 'marginTop': '10px'}, '▼ Примеры правых частей f(x):', {'expanded': False}
        
        if state.get('expanded', False):
            return {'display': 'none', 'marginTop': '10px'}, '▼ Примеры правых частей f(x):', {'expanded': False}
        else:
            return {'display': 'block', 'marginTop': '10px', 'animation': 'fadeIn 0.3s ease-in'}, '▲ Примеры правых частей f(x):', {'expanded': True}

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
        
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        triggered_dict = json.loads(triggered_id.replace("'", '"'))
        
        if triggered_dict['type'] == 'kernel-example':
            example_name = list(KERNEL_EXAMPLES.keys())[triggered_dict['index']]
            return KERNEL_EXAMPLES[example_name], no_update
        else:
            example_name = list(RHS_EXAMPLES.keys())[triggered_dict['index']]
            return no_update, RHS_EXAMPLES[example_name]
    
    @app.callback(
        [Output('legend-content', 'style'),
         Output('legend-state', 'data')],
        Input('legend-toggle', 'n_clicks'),
        State('legend-state', 'data'),
        prevent_initial_call=True
    )
    def toggle_legend(n_clicks, state):
        if n_clicks is None:
            return {'display': 'none', 'marginTop': '10px'}, state
        if state.get('expanded', False):
            return {'display': 'none', 'marginTop': '10px'}, {'expanded': False}
        else:
            return {'display': 'block', 'marginTop': '10px', 'animation': 'fadeIn 0.3s ease-in'}, {'expanded': True}
    
    @app.callback(
        Output('equation-display', 'children'),
        [Input('kernel-input', 'value'),
         Input('rhs-input', 'value')]
    )
    def update_equation_display(kernel_expr, rhs_expr):
        if not kernel_expr or not rhs_expr:
            return html.Div([
                html.Div("Введите выражения для ядра K(x,t) и правой части f(x)", 
                        style={'color': '#7F8C8D', 'fontStyle': 'italic', 'textAlign': 'center'})
            ])
        return format_equation_beautifully(kernel_expr, rhs_expr)
    
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
        error_text = ""
    
        if kernel_expr and kernel_expr.strip():
            valid, msg = validate_expression_detailed(kernel_expr, ['x', 't'])
            if not valid:
                kernel_valid = False
                kernel_error = msg
        elif not kernel_expr or not kernel_expr.strip():
            kernel_valid = False
            kernel_error = "поле ядра пусто"
        
        if rhs_expr and rhs_expr.strip():
            valid, msg = validate_expression_detailed(rhs_expr, ['x'])
            if not valid:
                rhs_valid = False
                rhs_error = msg
        elif not rhs_expr or not rhs_expr.strip():
            rhs_valid = False
            rhs_error = "поле правой части пусто"
        
        if not kernel_valid and not rhs_valid:
            error_text = f"Ошибки: в ядре - {kernel_error}, в правой части - {rhs_error}"
        elif not kernel_valid:
            error_text = f"Ошибка в ядре K(x,t): {kernel_error}"
        elif not rhs_valid:
            error_text = f"Ошибка в правой части f(x): {rhs_error}"
        
        button_disabled = not (kernel_valid and rhs_valid)
        
        if button_disabled:
            button_title = "Исправьте ошибки в выражениях"
        else:
            button_title = "Решить уравнение"
        
        if error_text:
            error_style = {'display': 'block', 'className': 'error-message'}
            return (button_disabled, button_title, error_text, error_style)
        else:
            return (button_disabled, button_title, "", {"display": "none"})
    
    # CALLBACK ДЛЯ ВЫВОДА ФОРМУЛЫ РЕШЕНИЯ
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
    def compute_and_display(n_clicks, kernel_expr, rhs_expr, initial_condition,
                            sec_x_min, sec_x_max, surf_x_min, surf_x_max, surf_t_min, surf_t_max):
        """Вычисляет решение и выводит все результаты"""
        if n_clicks is None:
            raise PreventUpdate
        
        if not kernel_expr or not kernel_expr.strip():
            raise PreventUpdate
        if not rhs_expr or not rhs_expr.strip():
            raise PreventUpdate
        
        kernel_valid, _ = validate_expression_detailed(kernel_expr, ['x', 't'])
        if not kernel_valid:
            raise PreventUpdate
        rhs_valid, _ = validate_expression_detailed(rhs_expr, ['x'])
        if not rhs_valid:
            raise PreventUpdate
        
        if initial_condition is None:
            initial_condition = 0.0
        
        try:
            # Получаем численное решение
            (fig_solution, fig_derivative, error_text, 
             computation_time, x_vals, phi_numerical, phi_reference) = run_volterra_solution(
                kernel_expr, rhs_expr, initial_condition, 1000, 200)
            
            # Строим графики ядра
            fig_sections = build_sections_plot(kernel_expr, sec_x_min, sec_x_max)
            fig_surface = build_surface_plot(kernel_expr, surf_x_min, surf_x_max, surf_t_min, surf_t_max)
            
            # Подбираем аналитическую формулу
            formula = fit_analytical_formula(x_vals, phi_numerical)
            
            if formula:
                display_html = html.Div([
                    html.Span("φ(x) = ", style={'fontWeight': 'bold', 'color': '#2C3E50', 'fontSize': '1.2em'}),
                    html.Span(formula, style={'color': '#2C3E50', 'fontFamily': 'monospace', 'fontSize': '1.4em', 'fontWeight': 'bold'})
                ])
            else:
                # Если формула не подобралась, выводим таблицу значений
                points = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
                values_html = []
                for xp in points:
                    idx = int(xp * len(x_vals))
                    if idx < len(phi_numerical):
                        values_html.append(html.Div(
                            f"φ({xp}) = {phi_numerical[idx]:.6f}", 
                            style={'fontFamily': 'monospace', 'margin': '3px 0', 'color': '#2C3E50'}
                        ))
                
                display_html = html.Div([
                    html.Span("Численное решение (аналитическая формула не найдена):", 
                             style={'fontWeight': 'bold', 'color': '#2C3E50'}),
                    html.Div(values_html, style={
                        'marginTop': '10px',
                        'padding': '10px',
                        'backgroundColor': '#F5F7FA',
                        'borderRadius': '8px',
                        'textAlign': 'left'
                    })
                ])
            
            max_error_display = html.Div([
                html.Div(
                    error_text,
                    style={
                        'fontWeight': 'bold',
                        'color': '#C0392B',
                        'fontSize': '1.1em',
                        'textAlign': 'center',
                        'padding': '12px 24px',
                        'background': "#E9F1F5",
                        'borderRadius': '12px',
                        'border': '1px solid #E8DCD0',
                        'display': 'inline-block'
                    }
                )
            ], style={'display': 'flex', 'justifyContent': 'center', 'margin': '30px 0 20px 0'})
            
            status_message = html.Div([
                html.Span("Вычисление успешно завершено! ", style={'fontWeight': 'bold', 'color': '#2C3E50'}),
                html.Span(f"Время: {computation_time:.2f} с", style={'color': '#7F8C8D'})
            ], style={'color': '#27ae60'})
            
            return (display_html, "", status_message, {'textAlign': 'center', 'margin': '10px'},
                    max_error_display, {'display': 'block'},
                    fig_solution, fig_derivative, error_text,
                    fig_sections, fig_surface)
            
        except Exception as e:
            error_msg = str(e)
            if "Ошибка при вычислении функции:" in error_msg:
                error_msg = error_msg.split("Ошибка при вычислении функции:")[-1].strip()
            
            error_status = html.Div([
                html.Span("Ошибка! ", style={'fontWeight': 'bold', 'color': '#E74C3C'}),
                html.Div(error_msg, style={'fontSize': '0.9em', 'marginTop': '10px', 'color': '#C0392B'})
            ], style={'color': '#E74C3C'})
            
            empty_fig = create_empty_figure()
            empty_display = html.Div(f"Ошибка: {error_msg}", style={'color': '#E74C3C'})
            
            return (empty_display, "", error_status, {'textAlign': 'center', 'margin': '10px'},
                    html.Div(""), {'display': 'none'},
                    empty_fig, empty_fig, "Ошибка вычислений",
                    empty_fig, empty_fig)

    @app.callback(
        Output('history-list', 'children'),
        [Input('solutions-history', 'data'),
         Input('clear-history-btn', 'n_clicks')],
        prevent_initial_call=False
    )
    def update_history_list(history_data, clear_clicks):
        ctx = callback_context
        
        if clear_clicks and ctx.triggered and 'clear-history-btn' in ctx.triggered[0]['prop_id']:
            return html.Div("История пуста", 
                          style={'color': '#95A5A6', 'fontStyle': 'italic', 'textAlign': 'center', 'padding': '20px'})
        
        if not history_data or len(history_data) == 0:
            return html.Div("История пуста", 
                          style={'color': '#95A5A6', 'fontStyle': 'italic', 'textAlign': 'center', 'padding': '20px'})
        
        history_items = []
        for record in history_data:
            if not isinstance(record, dict) or 'id' not in record:
                continue
                
            kernel_preview = record['kernel'][:50] + '...' if len(record['kernel']) > 50 else record['kernel']
            rhs_preview = record['rhs'][:50] + '...' if len(record['rhs']) > 50 else record['rhs']
            
            history_item = html.Div(
                children=[
                    html.Div(
                        children=[
                            html.Div(
                                children=[
                                    html.Span(f"{record['timestamp']} | {record['date']}", 
                                             style={'fontWeight': 'bold', 'color': '#2C3E50', 'fontSize': '0.9em'}),
                                    html.Span(f" | φ(0)={record.get('initial_condition', 0)}", 
                                             style={'color': '#7F8C8D', 'fontSize': '0.85em', 'marginLeft': '10px'}),
                                ]
                            ),
                            html.Div(
                                children=[
                                    html.Small(f"K(x,t) = {kernel_preview}", 
                                             style={'color': '#34495E', 'fontFamily': 'monospace'}),
                                    html.Br(),
                                    html.Small(f"f(x) = {rhs_preview}", 
                                             style={'color': '#E74C3C', 'fontFamily': 'monospace'}),
                                ], 
                                style={'marginLeft': '15px', 'marginTop': '5px', 'marginBottom': '5px'}
                            ),
                            html.Div(
                                children=[
                                    html.Button(
                                        html.Img(
                                            src='/assets/load-icon.png',
                                            style={'width': '20px', 'height': '20px', 'display': 'block'}
                                        ),
                                        id={'type': 'load-solution', 'index': record['id']},
                                        style={
                                            'padding': '8px',
                                            'marginRight': '8px',
                                            'backgroundColor': "#FFFFFF",
                                            'border': '1px solid #D1D9E6',
                                            'borderRadius': '5px',
                                            'cursor': 'pointer',
                                            'display': 'inline-flex',
                                            'alignItems': 'center',
                                            'justifyContent': 'center'
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
                                            'padding': '8px',
                                            'backgroundColor': "#FFFFFF",
                                            'border': '1px solid #D1D9E6',
                                            'borderRadius': '5px',
                                            'cursor': 'pointer',
                                            'display': 'inline-flex',
                                            'alignItems': 'center',
                                            'justifyContent': 'center'
                                        },
                                        title="Удалить из истории"
                                    ),
                                ], 
                                style={'marginTop': '8px', 'textAlign': 'right'}
                            )
                        ], 
                        style={'padding': '12px', 'borderBottom': '1px solid #D1D9E6',
                               'marginBottom': '8px', 'borderRadius': '8px',
                               'backgroundColor': 'white', 'border': '1px solid #D1D9E6'}
                    )
                ],
                id=f'history-item-{record["id"]}'
            )
            history_items.append(history_item)
        
        return history_items

    @app.callback(
        [Output('kernel-input', 'value', allow_duplicate=True),
         Output('rhs-input', 'value', allow_duplicate=True),
         Output('initial-condition', 'value', allow_duplicate=True),
         Output('volterra-graph', 'figure', allow_duplicate=True),
         Output('derivative-plot', 'figure', allow_duplicate=True),
         Output('error-output', 'children', allow_duplicate=True),
         Output('status-message', 'children', allow_duplicate=True),
         Output('status-message', 'style', allow_duplicate=True),
         Output('history-modal', 'style', allow_duplicate=True),
         Output('solve-button', 'n_clicks', allow_duplicate=True),
         Output('max-error-display', 'children', allow_duplicate=True),
         Output('max-error-display', 'style', allow_duplicate=True),
         Output('kernel-sections-plot', 'figure', allow_duplicate=True),
         Output('kernel-3d-plot', 'figure', allow_duplicate=True),
         Output('analytical-solution-display', 'children', allow_duplicate=True),
         Output('guess-accuracy', 'children', allow_duplicate=True)],
        [Input({'type': 'load-solution', 'index': ALL}, 'n_clicks')],
        [State('solutions-history', 'data'),
         State('sections-x-min', 'value'),
         State('sections-x-max', 'value'),
         State('surf-x-min', 'value'),
         State('surf-x-max', 'value'),
         State('surf-t-min', 'value'),
         State('surf-t-max', 'value')],
        prevent_initial_call='initial_duplicate'
    )
    def load_solution(load_clicks, history_data, sec_x_min, sec_x_max,
                       surf_x_min, surf_x_max, surf_t_min, surf_t_max):
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate
        if ctx.triggered[0].get('value') is None:
            raise PreventUpdate
        if not history_data:
            raise PreventUpdate
        solution_id = _pattern_button_index(ctx)
        if solution_id is None:
            raise PreventUpdate
        
        for record in history_data:
            if str(record.get('id')) != str(solution_id):
                continue
            if not all(k in record for k in ('kernel', 'rhs')):
                continue
            try:
                initial_cond = record.get('initial_condition', 0.0)
                (fig_solution, fig_derivative, err_text, 
                 _t, x_vals, phi_numerical, _phi_ref) = run_volterra_solution(
                    record['kernel'], record['rhs'], initial_cond, 1000, 200
                )
                
                fig_sections = build_sections_plot(record['kernel'], sec_x_min, sec_x_max)
                fig_surface = build_surface_plot(record['kernel'], surf_x_min, surf_x_max, surf_t_min, surf_t_max)
                
                # Подбираем формулу для загруженного решения
                formula = fit_analytical_formula(x_vals, phi_numerical)
                if formula:
                    display_html = html.Div([
                        html.Span("φ(x) = ", style={'fontWeight': 'bold', 'color': '#2C3E50', 'fontSize': '1.2em'}),
                        html.Span(formula, style={'color': '#2C3E50', 'fontFamily': 'monospace', 'fontSize': '1.4em', 'fontWeight': 'bold'})
                    ])
                else:
                    display_html = html.Div("--- Формула не подобрана ---", style={'color': '#7F8C8D'})
                
                max_error_display = html.Div([
                    html.Span(err_text, style={'fontWeight': 'bold', 'color': '#E74C3C', 'fontSize': '1.1em'})
                ])
                
                status_msg = html.Div([
                    html.Span("Загружено из истории! ", style={'fontWeight': 'bold', 'color': '#2C3E50'}),
                    html.Span(f"{record.get('timestamp', '')} {record.get('date', '')}", style={'color': '#7F8C8D'})
                ], style={'color': '#27ae60', 'textAlign': 'center', 'padding': '10px'})
                
                modal_closed_style = {'position': 'fixed', 'top': '0', 'left': '0', 'width': '100%', 'height': '100%',
                                      'backgroundColor': 'rgba(0,0,0,0.5)', 'zIndex': '1000', 'display': 'none',
                                      'backdropFilter': 'blur(5px)'}
                
                return (record['kernel'], record['rhs'], initial_cond,
                        fig_solution, fig_derivative, err_text,
                        status_msg, {'textAlign': 'center', 'margin': '10px'},
                        modal_closed_style,
                        1,
                        max_error_display,
                        {'display': 'block'},
                        fig_sections,
                        fig_surface,
                        display_html,
                        "")
                
            except Exception as e:
                error_msg = str(e)
                status_msg = html.Div([
                    html.Span("Ошибка! ", style={'fontWeight': 'bold', 'color': '#E74C3C'}),
                    html.Div(error_msg, style={'fontSize': '0.9em', 'marginTop': '10px', 'color': '#C0392B'})
                ], style={'color': '#E74C3C', 'textAlign': 'center', 'padding': '10px'})
                empty_fig = create_empty_figure()
                empty_error_display = html.Div("")
                empty_kernel_fig = create_empty_figure()
                empty_display = html.Div("--- Ошибка загрузки ---", style={'color': '#E74C3C'})
                return (
                    no_update, no_update, no_update,
                    empty_fig, empty_fig,
                    no_update,
                    status_msg,
                    {'textAlign': 'center', 'margin': '10px'},
                    {'position': 'fixed', 'top': '0', 'left': '0', 'width': '100%', 'height': '100%',
                     'backgroundColor': 'rgba(0,0,0,0.5)', 'zIndex': '1000', 'display': 'none',
                     'backdropFilter': 'blur(5px)'},
                    None,
                    empty_error_display,
                    {'display': 'none'},
                    empty_kernel_fig,
                    empty_kernel_fig,
                    empty_display,
                    ""
                )
        
        raise PreventUpdate
    
    @app.callback(
        Output('solutions-history', 'data', allow_duplicate=True),
        [Input('solve-button', 'n_clicks')],
        [State('kernel-input', 'value'),
         State('rhs-input', 'value'),
         State('initial-condition', 'value'),
         State('solutions-history', 'data')],
        prevent_initial_call=True
    )
    def save_solution_to_history(n_clicks, kernel_expr, rhs_expr, initial_condition, history_data):
        if n_clicks is None:
            raise PreventUpdate
        
        if not kernel_expr or not rhs_expr:
            raise PreventUpdate
        
        # Проверяем валидность выражений
        kernel_valid, _ = validate_expression_detailed(kernel_expr, ['x', 't'])
        rhs_valid, _ = validate_expression_detailed(rhs_expr, ['x'])
        
        if not kernel_valid or not rhs_valid:
            raise PreventUpdate
        
        # Получаем время вычисления (нужно вычислить решение)
        try:
            _, _, _, computation_time, _, _, _ = run_volterra_solution(
                kernel_expr, rhs_expr, initial_condition or 0, 1000, 200)
        except:
            computation_time = 0
        
        solution_record = {
            'id': str(uuid.uuid4()),
            'timestamp': time.strftime("%H:%M:%S"),
            'date': time.strftime("%d.%m.%Y"),
            'kernel': kernel_expr,
            'rhs': rhs_expr,
            'initial_condition': initial_condition or 0,
            'computation_time': computation_time,
        }
        
        hist = []
        for r in (history_data if isinstance(history_data, list) else []):
            if isinstance(r, dict) and r.get('id'):
                hist.append(r)
        
        new_history = [solution_record] + hist
        new_history = new_history[:20]
        
        return new_history
    
    @app.callback(
        Output('solutions-history', 'data', allow_duplicate=True),
        [Input({'type': 'delete-solution', 'index': ALL}, 'n_clicks')],
        [State('solutions-history', 'data')],
        prevent_initial_call='initial_duplicate'
    )
    def delete_solution(delete_clicks, history_data):
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate
        if ctx.triggered[0].get('value') is None:
            raise PreventUpdate
        if not history_data:
            raise PreventUpdate
        solution_id = _pattern_button_index(ctx)
        if solution_id is None:
            raise PreventUpdate
        
        new_history = [
            record for record in history_data
            if str(record.get('id')) != str(solution_id)
        ]
        
        return new_history
    
    @app.callback(
        Output('solutions-history', 'data', allow_duplicate=True),
        [Input('clear-history-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def clear_all_history(clear_clicks):
        if clear_clicks:
            return []
        raise PreventUpdate