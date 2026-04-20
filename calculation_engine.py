# calculation_engine.py
import numpy as np
from scipy.interpolate import interp1d
from expression_parser import parse_user_input, safe_eval_with_checks

def safe_function_evaluation(func, *args):
    """Безопасное вычисление функции с проверкой ошибок"""
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


def solve_integro_differential_combined(x, h, K, f, initial_condition=0.0):
    """
    Комбинированный метод для интегро-дифференциального уравнения
    ОПТИМИЗИРОВАННАЯ ВЕРСИЯ (без numba)
    """
    N = len(x) - 1
    phi = np.zeros(N + 1)
    phi[0] = initial_condition
    
    # Предвычисление всех значений f(x)
    f_values = np.zeros(N + 1)
    for idx, xi in enumerate(x):
        f_values[idx] = safe_function_evaluation(f, xi)
    
    # Кеш для значений ядра (ускоряет повторные вызовы)
    K_cache = {}
    
    def get_K(x_val, t_val):
        # Округляем для точности кеширования
        key = (round(x_val, 10), round(t_val, 10))
        if key not in K_cache:
            K_cache[key] = safe_function_evaluation(K, x_val, t_val)
        return K_cache[key]
    
    integral_values = np.zeros(N + 1)
    integral_values[0] = 0.0
    
    x_arr = x
    
    for i in range(N):
        xi = x_arr[i]
        yi = phi[i]
        
        # Вычисление интеграла I(xi) методом трапеций
        I_xi = 0.0
        if i > 0:
            # Используем простой цикл (быстрее чем создавать много массивов)
            for j in range(i):
                K_j = get_K(xi, x_arr[j])
                K_jp1 = get_K(xi, x_arr[j+1])
                I_xi += (K_j * phi[j] + K_jp1 * phi[j+1]) * (h * 0.5)
        
        k1 = h * (f_values[i] + I_xi)
        
        # k2
        x_mid = xi + h * 0.5
        I_mid = 0.0
        if i > 0:
            for j in range(i):
                K_mid_j = get_K(x_mid, x_arr[j])
                K_mid_jp1 = get_K(x_mid, x_arr[j+1])
                I_mid += (K_mid_j * phi[j] + K_mid_jp1 * phi[j+1]) * (h * 0.5)
        
        phi_mid_guess = yi + k1 * 0.5
        K_mid_xi = get_K(x_mid, xi)
        K_mid_mid = get_K(x_mid, x_mid)
        I_mid += (K_mid_xi * yi + K_mid_mid * phi_mid_guess) * (h * 0.25)
        k2 = h * (f_values[i] + I_mid)
        
        # k3
        phi_mid_guess2 = yi + k2 * 0.5
        I_mid2 = 0.0
        if i > 0:
            for j in range(i):
                K_mid_j = get_K(x_mid, x_arr[j])
                K_mid_jp1 = get_K(x_mid, x_arr[j+1])
                I_mid2 += (K_mid_j * phi[j] + K_mid_jp1 * phi[j+1]) * (h * 0.5)
        
        I_mid2 += (K_mid_xi * yi + K_mid_mid * phi_mid_guess2) * (h * 0.25)
        k3 = h * (f_values[i] + I_mid2)
        
        # k4
        x_next = xi + h
        I_next = 0.0
        if i > 0:
            for j in range(i):
                K_next_j = get_K(x_next, x_arr[j])
                K_next_jp1 = get_K(x_next, x_arr[j+1])
                I_next += (K_next_j * phi[j] + K_next_jp1 * phi[j+1]) * (h * 0.5)
        
        phi_next_guess = yi + k3
        K_next_xi = get_K(x_next, xi)
        K_next_next = get_K(x_next, x_next)
        I_next += (K_next_xi * yi + K_next_next * phi_next_guess) * (h * 0.5)
        k4 = h * (f_values[i+1] + I_next)
        
        phi[i+1] = yi + (k1 + 2*k2 + 2*k3 + k4) / 6.0
        integral_values[i+1] = I_next
    
    return phi, integral_values


