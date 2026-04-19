import re
import numpy as np

# Словарь синонимов функций (в нижнем регистре)
FUNCTION_SYNONYMS = {
    # Обратные тригонометрические
    'arcsin': 'np.arcsin',
    'arccos': 'np.arccos',
    'arctan': 'np.arctan',
    'arctg': 'np.arctan',
    'arcctg': 'np.arctan',
    'arccot': 'np.arctan',
    
    # Тригонометрические
    'sin': 'np.sin',
    'cos': 'np.cos',
    'tan': 'np.tan',
    'tg': 'np.tan',
    'cot': '1/np.tan',
    'ctg': '1/np.tan',
    'sec': '1/np.cos',
    'csc': '1/np.sin',
    'cosec': '1/np.sin',
    
    # Гиперболические
    'sinh': 'np.sinh',
    'cosh': 'np.cosh',
    'tanh': 'np.tanh',
    'sh': 'np.sinh',
    'ch': 'np.cosh',
    'th': 'np.tanh',
    'coth': '1/np.tanh',
    'cth': '1/np.tanh',
    
    # Логарифмы
    'ln': 'np.log',
    'lg': 'np.log10',
    'log2': 'np.log2',
    'log': 'np.log',
    
    # Экспонента и корни
    'exp': 'np.exp',
    'sqrt': 'np.sqrt',
    'abs': 'np.abs',
}

# Константы (в нижнем регистре)
CONSTANTS = {
    'pi': 'np.pi',
    'π': 'np.pi',
    'e': 'np.e',
}

# Греческие буквы для отображения
GREEK_LETTERS = {
    'alpha': 'α',
    'beta': 'β',
    'gamma': 'γ',
    'delta': 'δ',
    'epsilon': 'ε',
    'zeta': 'ζ',
    'eta': 'η',
    'theta': 'θ',
    'iota': 'ι',
    'kappa': 'κ',
    'lambda': 'λ',
    'mu': 'μ',
    'nu': 'ν',
    'xi': 'ξ',
    'omicron': 'ο',
    'pi': 'π',
    'rho': 'ρ',
    'sigma': 'σ',
    'tau': 'τ',
    'upsilon': 'υ',
    'phi': 'φ',
    'chi': 'χ',
    'psi': 'ψ',
    'omega': 'ω',
}

def normalize_case(expr):
    """Приводит выражение к нижнему регистру, но сохраняет переменные x и t в исходном виде"""
    expr = re.sub(r'\bx\b', '___VAR_X___', expr, flags=re.IGNORECASE)
    expr = re.sub(r'\bt\b', '___VAR_T___', expr, flags=re.IGNORECASE)
    expr = expr.lower()
    expr = expr.replace('___var_x___', 'x')
    expr = expr.replace('___var_t___', 't')
    return expr

def is_already_parsed(expr):
    """Проверяет, не было ли выражение уже в формате np.*"""
    if 'np.' not in expr:
        return False
    compact = re.sub(r'\s+', '', expr)
    compact_lower = compact.lower()
    for func in FUNCTION_SYNONYMS.keys():
        if re.search(r'(?<!np\.)\b' + re.escape(func) + r'\b', compact_lower):
            return False
    return True

def preprocess_expression(expr):
    """Предобработка выражения: удаление пробелов, добавление * где нужно"""
    expr = re.sub(r'\s+', '', expr)
    expr = re.sub(r'(\d+\.\d+)', r'__FLOAT_\1__', expr)
    expr = re.sub(r'(\d+)([a-zA-Zα-ω])', r'\1*\2', expr)
    expr = re.sub(r'([a-zA-Zα-ω])(\d+)', r'\1*\2', expr)
    expr = re.sub(r'(\d+)\(', r'\1*(', expr)
    expr = re.sub(r'([a-zA-Zα-ω])\(', lambda m: m.group(1) + '(', expr)
    expr = re.sub(r'\)\(', r')*(', expr)
    expr = re.sub(r'__FLOAT_(\d+\.\d+)__', r'\1', expr)
    return expr

def safe_eval_with_checks(expr, namespace, test_value=0.5):
    """Безопасное вычисление выражения с проверкой на математические ошибки"""
    try:
        result = eval(expr, {"__builtins__": {}}, namespace)
        
        if isinstance(result, complex):
            raise ValueError("Выражение дает комплексное число (корень из отрицательного числа или логарифм отрицательного числа)")
        
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
            # Убираем лишние детали из сообщения
            clean_msg = str(e).replace("Ошибка вычисления:", "").strip()
            raise ValueError(clean_msg)
        
