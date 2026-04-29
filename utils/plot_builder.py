import plotly.graph_objs as go
import numpy as np
from .expression_parser import validate_expression_detailed
from .calculation_engine import create_function_from_string

def create_empty_figure(title=""):
    fig = go.Figure()
    fig.update_layout(
        title=title, xaxis_title='x', yaxis_title='y',
        template='plotly_white', height=400,
        xaxis=dict(range=[0, 1]), yaxis=dict(range=[-1, 1]),
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family="Roboto, sans-serif", size=12, color="#2C3E50")
    )
    return fig

def build_sections_plot(kernel_expr, x_min, x_max):
    if not kernel_expr or not kernel_expr.strip():
        return create_empty_figure("")
    
    kernel_valid, _ = validate_expression_detailed(kernel_expr, ['x', 't'])
    if not kernel_valid:
        return create_empty_figure("")
    
    x_min = x_min if x_min is not None else 0
    x_max = x_max if x_max is not None else x_min + 1
    
    try:
        K_func = create_function_from_string(kernel_expr, ['x', 't'])
    except Exception:
        return create_empty_figure("")
    
    t_values = np.linspace(x_min, x_max, 5)
    x_vals = np.linspace(x_min, x_max, 500)
    colors = ['#2C3E50', '#34495E', '#E74C3C', '#C0392B', '#7F8C8D']
    
    fig = go.Figure()
    for i, t_val in enumerate(t_values):
        try:
            K_vals = [K_func(xi, t_val) for xi in x_vals]
            fig.add_trace(go.Scatter(
                x=x_vals, y=K_vals, mode='lines',
                name=f't = {t_val:.3f}',
                line=dict(color=colors[i % len(colors)], width=2)
            ))
        except Exception:
            pass
    
    fig.update_layout(
        title=f'x ∈ [{x_min:.2f}, {x_max:.2f}]',
        xaxis_title='x', yaxis_title='K(x,t)',
        template='plotly_white', height=400,
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family="Roboto, sans-serif", size=12, color="#2C3E50"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def build_surface_plot(kernel_expr, x_min, x_max, t_min, t_max):
    if not kernel_expr or not kernel_expr.strip():
        return create_empty_figure("")
    
    kernel_valid, _ = validate_expression_detailed(kernel_expr, ['x', 't'])
    if not kernel_valid:
        return create_empty_figure("")
    
    x_min = x_min if x_min is not None else 0
    x_max = x_max if x_max is not None else x_min + 1
    t_min = t_min if t_min is not None else 0
    t_max = t_max if t_max is not None else t_min + 1
    
    try:
        K_func = create_function_from_string(kernel_expr, ['x', 't'])
    except Exception:
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
    
    fig = go.Figure(data=[go.Surface(z=K_vals, x=X, y=T, colorscale='Blues')])
    fig.update_layout(
        title=f'x ∈ [{x_min:.2f}, {x_max:.2f}], t ∈ [{t_min:.2f}, {t_max:.2f}]',
        scene=dict(xaxis_title='x', yaxis_title='t', zaxis_title='K(x,t)'),
        height=450, plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family="Roboto, sans-serif", size=12, color="#2C3E50")
    )
    return fig

def build_graphs(x, phi_numerical, phi_reference, derivative_numerical, derivative_exact, error_text):
    """Строит графики решения и производной"""
    fig_solution = go.Figure()
    fig_solution.add_trace(go.Scatter(x=x, y=phi_reference, mode='lines', name='Эталон',
                                      line=dict(color='#E74C3C', width=2)))
    fig_solution.add_trace(go.Scatter(x=x, y=phi_numerical, mode='lines', name='Численное',
                                      line=dict(color='#2C3E50', dash='dash', width=1.5)))
    fig_solution.update_layout(
        xaxis_title='x', yaxis_title='φ(x)', hovermode='x unified',
        template='plotly_white', height=400, showlegend=True,
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family="Roboto, sans-serif", size=12, color="#2C3E50")
    )
    
    fig_derivative = go.Figure()
    fig_derivative.add_trace(go.Scatter(x=x, y=derivative_numerical, mode='lines', name="φ'(x) (численная)",
                                        line=dict(color='#34495E', width=2)))
    fig_derivative.add_trace(go.Scatter(x=x, y=derivative_exact, mode='lines', 
                                        name='f(x) + I(x) (точная)',
                                        line=dict(color='#E74C3C', dash='dash', width=1.5)))
    fig_derivative.update_layout(
        xaxis_title='x', yaxis_title="φ'(x)", hovermode='x unified',
        template='plotly_white', height=400, showlegend=True,
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family="Roboto, sans-serif", size=12, color="#2C3E50")
    )
    
    return fig_solution, fig_derivative