def get_reference_solution(x, K, f, initial_condition=0.0):
    """
    Эталонное решение для интегро-дифференциального уравнения
    ОПТИМИЗИРОВАННАЯ ВЕРСИЯ
    """
    N_ref = 200  # Уменьшено с 500 до 200 для скорости
    h_ref = (x[-1] - x[0]) / N_ref
    x_ref = np.linspace(x[0], x[-1], N_ref + 1)
    
    f_ref = np.zeros(N_ref + 1)
    for idx, xi in enumerate(x_ref):
        f_ref[idx] = safe_function_evaluation(f, xi)
    
    phi_ref = np.zeros(N_ref + 1)
    phi_ref[0] = initial_condition
    
    # Кеш для значений ядра
    K_cache_ref = {}
    
    def get_K_ref(x_val, t_val):
        key = (round(x_val, 10), round(t_val, 10))
        if key not in K_cache_ref:
            K_cache_ref[key] = safe_function_evaluation(K, x_val, t_val)
        return K_cache_ref[key]
    
    for i in range(N_ref):
        xi = x_ref[i]
        yi = phi_ref[i]
        
        try:
            # Вычисление интеграла I(xi)
            I_xi = 0.0
            if i > 0:
                for j in range(i):
                    t_j = x_ref[j]
                    t_jp1 = x_ref[j+1]
                    K_j = get_K_ref(xi, t_j)
                    K_jp1 = get_K_ref(xi, t_jp1)
                    I_xi += (K_j * phi_ref[j] + K_jp1 * phi_ref[j+1]) * (h_ref * 0.5)
            
            k1 = h_ref * (f_ref[i] + I_xi)
            
            # k2
            x_mid = xi + h_ref * 0.5
            I_mid = 0.0
            if i > 0:
                for j in range(i):
                    t_j = x_ref[j]
                    t_jp1 = x_ref[j+1]
                    K_mid_j = get_K_ref(x_mid, t_j)
                    K_mid_jp1 = get_K_ref(x_mid, t_jp1)
                    I_mid += (K_mid_j * phi_ref[j] + K_mid_jp1 * phi_ref[j+1]) * (h_ref * 0.5)
            
            phi_mid_guess = yi + k1 * 0.5
            K_mid_xi = get_K_ref(x_mid, xi)
            K_mid_mid = get_K_ref(x_mid, x_mid)
            I_mid += (K_mid_xi * yi + K_mid_mid * phi_mid_guess) * (h_ref * 0.25)
            k2 = h_ref * (f_ref[i] + I_mid)
            
            # k3
            phi_mid_guess2 = yi + k2 * 0.5
            I_mid2 = 0.0
            if i > 0:
                for j in range(i):
                    t_j = x_ref[j]
                    t_jp1 = x_ref[j+1]
                    K_mid_j = get_K_ref(x_mid, t_j)
                    K_mid_jp1 = get_K_ref(x_mid, t_jp1)
                    I_mid2 += (K_mid_j * phi_ref[j] + K_mid_jp1 * phi_ref[j+1]) * (h_ref * 0.5)
            
            I_mid2 += (K_mid_xi * yi + K_mid_mid * phi_mid_guess2) * (h_ref * 0.25)
            k3 = h_ref * (f_ref[i] + I_mid2)
            
            # k4
            x_next = xi + h_ref
            I_next = 0.0
            if i > 0:
                for j in range(i):
                    t_j = x_ref[j]
                    t_jp1 = x_ref[j+1]
                    K_next_j = get_K_ref(x_next, t_j)
                    K_next_jp1 = get_K_ref(x_next, t_jp1)
                    I_next += (K_next_j * phi_ref[j] + K_next_jp1 * phi_ref[j+1]) * (h_ref * 0.5)
            
            phi_next_guess = yi + k3
            K_next_xi = get_K_ref(x_next, xi)
            K_next_next = get_K_ref(x_next, x_next)
            I_next += (K_next_xi * yi + K_next_next * phi_next_guess) * (h_ref * 0.5)
            k4 = h_ref * (f_ref[i+1] + I_next)
            
            phi_ref[i+1] = yi + (k1 + 2*k2 + 2*k3 + k4) / 6.0
            
        except Exception as e:
            raise ValueError(str(e))
    
    interp_func = interp1d(x_ref, phi_ref, kind='linear')
    return interp_func(x)


# Основные экспортируемые функции
solve_volterra_RK4 = solve_integro_differential_combined


def create_function_from_string(expr_str, var_names):
    """Создает функцию из строки выражения"""
    parsed_expr = parse_user_input(expr_str, var_names)
    compiled = compile(parsed_expr, '<string>', 'eval')
    
    def func(*args):
        try:
            namespace = {'np': np}
            for var_name, var_value in zip(var_names, args):
                namespace[var_name] = var_value
            return safe_eval_with_checks(compiled, namespace)
        except Exception as e:
            error_msg = str(e)
            if error_msg.startswith("Ошибка вычисления:"):
                error_msg = error_msg.replace("Ошибка вычисления:", "").strip()
            raise ValueError(error_msg)
    return func