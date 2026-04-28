# calculation_engine.py
import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
from expression_parser import parse_user_input, safe_eval_with_checks
import math
import time
import plotly.graph_objs as go
import re

def safe_function_evaluation(func, *args):
    try:
        result = func(*args)
        if isinstance(result, complex):
            raise ValueError("Выражение дает комплексное число")
        if isinstance(result, (int, float, np.number)):
            if np.isinf(result):
                raise ValueError("Обнаружена бесконечность")
            if np.isnan(result):
                raise ValueError("Обнаружена неопределенность")
        return result
    except Exception as e:
        error_msg = str(e).lower()
        if "division by zero" in error_msg:
            raise ValueError("Обнаружено деление на ноль")
        elif "invalid value" in error_msg:
            raise ValueError("Некорректное математическое выражение")
        elif "math domain error" in error_msg:
            raise ValueError("Ошибка области определения функции")
        elif "name" in error_msg and "is not defined" in error_msg:
            match = re.search(r"name '([^']+)' is not defined", error_msg)
            if match:
                func_name = match.group(1)
                raise ValueError(f"Неизвестная функция или переменная '{func_name}'")
            raise ValueError(str(e))
        else:
            raise ValueError(str(e))

def trapezoidal_sum(x_set, phi_set, n, target_x, K_func, h):
    s = 0.0
    if n > 1:
        for j in range(n-1):
            val1 = K_func(target_x, x_set[j]) * phi_set[j]
            val2 = K_func(target_x, x_set[j+1]) * phi_set[j+1]
            s += (h / 2) * (val1 + val2)
    return s

def trapezoidal_sum_extended(x_set, phi_set, n, target_x, K_func, h, phi_val):
    s = trapezoidal_sum(x_set, phi_set, n, target_x, K_func, h)
    h_last = target_x - x_set[n-1]
    if h_last > 1e-12:
        val1 = K_func(target_x, x_set[n-1]) * phi_set[n-1]
        val2 = K_func(target_x, target_x) * phi_val
        s += (h_last / 2) * (val1 + val2)
    return s

def solve_volterra_RK4_trapezoidal(x, h, K_func_optimized, f_func_optimized, phi0):
    N = len(x) - 1
    phi = np.zeros(N + 1)
    phi[0] = phi0
        
    for i in range(N):
        xi = x[i]
        yi = phi[i]
        f_xi = f_func_optimized(xi)
        
        I1 = trapezoidal_sum(x, phi, i+1, xi, K_func_optimized, h)
        k1 = h * (f_xi + I1)
        
        phi_mid1 = yi + k1 / 2
        x_mid = xi + h / 2
        f_mid = f_func_optimized(x_mid)
        I2 = trapezoidal_sum_extended(x, phi, i+1, x_mid, K_func_optimized, h, phi_mid1)
        k2 = h * (f_mid + I2)
        
        phi_mid2 = yi + k2 / 2
        I3 = trapezoidal_sum_extended(x, phi, i+1, x_mid, K_func_optimized, h, phi_mid2)
        k3 = h * (f_mid + I3)
        
        phi_next_est = yi + k3
        x_next = xi + h
        f_next = f_func_optimized(x_next)
        I4 = trapezoidal_sum_extended(x, phi, i+1, x_next, K_func_optimized, h, phi_next_est)
        k4 = h * (f_next + I4)
        
        phi[i+1] = yi + (k1 + 2*k2 + 2*k3 + k4) / 6
    
    return phi

def get_reference_solution(x, K_func_optimized, f_func_optimized, phi0, N_ref=200):
    h_ref = (x[-1] - x[0]) / N_ref
    x_ref = np.linspace(x[0], x[-1], N_ref + 1)
    phi_ref = solve_volterra_RK4_trapezoidal(x_ref, h_ref, K_func_optimized, f_func_optimized, phi0)
    interp_func = interp1d(x_ref, phi_ref, kind='cubic')
    return interp_func(x)

def solve_volterra_RK4(x, h, K_func_optimized, f_func_optimized, initial_condition=0.0):
    phi = solve_volterra_RK4_trapezoidal(x, h, K_func_optimized, f_func_optimized, initial_condition)
    integral_values = np.zeros(len(x))
    return phi, integral_values

def create_function_from_string(expr_str, var_names):
    parsed_expr = parse_user_input(expr_str, var_names)
    compiled = compile(parsed_expr, '<string>', 'eval')
    base_namespace = {'np': np, 'math': math}
    
    def func_optimized(*args):
        try:
            local_vars = {}
            for var_name, var_value in zip(var_names, args):
                local_vars[var_name] = var_value
            return safe_eval_with_checks(compiled, {**base_namespace, **local_vars})
        except Exception as e:
            error_msg = str(e)
            if error_msg.startswith("Ошибка вычисления:"):
                error_msg = error_msg.replace("Ошибка вычисления:", "").strip()
            raise ValueError(f"Ошибка при вычислении функции: {error_msg}")
    
    return func_optimized

