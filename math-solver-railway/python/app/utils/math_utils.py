import sympy
from sympy import (
    Symbol, symbols, sympify, oo, zoo, nan, S,
    Rational, Float, Integer, Number,
    pi, E, I,
)
from typing import Any, Optional
import re
import math


def safe_sympify(expr_str: str) -> Optional[sympy.Basic]:
    """Safely parse a string into a SymPy expression."""
    try:
        transformations = sympy.parsing.sympy_parser.standard_transformations + (
            sympy.parsing.sympy_parser.implicit_multiplication_application,
            sympy.parsing.sympy_parser.convert_xor,
        )
        return sympy.parsing.sympy_parser.parse_expr(
            expr_str, transformations=transformations
        )
    except Exception:
        try:
            return sympify(expr_str)
        except Exception:
            return None


def get_free_symbols(expr) -> list[Symbol]:
    """Get free symbols from a SymPy expression, sorted by name."""
    if isinstance(expr, str):
        expr = safe_sympify(expr)
    if expr is None:
        return []
    try:
        return sorted(expr.free_symbols, key=lambda s: str(s))
    except Exception:
        return []


def is_numeric(expr) -> bool:
    """Check if a SymPy expression is purely numeric (no free symbols)."""
    if isinstance(expr, str):
        expr = safe_sympify(expr)
    if expr is None:
        return False
    try:
        return len(expr.free_symbols) == 0
    except Exception:
        return False


def safe_float(expr) -> Optional[float]:
    """Safely convert a SymPy expression to float."""
    try:
        val = float(expr)
        if math.isfinite(val):
            return val
        return None
    except (TypeError, ValueError, OverflowError):
        return None


def safe_eval_at(expr, var, value) -> Optional[Any]:
    """Safely evaluate expr at var=value."""
    try:
        result = expr.subs(var, value)
        if result.is_finite is not False and result != zoo and result != nan:
            return result
        return None
    except Exception:
        return None


def round_decimal(value: float, precision: int = 10) -> str:
    """Round a float and return string, removing trailing zeros."""
    if abs(value) < 1e-15:
        return "0"
    formatted = f"{value:.{precision}f}"
    if "." in formatted:
        formatted = formatted.rstrip("0").rstrip(".")
    return formatted


def is_polynomial(expr, var=None) -> bool:
    """Check if expression is a polynomial."""
    try:
        if isinstance(expr, str):
            expr = safe_sympify(expr)
        if expr is None:
            return False
        if var is None:
            syms = get_free_symbols(expr)
            if not syms:
                return True
            var = syms[0]
        poly = sympy.Poly(expr, var)
        return True
    except Exception:
        return False


def degree_of(expr, var=None) -> Optional[int]:
    """Get the degree of a polynomial expression."""
    try:
        if isinstance(expr, str):
            expr = safe_sympify(expr)
        if expr is None:
            return None
        if var is None:
            syms = get_free_symbols(expr)
            if not syms:
                return 0
            var = syms[0]
        return sympy.degree(expr, var)
    except Exception:
        return None


def gcd_of_expressions(*exprs) -> Any:
    """Compute GCD of multiple expressions."""
    try:
        result = exprs[0]
        for e in exprs[1:]:
            result = sympy.gcd(result, e)
        return result
    except Exception:
        return S.One


def lcm_of_expressions(*exprs) -> Any:
    """Compute LCM of multiple expressions."""
    try:
        result = exprs[0]
        for e in exprs[1:]:
            result = sympy.lcm(result, e)
        return result
    except Exception:
        return None


def detect_expression_complexity(expr_str: str) -> str:
    """Rate expression complexity: simple, moderate, complex."""
    length = len(expr_str)
    nested_parens = max_nesting_depth(expr_str)
    has_trig = bool(re.search(r"\b(sin|cos|tan|sec|csc|cot)\b", expr_str))
    has_calculus = bool(re.search(r"\b(diff|integrate|limit|sum|product)\b", expr_str))
    has_matrix = bool(re.search(r"\b(Matrix|det|eigenval|inverse)\b", expr_str))

    score = 0
    score += min(length // 20, 5)
    score += nested_parens
    if has_trig:
        score += 2
    if has_calculus:
        score += 3
    if has_matrix:
        score += 3

    if score <= 2:
        return "simple"
    elif score <= 6:
        return "moderate"
    return "complex"


def max_nesting_depth(expr_str: str) -> int:
    """Calculate maximum nesting depth of parentheses."""
    max_depth = 0
    current = 0
    for c in expr_str:
        if c in "([{":
            current += 1
            max_depth = max(max_depth, current)
        elif c in ")]}":
            current -= 1
    return max_depth
