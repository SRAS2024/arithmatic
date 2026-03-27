import sympy
from sympy import latex as sympy_latex
from typing import Any, Optional
import re


def expr_to_latex(expr: Any) -> str:
    """Convert a SymPy expression to LaTeX string."""
    try:
        if isinstance(expr, str):
            parsed = sympy.sympify(expr)
            return sympy_latex(parsed)
        return sympy_latex(expr)
    except Exception:
        return str(expr)


def matrix_to_latex(matrix) -> str:
    """Convert a SymPy Matrix to LaTeX."""
    try:
        return sympy_latex(matrix)
    except Exception:
        return str(matrix)


def equation_to_latex(lhs, rhs) -> str:
    """Generate LaTeX for an equation lhs = rhs."""
    try:
        l = sympy_latex(lhs) if not isinstance(lhs, str) else lhs
        r = sympy_latex(rhs) if not isinstance(rhs, str) else rhs
        return f"{l} = {r}"
    except Exception:
        return f"{lhs} = {rhs}"


def step_to_latex(description: str, expr: Any) -> str:
    """Format a solution step with description and LaTeX expression."""
    latex_str = expr_to_latex(expr) if not isinstance(expr, str) else expr
    return f"{description}: ${latex_str}$"


def wrap_latex_display(latex_str: str) -> str:
    """Wrap LaTeX in display math delimiters."""
    return f"$${latex_str}$$"


def wrap_latex_inline(latex_str: str) -> str:
    """Wrap LaTeX in inline math delimiters."""
    return f"${latex_str}$"


def text_to_latex_fraction(text: str) -> str:
    """Convert text fractions like '3/4' to LaTeX \\frac{3}{4}."""
    pattern = r"(\d+)\s*/\s*(\d+)"

    def replacer(m):
        return f"\\frac{{{m.group(1)}}}{{{m.group(2)}}}"

    return re.sub(pattern, replacer, text)


def format_solution_latex(steps: list[str], final_answer: Any) -> str:
    """Format a complete solution in LaTeX."""
    lines = []
    lines.append("\\begin{align*}")
    for i, step in enumerate(steps):
        if i < len(steps) - 1:
            lines.append(f"  & {step} \\\\")
        else:
            lines.append(f"  & {step}")
    lines.append("\\end{align*}")
    answer_latex = expr_to_latex(final_answer)
    lines.append(f"\\boxed{{{answer_latex}}}")
    return "\n".join(lines)


def clean_latex(latex_str: str) -> str:
    """Clean up LaTeX string for display."""
    result = latex_str.strip()
    result = result.replace("\\left(", "(").replace("\\right)", ")")
    return result


def derivative_to_latex(expr, var) -> str:
    """Format a derivative in LaTeX notation."""
    expr_latex = expr_to_latex(expr)
    var_str = str(var)
    return f"\\frac{{d}}{{d{var_str}}}\\left({expr_latex}\\right)"


def integral_to_latex(expr, var, lower=None, upper=None) -> str:
    """Format an integral in LaTeX notation."""
    expr_latex = expr_to_latex(expr)
    var_str = str(var)
    if lower is not None and upper is not None:
        lower_latex = expr_to_latex(lower)
        upper_latex = expr_to_latex(upper)
        return f"\\int_{{{lower_latex}}}^{{{upper_latex}}} {expr_latex} \\, d{var_str}"
    return f"\\int {expr_latex} \\, d{var_str}"


def limit_to_latex(expr, var, point, direction="") -> str:
    """Format a limit in LaTeX notation."""
    expr_latex = expr_to_latex(expr)
    var_str = str(var)
    point_latex = expr_to_latex(point)
    dir_str = ""
    if direction == "+":
        dir_str = "^{+}"
    elif direction == "-":
        dir_str = "^{-}"
    return f"\\lim_{{{var_str} \\to {point_latex}{dir_str}}} {expr_latex}"
