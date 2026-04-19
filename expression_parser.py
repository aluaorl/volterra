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
    
    # Экспонента
    'exp': 'np.exp',
    
    # Корни и степени
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
    # Сохраняем переменные x и t (они могут быть в любом регистре, но мы их приведем к нижнему)
    # Для этого сначала заменяем x и t на временные маркеры
    expr = re.sub(r'\bx\b', '___VAR_X___', expr, flags=re.IGNORECASE)
    expr = re.sub(r'\bt\b', '___VAR_T___', expr, flags=re.IGNORECASE)
    
    # Приводим все к нижнему регистру
    expr = expr.lower()
    
    # Восстанавливаем переменные
    expr = expr.replace('___var_x___', 'x')
    expr = expr.replace('___var_t___', 't')
    
    return expr

def is_already_parsed(expr):
    """Проверяет, не было ли выражение уже в формате np.* (без «голых» имён функций)."""
    if 'np.' not in expr:
        return False
    compact = re.sub(r'\s+', '', expr)
    # Приводим к нижнему регистру для проверки
    compact_lower = compact.lower()
    for func in FUNCTION_SYNONYMS.keys():
        if re.search(r'(?<!np\.)\b' + re.escape(func) + r'\b', compact_lower):
            return False
    return True

def preprocess_expression(expr):
    """Предобработка выражения: удаление пробелов, добавление * где нужно"""
    # Удаляем пробелы
    expr = re.sub(r'\s+', '', expr)
    
    # Защищаем числа с плавающей точкой
    expr = re.sub(r'(\d+\.\d+)', r'__FLOAT_\1__', expr)
    
    # Добавляем * между числом и буквой (2x -> 2*x)
    expr = re.sub(r'(\d+)([a-zA-Zα-ω])', r'\1*\2', expr)
    
    # Добавляем * между буквой и числом (x2 -> x*2)
    expr = re.sub(r'([a-zA-Zα-ω])(\d+)', r'\1*\2', expr)
    
    # Добавляем * между числом и скобкой (2(x+1) -> 2*(x+1))
    expr = re.sub(r'(\d+)\(', r'\1*(', expr)
    
    # Добавляем * между буквой и скобкой, но не для функций
    expr = re.sub(r'([a-zA-Zα-ω])\(', lambda m: m.group(1) + '(', expr)
    
    # Добавляем * между скобкой и скобкой ()( -> )*(
    expr = re.sub(r'\)\(', r')*(', expr)
    
    # Восстанавливаем числа с плавающей точкой
    expr = re.sub(r'__FLOAT_(\d+\.\d+)__', r'\1', expr)
    
    return expr

def find_matching_paren(text, start_idx):
    """Находит индекс закрывающей скобки для открывающей на позиции start_idx"""
    count = 1
    i = start_idx + 1
    while i < len(text) and count > 0:
        if text[i] == '(':
            count += 1
        elif text[i] == ')':
            count -= 1
        i += 1
    return i - 1 if count == 0 else -1

