import re
import numpy as np

FUNCTION_SYNONYMS = {
    # Обратные тригонометрические (арксинусы)
    'arcsin': 'np.arcsin',
    'asin': 'np.arcsin',
    'arsin': 'np.arcsin',
    
    'arccos': 'np.arccos',
    'acos': 'np.arccos',
    'arcos': 'np.arccos',
    
    'arctan': 'np.arctan',
    'atan': 'np.arctan',
    'arctg': 'np.arctan',
    'atg': 'np.arctan',
    
    'arccot': 'arccot',
    'arcctg': 'arccot',
    'acot': 'arccot',
    'actg': 'arccot',
    
    'arcsec': 'arcsec',
    'asec': 'arcsec',
    
    'arccsc': 'arccsc',
    'acsc': 'arccsc',
    'arccosec': 'arccsc',
    
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
    'sh': 'np.sinh',
    'cosh': 'np.cosh',
    'ch': 'np.cosh',
    'tanh': 'np.tanh',
    'th': 'np.tanh',
    'coth': '1/np.tanh',
    'cth': '1/np.tanh',
    'sech': '1/np.cosh',
    'sch': '1/np.cosh',
    'csch': '1/np.sinh',
    'cosech': '1/np.sinh',
    
    # Обратные гиперболические
    'arsinh': 'np.arcsinh',
    'asinh': 'np.arcsinh',
    'arsh': 'np.arcsinh',
    'arcsinh': 'np.arcsinh',
    
    'arcosh': 'np.arccosh',
    'acosh': 'np.arccosh',
    'arch': 'np.arccosh',
    'arccosh': 'np.arccosh',
    
    'artanh': 'np.arctanh',
    'atanh': 'np.arctanh',
    'arth': 'np.arctanh',
    'arctanh': 'np.arctanh',
    
    'arcoth': 'arcoth',
    'acoth': 'arcoth',
    'arcth': 'arcoth',
    
    'arsech': 'arsech',
    'asech': 'arsech',
    'arsch': 'arsech',
    
    'arcsch': 'arcsch',
    'acsch': 'arcsch',
    'arcosech': 'arcsch',
    
    # Логарифмы
    'ln': 'np.log',
    'lg': 'np.log10',
    'log2': 'np.log2',
    'log10': 'np.log10',
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
    expr = re.sub(r'\bx\b', '___VAR_X___', expr, flags=re.IGNORECASE)
    expr = re.sub(r'\bt\b', '___VAR_T___', expr, flags=re.IGNORECASE)
    expr = expr.lower()
    expr = expr.replace('___var_x___', 'x')
    expr = expr.replace('___var_t___', 't')
    return expr

def is_already_parsed(expr):
    if 'np.' not in expr:
        return False
    compact = re.sub(r'\s+', '', expr)
    compact_lower = compact.lower()
    for func in FUNCTION_SYNONYMS.keys():
        if re.search(r'(?<!np\.)\b' + re.escape(func) + r'\b', compact_lower):
            return False
    return True

def preprocess_expression(expr):
    expr = re.sub(r'\s+', '', expr)
    expr = re.sub(r'(\d+\.\d+)', r'__FLOAT_\1__', expr)
    expr = re.sub(r'(\d+)([a-zA-Zα-ω])', r'\1*\2', expr)
    expr = re.sub(r'([a-zA-Zα-ω])(\d+)', r'\1*\2', expr)
    expr = re.sub(r'(\d+)\(', r'\1*(', expr)
    expr = re.sub(r'([a-zA-Zα-ω])\(', lambda m: m.group(1) + '(', expr)
    expr = re.sub(r'\)\(', r')*(', expr)
    expr = re.sub(r'__FLOAT_(\d+\.\d+)__', r'\1', expr)
    return expr

def process_power_after_function(expr):
    pattern = r'([a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\))\s*\^\s*([0-9]+(?:\.[0-9]+)?)'
    
    def replace_power(match):
        func_call = match.group(1)
        power = match.group(2)
        return f'({func_call})**{power}'
    
    expr = re.sub(pattern, replace_power, expr)
    
    pattern2 = r'\(([^)]+)\)\s*\^\s*([0-9]+(?:\.[0-9]+)?)'
    
    def replace_power2(match):
        inner = match.group(1)
        power = match.group(2)
        return f'({inner})**{power}'
    
    expr = re.sub(pattern2, replace_power2, expr)
    
    return expr

def process_sqrt(expr):
    pattern = r'sqrt\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)'
    
    def replace_sqrt(match):
        n = match.group(1)
        x = match.group(2)
        return f'(({x})**(1/({n})))'
    
    expr = re.sub(pattern, replace_sqrt, expr)
    
    expr = re.sub(r'sqrt\s*\(\s*([^)]+)\s*\)', r'np.sqrt(\1)', expr)
    
    return expr

def safe_eval_with_checks(expr, namespace, test_value=0.5):
    try:
        result = eval(expr, {"__builtins__": {}}, namespace)
        
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
        if "division by zero" in error_msg or "divide by zero" in error_msg:
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
                raise ValueError(f"Неизвестная функция '{func_name}'")
            raise ValueError("Неизвестная функция или переменная")
        else:
            raise ValueError("Некорректное математическое выражение")

def process_arccot(expr):
    expr = re.sub(r'arccot\(([^)]+)\)', r'np.arctan(1/\1)', expr)
    expr = re.sub(r'arcctg\(([^)]+)\)', r'np.arctan(1/\1)', expr)
    expr = re.sub(r'acot\(([^)]+)\)', r'np.arctan(1/\1)', expr)
    return expr

def process_arcsec(expr):
    expr = re.sub(r'arcsec\(([^)]+)\)', r'np.arccos(1/\1)', expr)
    expr = re.sub(r'asec\(([^)]+)\)', r'np.arccos(1/\1)', expr)
    return expr

def process_arccsc(expr):
    expr = re.sub(r'arccsc\(([^)]+)\)', r'np.arcsin(1/\1)', expr)
    expr = re.sub(r'acsc\(([^)]+)\)', r'np.arcsin(1/\1)', expr)
    expr = re.sub(r'arccosec\(([^)]+)\)', r'np.arcsin(1/\1)', expr)
    return expr

def process_arcoth(expr):
    expr = re.sub(r'arcoth\(([^)]+)\)', r'np.arctanh(1/\1)', expr)
    expr = re.sub(r'acoth\(([^)]+)\)', r'np.arctanh(1/\1)', expr)
    expr = re.sub(r'arcth\(([^)]+)\)', r'np.arctanh(1/\1)', expr)
    return expr

def process_arsech(expr):
    expr = re.sub(r'arsech\(([^)]+)\)', r'np.arccosh(1/\1)', expr)
    expr = re.sub(r'asech\(([^)]+)\)', r'np.arccosh(1/\1)', expr)
    expr = re.sub(r'arsch\(([^)]+)\)', r'np.arccosh(1/\1)', expr)
    return expr

def process_arcsch(expr):
    expr = re.sub(r'arcsch\(([^)]+)\)', r'np.arcsinh(1/\1)', expr)
    expr = re.sub(r'acsch\(([^)]+)\)', r'np.arcsinh(1/\1)', expr)
    expr = re.sub(r'arcosech\(([^)]+)\)', r'np.arcsinh(1/\1)', expr)
    return expr

def process_log_base(expr):
    pattern = r'log\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)'
    expr = re.sub(pattern, r'np.log(\2)/np.log(\1)', expr)
    return expr

def validate_expression_detailed(expr_str, variables=['x', 't']):
    if not expr_str or expr_str.strip() == '':
        return False, "Поле не может быть пустым"
    
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
            return True, ""
        
        expr = preprocess_expression(expr)
        expr = process_power_after_function(expr)
        expr = re.sub(r'e\^\(([^)]+)\)', r'np.exp(\1)', expr)
        expr = re.sub(r'e\^([a-zA-Z0-9α-ω]+)', r'np.exp(\1)', expr)
        expr = re.sub(r'e\^\(-([^)]+)\)', r'np.exp(-\1)', expr)
        expr = process_sqrt(expr)
        
        expr = process_arccot(expr)
        expr = process_arcsec(expr)
        expr = process_arccsc(expr)
        expr = process_arcoth(expr)
        expr = process_arsech(expr)
        expr = process_arcsch(expr)
        expr = process_log_base(expr)
        
        for func_name, np_func in FUNCTION_SYNONYMS.items():
            pattern = r'(?<!np\.)\b' + re.escape(func_name) + r'\s*\('
            
            if np_func in ['1/np.tan', '1/np.cosh', '1/np.sinh', '1/np.tanh']:
                expr = re.sub(pattern, np_func + '(', expr)
            else:
                expr = re.sub(pattern, np_func + '(', expr)
        
        for const, replacement in CONSTANTS.items():
            expr = re.sub(r'\b' + re.escape(const) + r'\b', replacement, expr)
        
        expr = re.sub(r'([a-zA-Z0-9α-ω\(\)]+)\^([a-zA-Z0-9α-ω\(\)]+)', r'(\1)**(\2)', expr)
        expr = re.sub(r'\s+', '', expr)
        
        if expr.count('(') != expr.count(')'):
            return False, "Несбалансированные скобки"
        
        try:
            compile(expr, '<string>', 'eval')
        except SyntaxError as e:
            error_msg = str(e)
            if "unexpected EOF" in error_msg:
                return False, "Незавершенное выражение"
            elif "invalid syntax" in error_msg:
                return False, "Некорректный синтаксис выражения"
            else:
                return False, "Ошибка в синтаксисе выражения"
        
        test_namespace = {'np': np}
        test_points = [0.1, 0.3, 0.5, 0.7, 0.9]
        
        for test_val in test_points:
            for var in variables:
                test_namespace[var] = test_val
            try:
                safe_eval_with_checks(expr, test_namespace, test_val)
            except ValueError as e:
                return False, str(e)
        
        return True, ""
        
    except SyntaxError as e:
        error_msg = str(e)
        if "unexpected EOF" in error_msg:
            return False, "Незавершенное выражение"
        elif "invalid syntax" in error_msg:
            return False, "Некорректный синтаксис выражения"
        else:
            return False, "Ошибка в синтаксисе выражения"
    except ValueError as e:
        return False, str(e)
    except Exception as e:
        error_msg = str(e).lower()
        if "division by zero" in error_msg:
            return False, "Обнаружено деление на ноль"
        elif "name" in error_msg and "is not defined" in error_msg:
            return False, "Неизвестная функция или переменная"
        else:
            return False, "Некорректное математическое выражение"

def parse_user_input(expr_str, variables=['x', 't']):
    if not expr_str or expr_str.strip() == '':
        raise ValueError("Выражение не может быть пустым")
    
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
        expr = process_power_after_function(expr)
        expr = re.sub(r'e\^\(([^)]+)\)', r'np.exp(\1)', expr)
        expr = re.sub(r'e\^([a-zA-Z0-9α-ω]+)', r'np.exp(\1)', expr)
        expr = re.sub(r'e\^\(-([^)]+)\)', r'np.exp(-\1)', expr)
        expr = process_sqrt(expr)
        
        expr = process_arccot(expr)
        expr = process_arcsec(expr)
        expr = process_arccsc(expr)
        expr = process_arcoth(expr)
        expr = process_arsech(expr)
        expr = process_arcsch(expr)
        expr = process_log_base(expr)
        
        for func_name, np_func in FUNCTION_SYNONYMS.items():
            pattern = r'(?<!np\.)\b' + re.escape(func_name) + r'\s*\('
            
            if np_func in ['1/np.tan', '1/np.cosh', '1/np.sinh', '1/np.tanh']:
                expr = re.sub(pattern, np_func + '(', expr)
            else:
                expr = re.sub(pattern, np_func + '(', expr)
        
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
    result = expr.replace('np.', '')
    result = result.replace('**', '^')
    result = re.sub(r'exp\(([^)]+)\)', r'e^{\1}', result)
    
    for eng, gr in GREEK_LETTERS.items():
        result = result.replace(eng, gr)
    
    result = result.replace('1/tan', 'cot')
    result = result.replace('arctan(1/', 'arcctg(')
    result = result.replace('arccos(1/', 'arcsec(')
    result = result.replace('arcsin(1/', 'arccsc(')
    result = result.replace('arctanh(1/', 'arcoth(')
    result = result.replace('arccosh(1/', 'arsech(')
    result = result.replace('arcsinh(1/', 'arcsch(')
    
    if is_kernel:
        return f"K(x,t) = {result}"
    else:
        return f"f(x) = {result}"

def validate_expression(expr_str, variables=['x', 't']):
    try:
        parse_user_input(expr_str, variables)
        return True, "Выражение корректно"
    except ValueError as e:
        return False, str(e)

# ============= ДОБАВЛЕННАЯ ФУНКЦИЯ =============
def format_equation_beautifully(kernel_expr, rhs_expr):
    from dash import html
    
    if not kernel_expr or not rhs_expr:
        return html.Div("Введите выражения для ядра K(x,t) и правой части f(x)", 
                       style={'color': '#7F8C8D', 'fontStyle': 'italic', 'textAlign': 'center'})
    
    return html.Div([
        html.Span("φ'(x) = ", style={'fontWeight': 'bold', 'color': '#2C3E50', 'fontSize': '1.2em'}),
        html.Span(rhs_expr, style={'color': '#E74C3C', 'fontFamily': 'monospace', 'fontSize': '1.2em'}),
        html.Span(" + ∫₀ˣ ", style={'fontWeight': 'bold', 'color': '#2C3E50', 'fontSize': '1.2em'}),
        html.Span(kernel_expr, style={'color': '#34495E', 'fontFamily': 'monospace', 'fontSize': '1.2em'}),
        html.Span(" · φ(t) dt", style={'fontWeight': 'bold', 'color': '#2C3E50', 'fontSize': '1.2em'}),
    ], style={'textAlign': 'center'})