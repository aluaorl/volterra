# calculation_engine.py (Revised Version 2)
import numpy as np
from scipy.interpolate import interp1d
from expression_parser import parse_user_input, safe_eval_with_checks
import math 

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
            import re
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
        
        # k1
        I1 = trapezoidal_sum(x, phi, i+1, xi, K_func_optimized, h)
        k1 = h * (f_xi + I1)
        
        # k2
        phi_mid1 = yi + k1 / 2
        x_mid = xi + h / 2
        f_mid = f_func_optimized(x_mid) 
        I2 = trapezoidal_sum_extended(x, phi, i+1, x_mid, K_func_optimized, h, phi_mid1)
        k2 = h * (f_mid + I2)
        
        # k3
        phi_mid2 = yi + k2 / 2
        I3 = trapezoidal_sum_extended(x, phi, i+1, x_mid, K_func_optimized, h, phi_mid2)
        k3 = h * (f_mid + I3)
        
        # k4
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
    
    base_namespace = {'np': np, 'math': math} # Добавляем math
    
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