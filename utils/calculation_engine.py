import numpy as np
import time
from scipy.interpolate import interp1d
from .expression_parser import parse_user_input, safe_eval_with_checks
import math

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

def solve_volterra_RK4_trapezoidal(x, h, K_func, f_func, phi0):
    N = len(x) - 1
    phi = np.zeros(N + 1)
    phi[0] = phi0
        
    for i in range(N):
        xi = x[i]
        yi = phi[i]
        f_xi = f_func(xi)
        
        I1 = trapezoidal_sum(x, phi, i+1, xi, K_func, h)
        k1 = h * (f_xi + I1)
        
        phi_mid1 = yi + k1 / 2
        x_mid = xi + h / 2
        f_mid = f_func(x_mid)
        I2 = trapezoidal_sum_extended(x, phi, i+1, x_mid, K_func, h, phi_mid1)
        k2 = h * (f_mid + I2)
        
        phi_mid2 = yi + k2 / 2
        I3 = trapezoidal_sum_extended(x, phi, i+1, x_mid, K_func, h, phi_mid2)
        k3 = h * (f_mid + I3)
        
        phi_next_est = yi + k3
        x_next = xi + h
        f_next = f_func(x_next)
        I4 = trapezoidal_sum_extended(x, phi, i+1, x_next, K_func, h, phi_next_est)
        k4 = h * (f_next + I4)
        
        phi[i+1] = yi + (k1 + 2*k2 + 2*k3 + k4) / 6
    
    return phi

def get_reference_solution(x, K_func, f_func, phi0, N_ref=200):
    h_ref = (x[-1] - x[0]) / N_ref
    x_ref = np.linspace(x[0], x[-1], N_ref + 1)
    phi_ref = solve_volterra_RK4_trapezoidal(x_ref, h_ref, K_func, f_func, phi0)
    interp_func = interp1d(x_ref, phi_ref, kind='cubic')
    return interp_func(x)

def solve_volterra_RK4(x, h, K_func, f_func, initial_condition=0.0):
    phi = solve_volterra_RK4_trapezoidal(x, h, K_func, f_func, initial_condition)
    integral_values = np.zeros(len(x))
    return phi, integral_values

def create_function_from_string(expr_str, var_names):
    parsed_expr = parse_user_input(expr_str, var_names)
    compiled = compile(parsed_expr, '<string>', 'eval')
    base_namespace = {'np': np, 'math': math}
    
    def func_optimized(*args):
        try:
            local_vars = {var_name: var_value for var_name, var_value in zip(var_names, args)}
            return safe_eval_with_checks(compiled, {**base_namespace, **local_vars})
        except Exception as e:
            raise ValueError(f"Ошибка при вычислении функции: {str(e)}")
    
    return func_optimized

def run_volterra_solution(kernel_expr, rhs_expr, initial_condition, N_points=1000, N_ref=200):
    start_time = time.time()
    
    K_func = create_function_from_string(kernel_expr, ['x', 't'])
    f_func = create_function_from_string(rhs_expr, ['x'])
    
    a, b = 0, 1
    h = (b - a) / N_points
    x = np.linspace(a, b, N_points + 1)

    phi_numerical, integral_values = solve_volterra_RK4(x, h, K_func, f_func, initial_condition)
    phi_reference = get_reference_solution(x, K_func, f_func, initial_condition, N_ref)
    f_values = np.array([f_func(xi) for xi in x])
    
    derivative_numerical = np.gradient(phi_numerical, h)
    derivative_exact = f_values + integral_values
    
    error = np.abs(phi_numerical - phi_reference)
    max_error = np.max(error)
    error_text = f'Глобальная погрешность в равномерной норме l_inf: {max_error:.2e}'
    computation_time = time.time() - start_time
    
    return (x, phi_numerical, phi_reference, derivative_numerical, derivative_exact, 
            error_text, computation_time, integral_values)