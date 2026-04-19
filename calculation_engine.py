import numpy as np
from scipy.interpolate import interp1d
from expression_parser import parse_user_input, safe_eval_with_checks

def safe_function_evaluation(func, *args):
    """Безопасное вычисление функции с проверкой ошибок"""
    try:
        result = func(*args)
        # Проверка на некорректные значения
        if isinstance(result, complex):
            raise ValueError("Выражение дает комплексное число (корень из отрицательного или логарифм отрицательного числа)")
        if isinstance(result, (int, float, np.number)):
            if np.isinf(result):
                raise ValueError("Выражение дает бесконечность (деление на ноль)")
            if np.isnan(result):
                raise ValueError("Выражение дает неопределенность (NaN) - возможно, корень из отрицательного числа или логарифм отрицательного числа")
        return result
    except Exception as e:
        error_msg = str(e).lower()
        if "division by zero" in error_msg or "divide by zero" in error_msg:
            raise ValueError("Обнаружено деление на ноль")
        elif "invalid value" in error_msg:
            raise ValueError("Некорректное математическое выражение (корень из отрицательного числа или логарифм отрицательного числа)")
        elif "math domain error" in error_msg:
            raise ValueError("Ошибка области определения (корень из отрицательного числа или логарифм отрицательного числа)")
        elif "name" in error_msg and "is not defined" in error_msg:
            import re
            match = re.search(r"name '([^']+)' is not defined", error_msg)
            if match:
                func_name = match.group(1)
                raise ValueError(f"Неизвестная функция или переменная '{func_name}'")
            raise ValueError(str(e))
        else:
            raise ValueError(str(e))

def solve_volterra_RK4_fast(x, h, K, f):
    """Максимально оптимизированное решение с кэшированием и проверками"""
    N = len(x) - 1
    phi = np.zeros(N + 1)
    phi[0] = 0.0
    
    # Предвычисление всех значений f(x) с проверками
    f_values = np.zeros(N + 1)
    for idx, xi in enumerate(x):
        try:
            f_values[idx] = safe_function_evaluation(f, xi)
        except Exception as e:
            # Упрощаем сообщение об ошибке
            raise ValueError(str(e))
    
    for i in range(N):
        xi = x[i]
        yi = phi[i]
        
        try:
            # Предвычисляем значения ядра для всех target_x
            target_x1 = xi
            target_x2 = xi + h/2
            target_x3 = xi + h/2
            target_x4 = xi + h
            
            # Массивы для хранения значений ядра
            K1 = np.zeros(i + 2)
            K2 = np.zeros(i + 2)
            K3 = np.zeros(i + 2)
            K4 = np.zeros(i + 2)
            
            # Вычисляем все значения ядра за один проход с проверками
            for j in range(i + 1):
                xj = x[j]
                K1[j] = safe_function_evaluation(K, target_x1, xj)
                K2[j] = safe_function_evaluation(K, target_x2, xj)
                K3[j] = safe_function_evaluation(K, target_x3, xj)
                K4[j] = safe_function_evaluation(K, target_x4, xj)
            
            K1[i+1] = safe_function_evaluation(K, target_x1, target_x1)
            K2[i+1] = safe_function_evaluation(K, target_x2, target_x2)
            K3[i+1] = safe_function_evaluation(K, target_x3, target_x3)
            K4[i+1] = safe_function_evaluation(K, target_x4, target_x4)
            
            # Вычисление интегральных сумм векторизованно
            if i > 0:
                # Для k1
                sum1 = np.sum((K1[:i] * phi[:i] + K1[1:i+1] * phi[1:i+1])) * (h/2)
                k1 = h * (f_values[i] + sum1)
                
                # Для k2
                sum2 = np.sum((K2[:i] * phi[:i] + K2[1:i+1] * phi[1:i+1])) * (h/2)
                h_last = h/2
                sum2 += (h_last/2) * (K2[i] * phi[i] + K2[i+1] * (yi + k1/2))
                k2 = h * (f_values[i] + sum2)
                
                # Для k3
                sum3 = np.sum((K3[:i] * phi[:i] + K3[1:i+1] * phi[1:i+1])) * (h/2)
                sum3 += (h_last/2) * (K3[i] * phi[i] + K3[i+1] * (yi + k2/2))
                k3 = h * (f_values[i] + sum3)
                
                # Для k4
                sum4 = np.sum((K4[:i] * phi[:i] + K4[1:i+1] * phi[1:i+1])) * (h/2)
                h_last = h
                sum4 += (h_last/2) * (K4[i] * phi[i] + K4[i+1] * (yi + k3))
                k4 = h * (f_values[i+1] + sum4)
            else:
                # Первая итерация (i=0)
                k1 = h * f_values[0]
                k2 = h * f_values[0]
                k3 = h * f_values[0]
                k4 = h * f_values[1]
            
            phi[i+1] = yi + (k1 + 2*k2 + 2*k3 + k4) / 6
            
        except Exception as e:
            # Упрощаем сообщение об ошибке - убираем технические детали
            error_msg = str(e)
            # Если сообщение уже короткое, оставляем как есть
            if not error_msg.startswith("Ошибка при вычислении функции:"):
                raise ValueError(error_msg)
            else:
                raise ValueError(error_msg)
    
    return phi