def fit_analytical_formula(x_values, y_values):
    """
    Подбирает аналитическую формулу для численных данных
    Возвращает строку с формулой
    """
    results = []
    
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
                terms.append(f"{a:.6f}*x²")
            if abs(b) > 1e-10:
                sign = '+' if b > 0 and terms else ''
                terms.append(f"{sign}{b:.6f}*x")
            if abs(c) > 1e-10:
                sign = '+' if c > 0 and terms else ''
                terms.append(f"{sign}{c:.6f}")
            return ''.join(terms)
    except:
        pass
    
    # 4. Степенная: a*x^b
    def power(x, a, b):
        return a * np.power(x + 1e-10, b)
    
    try:
        popt, _ = curve_fit(power, x_values, y_values, maxfev=10000)
        a, b = popt
        y_pred = power(x_values, a, b)
        max_error = np.max(np.abs(y_values - y_pred))
        
        if max_error < 1e-6:
            return f"{a:.6f}*x^{b:.6f}"
    except:
        pass
    
    # 5. Экспоненциальная: a*exp(b*x) + c
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
    
    # 6. Синус: a*sin(b*x + c) + d
    def sin_func(x, a, b, c, d):
        return a * np.sin(b * x + c) + d
    
    try:
        p0 = [np.std(y_values), 2*np.pi, 0, np.mean(y_values)]
        popt, _ = curve_fit(sin_func, x_values, y_values, p0=p0, maxfev=10000)
        a, b, c, d = popt
        y_pred = sin_func(x_values, a, b, c, d)
        max_error = np.max(np.abs(y_values - y_pred))
        
        if max_error < 1e-6:
            if abs(d) < 1e-10:
                return f"{a:.6f}*sin({b:.6f}*x + {c:.6f})"
            return f"{a:.6f}*sin({b:.6f}*x + {c:.6f}) + {d:.6f}"
    except:
        pass
    
    # 7. Сумма синуса и косинуса
    def sin_cos(x, a, b, w, c):
        return a * np.sin(w * x) + b * np.cos(w * x) + c
    
    try:
        p0 = [np.std(y_values), np.std(y_values), 2*np.pi, np.mean(y_values)]
        popt, _ = curve_fit(sin_cos, x_values, y_values, p0=p0, maxfev=10000)
        a, b, w, c = popt
        y_pred = sin_cos(x_values, a, b, w, c)
        max_error = np.max(np.abs(y_values - y_pred))
        
        if max_error < 1e-6:
            terms = []
            if abs(a) > 1e-10:
                terms.append(f"{a:.6f}*sin({w:.6f}*x)")
            if abs(b) > 1e-10:
                sign = '+' if b > 0 and terms else ''
                terms.append(f"{sign}{b:.6f}*cos({w:.6f}*x)")
            if abs(c) > 1e-10:
                sign = '+' if c > 0 and terms else ''
                terms.append(f"{sign}{c:.6f}")
            return ''.join(terms)
    except:
        pass
    
    # 8. Затухающий синус: a*sin(b*x + c)*exp(d*x) + e
    def damped_sine(x, a, b, c, d, e):
        return a * np.sin(b * x + c) * np.exp(d * x) + e
    
    try:
        p0 = [np.std(y_values), 2*np.pi, 0, -0.2, np.mean(y_values)]
        popt, _ = curve_fit(damped_sine, x_values, y_values, p0=p0, maxfev=10000)
        a, b, c, d, e = popt
        y_pred = damped_sine(x_values, a, b, c, d, e)
        max_error = np.max(np.abs(y_values - y_pred))
        
        if max_error < 1e-6:
            if abs(e) < 1e-10:
                return f"{a:.6f}*sin({b:.6f}*x + {c:.6f})*exp({d:.6f}*x)"
            return f"{a:.6f}*sin({b:.6f}*x + {c:.6f})*exp({d:.6f}*x) + {e:.6f}"
    except:
        pass
    
    # Если ничего не подошло, возвращаем полиномиальную аппроксимацию
    try:
        coeffs = np.polyfit(x_values, y_values, 3)
        terms = []
        for i, coef in enumerate(coeffs):
            if abs(coef) > 1e-10:
                power = 3 - i
                if power == 3:
                    terms.append(f"{coef:.6f}*x³")
                elif power == 2:
                    sign = '+' if coef > 0 else ''
                    terms.append(f"{sign}{coef:.6f}*x²")
                elif power == 1:
                    sign = '+' if coef > 0 else ''
                    terms.append(f"{sign}{coef:.6f}*x")
                else:
                    sign = '+' if coef > 0 else ''
                    terms.append(f"{sign}{coef:.6f}")
        return ''.join(terms) if terms else "0"
    except:
        pass
    
    return None

def run_volterra_solution_core(kernel_expr, rhs_expr, initial_condition, N_points=1000, N_ref=200):
    start_time = time.time()
    
    if not kernel_expr or not kernel_expr.strip():
        raise ValueError("Выражение для ядра K(x,t) не может быть пустым")
    if not rhs_expr or not rhs_expr.strip():
        raise ValueError("Выражение для правой части f(x) не может быть пустым")
    
    K_current = create_function_from_string(kernel_expr, ['x', 't'])
    f_current = create_function_from_string(rhs_expr, ['x'])
    
    a, b = 0, 1
    h = (b - a) / N_points
    x = np.linspace(a, b, N_points + 1)
    
    phi_numerical, integral_values = solve_volterra_RK4(x, h, K_current, f_current, initial_condition)
    phi_reference = get_reference_solution(x, K_current, f_current, initial_condition, N_ref)
    
    derivative_numerical = np.gradient(phi_numerical, h)
    
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
    fig_derivative.update_layout(
        title='', xaxis_title='x', yaxis_title="φ'(x)", hovermode='x unified',
        template='plotly_white', height=400, showlegend=True,
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family="Roboto, sans-serif", size=12, color="#2C3E50")
    )
    
    error = np.abs(phi_numerical - phi_reference)
    max_error = np.max(error)
    error_text = f'Глобальная погрешность: {max_error:.2e}'
    computation_time = time.time() - start_time
    
    return (fig_solution, fig_derivative, error_text, computation_time, x, phi_numerical, phi_reference)