def validate_expression_detailed(expr_str, variables=['x', 't']):
    """Подробная валидация выражения с возвратом понятного сообщения"""
    if not expr_str or expr_str.strip() == '':
        return False, "Выражение не может быть пустым"
    
    try:
        expr = normalize_case(expr_str)
        
        if is_already_parsed(expr):
            test_namespace = {'np': np}
            for var in variables:
                test_namespace[var] = 0.5
            for test_val in [0.1, 0.3, 0.5, 0.7, 0.9]:
                for var in variables:
                    test_namespace[var] = test_val
                safe_eval_with_checks(expr, test_namespace, test_val)
            return True, "Выражение корректно"
        
        expr = preprocess_expression(expr)
        
        # Обработка e^
        expr = re.sub(r'e\^\(([^)]+)\)', r'np.exp(\1)', expr)
        expr = re.sub(r'e\^([a-zA-Z0-9α-ω]+)', r'np.exp(\1)', expr)
        expr = re.sub(r'e\^\(-([^)]+)\)', r'np.exp(-\1)', expr)
        
        # Замена функций
        for func_name, np_func in FUNCTION_SYNONYMS.items():
            pattern_with_paren = r'(?<!np\.)\b' + re.escape(func_name) + r'\s*\('
            expr = re.sub(pattern_with_paren, np_func + '(', expr)
        
        # Замена констант
        for const, replacement in CONSTANTS.items():
            expr = re.sub(r'\b' + re.escape(const) + r'\b', replacement, expr)
        
        # Обработка степени
        expr = re.sub(r'([a-zA-Z0-9α-ω\(\)]+)\^([a-zA-Z0-9α-ω\(\)]+)', r'(\1)**(\2)', expr)
        
        expr = re.sub(r'\s+', '', expr)
        
        if expr.count('(') != expr.count(')'):
            return False, "Несбалансированные скобки"
        
        # Проверка на валидность
        test_namespace = {'np': np}
        for var in variables:
            test_namespace[var] = 0.5
        
        compile(expr, '<string>', 'eval')
        
        # Тестируем в нескольких точках
        test_points = [0.1, 0.3, 0.5, 0.7, 0.9]
        for test_val in test_points:
            for var in variables:
                test_namespace[var] = test_val
            safe_eval_with_checks(expr, test_namespace, test_val)
        
        return True, "Выражение корректно"
        
    except Exception as e:
        return False, str(e)

def parse_user_input(expr_str, variables=['x', 't']):
    """Основная функция парсинга пользовательского ввода"""
    if not expr_str or expr_str.strip() == '':
        raise ValueError("Выражение не может быть пустым")
    
    original_expr = expr_str
    expr = normalize_case(expr_str)
    
    if is_already_parsed(expr):
        test_namespace = {'np': np}
        for var in variables:
            test_namespace[var] = 0.5
        test_points = [0.1, 0.3, 0.5, 0.7, 0.9]
        for test_val in test_points:
            for var in variables:
                test_namespace[var] = test_val
            safe_eval_with_checks(expr, test_namespace, test_val)
        return expr
    
    try:
        expr = preprocess_expression(expr)
        
        expr = re.sub(r'e\^\(([^)]+)\)', r'np.exp(\1)', expr)
        expr = re.sub(r'e\^([a-zA-Z0-9α-ω]+)', r'np.exp(\1)', expr)
        expr = re.sub(r'e\^\(-([^)]+)\)', r'np.exp(-\1)', expr)
        
        for func_name, np_func in FUNCTION_SYNONYMS.items():
            pattern_with_paren = r'(?<!np\.)\b' + re.escape(func_name) + r'\s*\('
            expr = re.sub(pattern_with_paren, np_func + '(', expr)
        
        for const, replacement in CONSTANTS.items():
            expr = re.sub(r'\b' + re.escape(const) + r'\b', replacement, expr)
        
        expr = re.sub(r'([a-zA-Z0-9α-ω\(\)]+)\^([a-zA-Z0-9α-ω\(\)]+)', r'(\1)**(\2)', expr)
        expr = re.sub(r'np\.arctan\(1/([^)]+)\)', r'np.arctan(1/\1)', expr)
        expr = re.sub(r'1/np\.tan\(', r'np.tan(', expr)
        expr = re.sub(r'\s+', '', expr)
        
        if expr.count('(') != expr.count(')'):
            raise ValueError("Несбалансированные скобки")
        
        test_namespace = {'np': np}
        for var in variables:
            test_namespace[var] = 0.5
        
        compile(expr, '<string>', 'eval')
        
        test_points = [0.1, 0.3, 0.5, 0.7, 0.9]
        for test_val in test_points:
            for var in variables:
                test_namespace[var] = test_val
            safe_eval_with_checks(expr, test_namespace, test_val)
        
        return expr
        
    except Exception as e:
        raise ValueError(str(e))

def format_for_display(expr, is_kernel=True):
    """Форматирование выражения для красивого отображения"""
    result = expr.replace('np.', '')
    result = result.replace('**', '^')
    result = re.sub(r'exp\(([^)]+)\)', r'e^{\1}', result)
    
    for eng, gr in GREEK_LETTERS.items():
        result = result.replace(eng, gr)
    
    result = result.replace('1/tan', 'cot')
    result = result.replace('arctan(1/', 'arcctg(')
    
    if is_kernel:
        return f"K(x,t) = {result}"
    else:
        return f"f(x) = {result}"

def validate_expression(expr_str, variables=['x', 't']):
    """Валидация выражения"""
    try:
        parse_user_input(expr_str, variables)
        return True, "Выражение корректно"
    except ValueError as e:
        return False, str(e)