def get_reference_solution_fast(x, K, f):
    """Быстрое эталонное решение с проверками"""
    N_ref = 200
    h_ref = (x[-1] - x[0]) / N_ref
    x_ref = np.linspace(x[0], x[-1], N_ref + 1)
    
    # Вычисляем f_ref с проверками
    f_ref = np.zeros(N_ref + 1)
    for idx, xi in enumerate(x_ref):
        try:
            f_ref[idx] = safe_function_evaluation(f, xi)
        except Exception as e:
            raise ValueError(str(e))
    
    phi_ref = np.zeros(N_ref + 1)
    phi_ref[0] = 0
    
    for i in range(N_ref):
        xi = x_ref[i]
        yi = phi_ref[i]
        
        try:
            if i > 0:
                K_vals = np.array([safe_function_evaluation(K, xi, x_ref[j]) for j in range(i+1)])
                K_diag = safe_function_evaluation(K, xi, xi)
                sum1 = np.sum(K_vals[:i] * phi_ref[:i] + K_vals[1:i+1] * phi_ref[1:i+1]) * (h_ref/2)
                k1 = h_ref * (f_ref[i] + sum1)
                
                x_mid = xi + h_ref/2
                K_vals_mid = np.array([safe_function_evaluation(K, x_mid, x_ref[j]) for j in range(i+1)])
                K_diag_mid = safe_function_evaluation(K, x_mid, x_mid)
                sum2 = np.sum(K_vals_mid[:i] * phi_ref[:i] + K_vals_mid[1:i+1] * phi_ref[1:i+1]) * (h_ref/2)
                sum2 += (h_ref/2) * (K_vals_mid[i] * phi_ref[i] + K_diag_mid * (yi + k1/2))
                k2 = h_ref * (f_ref[i] + sum2)
                
                sum3 = np.sum(K_vals_mid[:i] * phi_ref[:i] + K_vals_mid[1:i+1] * phi_ref[1:i+1]) * (h_ref/2)
                sum3 += (h_ref/2) * (K_vals_mid[i] * phi_ref[i] + K_diag_mid * (yi + k2/2))
                k3 = h_ref * (f_ref[i] + sum3)
                
                x_next = xi + h_ref
                K_vals_next = np.array([safe_function_evaluation(K, x_next, x_ref[j]) for j in range(i+1)])
                K_diag_next = safe_function_evaluation(K, x_next, x_next)
                sum4 = np.sum(K_vals_next[:i] * phi_ref[:i] + K_vals_next[1:i+1] * phi_ref[1:i+1]) * (h_ref/2)
                sum4 += h_ref * (K_vals_next[i] * phi_ref[i] + K_diag_next * (yi + k3)) / 2
                k4 = h_ref * (f_ref[i+1] + sum4)
            else:
                k1 = h_ref * f_ref[0]
                k2 = h_ref * f_ref[0]
                k3 = h_ref * f_ref[0]
                k4 = h_ref * f_ref[1]
            
            phi_ref[i+1] = yi + (k1 + 2*k2 + 2*k3 + k4) / 6
            
        except Exception as e:
            # Упрощаем сообщение об ошибке
            error_msg = str(e)
            raise ValueError(error_msg)
    
    interp_func = interp1d(x_ref, phi_ref, kind='linear')
    return interp_func(x)

solve_volterra_RK4 = solve_volterra_RK4_fast
get_reference_solution = get_reference_solution_fast

def create_function_from_string(expr_str, var_names):
    """Создает функцию из строки выражения с поддержкой упрощенного ввода и проверками"""
    # Парсим пользовательский ввод
    parsed_expr = parse_user_input(expr_str, var_names)
    compiled = compile(parsed_expr, '<string>', 'eval')
    
    def func(*args):
        try:
            namespace = {'np': np}
            for var_name, var_value in zip(var_names, args):
                namespace[var_name] = var_value
            return safe_eval_with_checks(compiled, namespace)
        except Exception as e:
            # Убираем лишние детали из сообщения
            error_msg = str(e)
            # Если сообщение содержит "Ошибка вычисления:", убираем это
            if error_msg.startswith("Ошибка вычисления:"):
                error_msg = error_msg.replace("Ошибка вычисления:", "").strip()
            raise ValueError(error_msg)
    return func