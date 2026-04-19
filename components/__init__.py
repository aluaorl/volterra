from .input_panel import create_input_panel, KERNEL_EXAMPLES, RHS_EXAMPLES
from .result_panels import create_result_panels
from .history_panel import create_history_panel  # Добавьте эту строку
from .callbacks import register_callbacks

__all__ = ['create_input_panel', 'create_result_panels', 'create_history_panel', 
           'register_callbacks', 'KERNEL_EXAMPLES', 'RHS_EXAMPLES']