def parse_user_input(expr_str, variables=['x', 't']):
    """Основная функция парсинга пользовательского ввода (регистронезависимая)"""
    if not expr_str or expr_str.strip() == '':
        raise ValueError("Выражение не может быть пустым")
    
    # Сохраняем оригинал для отображения, но работаем с normalized версией
    original_expr = expr_str
    
    # Приводим к нижнему регистру, но сохраняем переменные
    expr = normalize_case(expr_str)
    
    # Если выражение уже содержит np. и не содержит исходных имен функций, возвращаем как есть
    if is_already_parsed(expr):
        # Проверяем только валидность
        try:
            test_namespace = {'np': np}
            for var in variables:
                test_namespace[var] = 0.5
            eval(expr, {"__builtins__": {}}, test_namespace)
            return expr
        except Exception as e:
            raise ValueError(f"Ошибка в выражении: {str(e)}")
    
    try:
        # Предобработка
        expr = preprocess_expression(expr)
        
        # Специальная обработка e^
        expr = re.sub(r'e\^\(([^)]+)\)', r'np.exp(\1)', expr)
        expr = re.sub(r'e\^([a-zA-Z0-9α-ω]+)', r'np.exp(\1)', expr)
        expr = re.sub(r'e\^\(-([^)]+)\)', r'np.exp(-\1)', expr)
        
        # Замена функций на np.версии с добавлением скобок
        for func_name, np_func in FUNCTION_SYNONYMS.items():
            # Ищем функцию, за которой следует либо пробел, либо скобка, либо конец строки
            # Шаблон: func_name затем не буква (пробел, скобка, оператор и т.д.)
            
            # Сначала обрабатываем случай с явными скобками: func(xxx)
            # Не трогаем уже префиксованный numpy-ввод: np.exp(...) — иначе получится np.np.exp(...)
            pattern_with_paren = r'(?<!np\.)\b' + re.escape(func_name) + r'\s*\('
            expr = re.sub(pattern_with_paren, np_func + '(', expr)
            
            # Затем случай без скобок: func xxx
            # Находим функцию, после которой идет пробел или начало аргумента
            pattern_no_paren = r'(?<!np\.)\b' + re.escape(func_name) + r'\s+([^+\-*/)\s]+|[^+\-*/)\s]*\([^)]*\)[^+\-*/)\s]*)'
            
            def replace_no_paren(match):
                # Извлекаем аргумент
                arg_start = match.end(0)
                # Ищем конец аргумента
                arg_end = arg_start
                depth = 0
                while arg_end < len(expr):
                    char = expr[arg_end]
                    if char == '(':
                        depth += 1
                    elif char == ')':
                        if depth == 0:
                            break
                        depth -= 1
                    elif depth == 0 and char in '+-*/,':
                        # Проверяем, не унарный ли минус
                        if char == '-' and arg_end == arg_start:
                            arg_end += 1
                            continue
                        break
                    arg_end += 1
                arg = expr[arg_start:arg_end]
                return f"{np_func}({arg})"
            
            # Применяем замену для случаев без скобок
            # Но только если функция не была уже заменена
            if not expr.startswith('np.'):
                expr = re.sub(pattern_no_paren, replace_no_paren, expr)
        
        # Замена констант
        for const, replacement in CONSTANTS.items():
            expr = re.sub(r'\b' + re.escape(const) + r'\b', replacement, expr)
        
        # Обработка степени
        expr = re.sub(r'([a-zA-Z0-9α-ω\(\)]+)\^([a-zA-Z0-9α-ω\(\)]+)', r'(\1)**(\2)', expr)
        
        # Обработка arcctg
        expr = re.sub(r'np\.arctan\(1/([^)]+)\)', r'np.arctan(1/\1)', expr)
        
        # Обработка ctg/cot
        expr = re.sub(r'1/np\.tan\(', r'np.tan(', expr)
        
        # Удаляем лишние пробелы
        expr = re.sub(r'\s+', '', expr)
        
        # Проверка баланса скобок
        if expr.count('(') != expr.count(')'):
            raise ValueError("Несбалансированные скобки")
        
        # Проверка на валидность
        test_namespace = {'np': np}
        for var in variables:
            test_namespace[var] = 0.5
        
        try:
            compile(expr, '<string>', 'eval')
            # Тестовое вычисление
            test_result = eval(expr, {"__builtins__": {}}, test_namespace)
            if not isinstance(test_result, (int, float, np.number)):
                raise ValueError(f"Выражение должно возвращать число, получено {type(test_result)}")
        except SyntaxError as e:
            raise ValueError(f"Синтаксическая ошибка: {str(e)}")
        except Exception as e:
            raise ValueError(f"Ошибка в выражении: {str(e)}")
        
        return expr
        
    except Exception as e:
        raise ValueError(f"Не удалось разобрать выражение '{original_expr}': {str(e)}")

def format_for_display(expr, is_kernel=True):
    """Форматирование выражения для красивого отображения"""
    result = expr.replace('np.', '')
    result = result.replace('**', '^')
    
    # Обработка e^
    result = re.sub(r'exp\(([^)]+)\)', r'e^{\1}', result)
    
    # Греческие буквы
    for eng, gr in GREEK_LETTERS.items():
        result = result.replace(eng, gr)
    
    # Упрощаем отображение
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
        return True, "✓ Выражение корректно"
    except ValueError as e:
        return False, str(e)

# Тесты
if __name__ == "__main__":
    test_expressions = [
        "0.2 * sin(-(x - t))",
        "0.2 * COS(-(x - t))",  # UPPERCASE
        "0.2 * SiN(-(x - t))",   # Mixed case
        "SIN(x)",                 # UPPERCASE
        "Cos(2*x)",              # Capitalized
        "2*SIN(x)",              # UPPERCASE
        "SINx",                  # UPPERCASE without parentheses
        "e^(-x)",
        "E^X",                   # UPPERCASE
        "LN(x)",                 # UPPERCASE
        "x^2",
        "SIN x + COS t",         # UPPERCASE with spaces
    ]
    
    print("Тестирование парсера (регистронезависимый):")
    print("-" * 50)
    for expr in test_expressions:
        try:
            result = parse_user_input(expr)
            print(f"✓ '{expr}'")
            print(f"  -> '{result}'")
            
            # Проверяем, что результат можно вычислить
            namespace = {'np': np, 'x': 0.5, 't': 0.3}
            value = eval(result, {"__builtins__": {}}, namespace)
            print(f"  Значение: {value}")
            print()
        except Exception as e:
            print(f"✗ '{expr}' -> {e}")
            print()
    
    print("=" * 50)
    print("Тест уже обработанного выражения:")
    try:
        expr = "0.2*np.cos(-(x-t))"
        parsed = parse_user_input(expr)
        print(f"Исходное: {expr}")
        print(f"После парсинга: {parsed}")
        namespace = {'np': np, 'x': 0.5, 't': 0.3}
        value = eval(parsed, {"__builtins__": {}}, namespace)
        print(f"Значение: {value}")
    except Exception as e:
        print(f"Ошибка: {e}")
    
    print("=" * 50)
    print("Тест смешанного регистра:")
    try:
        expr = "0.2 * CoS(-(X - T))"
        parsed = parse_user_input(expr)
        print(f"Исходное: {expr}")
        print(f"После парсинга: {parsed}")
        namespace = {'np': np, 'x': 0.5, 't': 0.3}
        value = eval(parsed, {"__builtins__": {}}, namespace)
        expected = 0.2 * np.cos(-(0.5 - 0.3))
        print(f"Значение: {value}, ожидалось: {expected}")
        print(f"Совпадение: {abs(value - expected) < 1e-10}")
    except Exception as e:
        print(f"Ошибка: {e}")