import numpy as np
from scipy.optimize import curve_fit

def fit_analytical_formula(x_values, y_values):
    try:
        # 1. Константа
        const_val = np.mean(y_values)
        if np.max(np.abs(y_values - const_val)) < 1e-8:
            return f"{const_val:.6f}"
        
        best_formula = None
        best_error = float('inf')
        
        # ============= 2. СИНУС =============
        def sin_func(x, a, w, p, c): 
            return a * np.sin(w * x + p) + c
        try:
            p0 = [np.std(y_values), 2*np.pi, 0, np.mean(y_values)]
            popt, _ = curve_fit(sin_func, x_values, y_values, p0=p0, maxfev=10000)
            a, w, p, c = popt
            y_pred = sin_func(x_values, a, w, p, c)
            error = np.max(np.abs(y_values - y_pred))
            
            if error < 1e-6 and error < best_error:
                best_error = error
                if abs(c) < 1e-10:
                    best_formula = f"{a:.6f}*sin({w:.6f}*x + {p:.6f})"
                else:
                    best_formula = f"{a:.6f}*sin({w:.6f}*x + {p:.6f}) + {c:.6f}"
        except: pass
        
        # ============= 3. КОСИНУС =============
        def cos_func(x, a, w, p, c): 
            return a * np.cos(w * x + p) + c
        try:
            p0 = [np.std(y_values), 2*np.pi, 0, np.mean(y_values)]
            popt, _ = curve_fit(cos_func, x_values, y_values, p0=p0, maxfev=10000)
            a, w, p, c = popt
            y_pred = cos_func(x_values, a, w, p, c)
            error = np.max(np.abs(y_values - y_pred))
            
            if error < 1e-6 and error < best_error:
                best_error = error
                if abs(c) < 1e-10:
                    best_formula = f"{a:.6f}*cos({w:.6f}*x + {p:.6f})"
                else:
                    best_formula = f"{a:.6f}*cos({w:.6f}*x + {p:.6f}) + {c:.6f}"
        except: pass
        
        # ============= 4. СУММА СИНУСА И КОСИНУСА С ОДИНАКОВОЙ ЧАСТОТОЙ =============
        def sin_cos_same_freq(x, a, b, w, c):
            return a * np.sin(w * x) + b * np.cos(w * x) + c
        try:
            p0 = [np.std(y_values)/2, np.std(y_values)/2, 2*np.pi, np.mean(y_values)]
            popt, _ = curve_fit(sin_cos_same_freq, x_values, y_values, p0=p0, maxfev=10000)
            a, b, w, c = popt
            y_pred = sin_cos_same_freq(x_values, a, b, w, c)
            error = np.max(np.abs(y_values - y_pred))
            
            if error < 1e-6 and error < best_error:
                best_error = error
                terms = []
                if abs(a) > 1e-10:
                    terms.append(f"{a:.6f}*sin({w:.6f}*x)")
                if abs(b) > 1e-10:
                    sign = '+' if b > 0 and terms else ''
                    terms.append(f"{sign}{b:.6f}*cos({w:.6f}*x)")
                if abs(c) > 1e-10:
                    sign = '+' if c > 0 and terms else ''
                    terms.append(f"{sign}{c:.6f}")
                best_formula = ''.join(terms)
        except: pass
        
        # ============= 5. СУММА СИНУСА И КОСИНУСА С РАЗНЫМИ ЧАСТОТАМИ =============
        def sin_cos_diff_freq(x, a, w1, b, w2, p, c):
            return a * np.sin(w1 * x) + b * np.cos(w2 * x + p) + c
        try:
            p0 = [np.std(y_values)/2, 2*np.pi, np.std(y_values)/2, 2*np.pi, 0, np.mean(y_values)]
            popt, _ = curve_fit(sin_cos_diff_freq, x_values, y_values, p0=p0, maxfev=10000)
            a, w1, b, w2, p, c = popt
            y_pred = sin_cos_diff_freq(x_values, a, w1, b, w2, p, c)
            error = np.max(np.abs(y_values - y_pred))
            
            if error < 1e-6 and error < best_error:
                best_error = error
                terms = []
                if abs(a) > 1e-10:
                    terms.append(f"{a:.6f}*sin({w1:.6f}*x)")
                if abs(b) > 1e-10:
                    sign = '+' if b > 0 and terms else ''
                    terms.append(f"{sign}{b:.6f}*cos({w2:.6f}*x + {p:.6f})")
                if abs(c) > 1e-10:
                    sign = '+' if c > 0 and terms else ''
                    terms.append(f"{sign}{c:.6f}")
                best_formula = ''.join(terms)
        except: pass
        
        # ============= 6. СУММА ДВУХ СИНУСОВ =============
        def two_sines(x, a1, w1, p1, a2, w2, p2, c):
            return a1 * np.sin(w1 * x + p1) + a2 * np.sin(w2 * x + p2) + c
        try:
            p0 = [np.std(y_values)/2, 2*np.pi, 0, np.std(y_values)/2, 4*np.pi, 0, np.mean(y_values)]
            popt, _ = curve_fit(two_sines, x_values, y_values, p0=p0, maxfev=10000)
            a1, w1, p1, a2, w2, p2, c = popt
            y_pred = two_sines(x_values, a1, w1, p1, a2, w2, p2, c)
            error = np.max(np.abs(y_values - y_pred))
            
            if error < 1e-6 and error < best_error:
                best_error = error
                terms = []
                if abs(a1) > 1e-10:
                    terms.append(f"{a1:.6f}*sin({w1:.6f}*x + {p1:.6f})")
                if abs(a2) > 1e-10:
                    sign = '+' if a2 > 0 and terms else ''
                    terms.append(f"{sign}{a2:.6f}*sin({w2:.6f}*x + {p2:.6f})")
                if abs(c) > 1e-10:
                    sign = '+' if c > 0 and terms else ''
                    terms.append(f"{sign}{c:.6f}")
                best_formula = ''.join(terms)
        except: pass
        
        # ============= 7. СУММА ДВУХ КОСИНУСОВ =============
        def two_cosines(x, a1, w1, p1, a2, w2, p2, c):
            return a1 * np.cos(w1 * x + p1) + a2 * np.cos(w2 * x + p2) + c
        try:
            p0 = [np.std(y_values)/2, 2*np.pi, 0, np.std(y_values)/2, 4*np.pi, 0, np.mean(y_values)]
            popt, _ = curve_fit(two_cosines, x_values, y_values, p0=p0, maxfev=10000)
            a1, w1, p1, a2, w2, p2, c = popt
            y_pred = two_cosines(x_values, a1, w1, p1, a2, w2, p2, c)
            error = np.max(np.abs(y_values - y_pred))
            
            if error < 1e-6 and error < best_error:
                best_error = error
                terms = []
                if abs(a1) > 1e-10:
                    terms.append(f"{a1:.6f}*cos({w1:.6f}*x + {p1:.6f})")
                if abs(a2) > 1e-10:
                    sign = '+' if a2 > 0 and terms else ''
                    terms.append(f"{sign}{a2:.6f}*cos({w2:.6f}*x + {p2:.6f})")
                if abs(c) > 1e-10:
                    sign = '+' if c > 0 and terms else ''
                    terms.append(f"{sign}{c:.6f}")
                best_formula = ''.join(terms)
        except: pass
        
        # ============= 8. ЭКСПОНЕНЦИАЛЬНАЯ =============
        def exp_func(x, a, b, c): 
            return a * np.exp(b * x) + c
        try:
            p0 = [y_values[-1] - y_values[0], -1, y_values[0]]
            popt, _ = curve_fit(exp_func, x_values, y_values, p0=p0, maxfev=10000)
            a, b, c = popt
            y_pred = exp_func(x_values, a, b, c)
            error = np.max(np.abs(y_values - y_pred))
            
            if error < 1e-6 and error < best_error:
                best_error = error
                if abs(c) < 1e-10:
                    best_formula = f"{a:.6f}*exp({b:.6f}*x)"
                else:
                    best_formula = f"{a:.6f}*exp({b:.6f}*x) + {c:.6f}"
        except: pass
        
        # ============= 9. ЛИНЕЙНАЯ =============
        def linear(x, a, b): 
            return a * x + b
        try:
            popt, _ = curve_fit(linear, x_values, y_values, maxfev=10000)
            a, b = popt
            y_pred = linear(x_values, a, b)
            error = np.max(np.abs(y_values - y_pred))
            
            if error < 1e-6 and error < best_error:
                best_error = error
                if abs(b) < 1e-10:
                    best_formula = f"{a:.6f}*x"
                else:
                    sign = '+' if b > 0 else '-'
                    best_formula = f"{a:.6f}*x {sign} {abs(b):.6f}"
        except: pass
        
        # ============= 10. КВАДРАТИЧНАЯ =============
        def quadratic(x, a, b, c):
            return a * x**2 + b * x + c
        try:
            popt, _ = curve_fit(quadratic, x_values, y_values, maxfev=10000)
            a, b, c = popt
            y_pred = quadratic(x_values, a, b, c)
            error = np.max(np.abs(y_values - y_pred))
            
            if error < 1e-6 and error < best_error:
                best_error = error
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
                best_formula = ''.join(terms)
        except: pass
        
        # ============= 11. ПОЛИНОМ 3-Й СТЕПЕНИ (как запасной вариант) =============
        if best_error > 1e-5:
            try:
                coeffs = np.polyfit(x_values, y_values, 3)
                y_pred = np.polyval(coeffs, x_values)
                error = np.max(np.abs(y_values - y_pred))
                
                if error < best_error:
                    terms = []
                    for i, coef in enumerate(coeffs):
                        if abs(coef) > 1e-8:
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
                    if terms:
                        result = ''.join(terms).replace('+-', '-')
                        best_formula = result if not result.startswith('+') else result[1:]
            except: pass
        
        if best_formula:
            import re
            best_formula = best_formula.replace('exp', 'e')
            best_formula = re.sub(r'e\(([^)]+)\)', r'e^{\1}', best_formula)
            best_formula = best_formula.replace('+-', '-')
            best_formula = best_formula.replace('-+', '-')
            if best_formula.startswith('+'):
                best_formula = best_formula[1:]
            return best_formula
        
        return None
        
    except Exception as e:
        print(f"Ошибка в fit_analytical_formula: {e}")
        return None