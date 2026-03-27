import re
from typing import Optional
from app.services.normalize_service import NormalizeService


class ParserService:
    """Parses math expressions and detects problem types."""

    def __init__(self):
        self.normalizer = NormalizeService()

    def parse(self, expression: str) -> dict:
        """Parse an expression and return structured info."""
        normalized = self.normalizer.normalize(expression)
        problem_type = self.detect_type(normalized)
        variables = self._extract_variables(normalized)
        return {
            "original": expression,
            "normalized": normalized,
            "problem_type": problem_type,
            "variables": variables,
            "is_equation": self._is_equation(normalized),
            "is_system": self._is_system(normalized),
            "is_matrix": self._is_matrix(normalized),
        }

    def detect_type(self, expression: str) -> str:
        """Detect the type of math problem."""
        expr = expression.lower().strip()

        # Check for explicit commands
        if re.search(r"\b(derivative|differentiate|d/d[a-z])\b", expr):
            return "calculus"
        if re.search(r"\b(integrate|integral|antiderivative)\b", expr):
            return "calculus"
        if re.search(r"\b(limit|lim)\b", expr):
            return "calculus"
        if re.search(r"\b(taylor|maclaurin|series)\b", expr):
            return "calculus"
        if re.search(r"\b(sum|product)\b", expr) and re.search(r"\b(n|k|i)\s*=", expr):
            return "calculus"

        # Differential equations
        if re.search(r"\b(ode|dsolve)\b", expr) or re.search(r"y['\u2032]+|dy/dx|d\^?\d*y/dx\^?\d*", expr):
            return "differential_equation"

        # Matrix / linear algebra
        if re.search(r"\b(matrix|det|determinant|eigenval|eigenvec|inverse|transpose|rank|nullspace|rref)\b", expr):
            return "linear_algebra"
        if re.search(r"\[\s*\[", expr):
            return "linear_algebra"

        # Statistics / probability
        if re.search(r"\b(mean|median|mode|std|stdev|variance|correlation|regression|probability|binomial|poisson|normal|chi.?square|t.?test|z.?score|percentile)\b", expr):
            return "stats"

        # Optimization
        if re.search(r"\b(minimize|maximize|optimize|extrema|critical.?point|min|max)\b", expr):
            return "optimization"

        # System of equations
        if self._is_system(expression):
            return "system"

        # Single equation
        if self._is_equation(expression):
            # Check if it's a trig equation
            if re.search(r"\b(sin|cos|tan|cot|sec|csc)\b", expr):
                return "equation"
            return "equation"

        # Polynomial operations
        if re.search(r"\b(factor|expand|simplify|partial.?fraction)\b", expr):
            return "algebra"

        # Check for trig
        if re.search(r"\b(sin|cos|tan|cot|sec|csc|asin|acos|atan)\b", expr):
            return "algebra"

        # Check for pure arithmetic
        if re.match(r"^[\d\s+\-*/^().,%!]+$", expr):
            return "arithmetic"

        # Check for algebraic expression with variables
        if re.search(r"[a-zA-Z]", expr):
            return "algebra"

        return "arithmetic"

    def _is_equation(self, expr: str) -> bool:
        """Check if expression is an equation."""
        cleaned = expr.replace("<=", "LE").replace(">=", "GE").replace("!=", "NE").replace("==", "EQ")
        return "=" in cleaned

    def _is_system(self, expr: str) -> bool:
        """Check if expression represents a system of equations."""
        separators = [";", "\n", "\\n", " and "]
        for sep in separators:
            parts = expr.split(sep)
            eq_count = sum(1 for p in parts if self._is_equation(p.strip()) and p.strip())
            if eq_count >= 2:
                return True
        # Also check for comma-separated equations with variables
        if expr.count("=") >= 2 and "," in expr:
            parts = expr.split(",")
            eq_count = sum(1 for p in parts if self._is_equation(p.strip()) and p.strip())
            if eq_count >= 2:
                return True
        return False

    def _is_matrix(self, expr: str) -> bool:
        """Check if expression contains a matrix."""
        return bool(re.search(r"\[\s*\[", expr)) or "Matrix" in expr

    def _extract_variables(self, expr: str) -> list[str]:
        """Extract variable names from expression."""
        known_funcs = {
            "sin", "cos", "tan", "cot", "sec", "csc",
            "asin", "acos", "atan", "atan2",
            "sinh", "cosh", "tanh",
            "log", "ln", "exp", "sqrt", "abs", "sign",
            "pi", "inf", "oo", "nan",
            "integrate", "diff", "limit", "sum", "product",
            "solve", "factor", "expand", "simplify",
            "factorial", "gamma", "beta", "zeta",
            "det", "trace", "transpose", "inverse", "rref",
            "matrix", "eigenval", "eigenvec", "rank", "nullspace",
            "mean", "median", "mode", "std", "var", "stdev",
            "minimize", "maximize", "optimize",
            "derivative", "differentiate", "antiderivative",
            "taylor", "maclaurin", "series",
            "partial", "fraction", "fractions",
            "binomial", "poisson", "normal",
            "dsolve", "ode",
            "true", "false", "and", "or", "not",
        }
        pattern = r"\b([a-zA-Z_]\w*)\b"
        matches = re.findall(pattern, expr)
        variables = []
        seen = set()
        for m in matches:
            lower = m.lower()
            if lower not in known_funcs and m not in seen and len(m) <= 5:
                variables.append(m)
                seen.add(m)
        return variables

    def split_system(self, expr: str) -> list[str]:
        """Split a system of equations into individual equations."""
        for sep in [";", "\n", "\\n"]:
            parts = [p.strip() for p in expr.split(sep) if p.strip()]
            if len(parts) >= 2 and all(self._is_equation(p) for p in parts):
                return parts
        if " and " in expr.lower():
            parts = [p.strip() for p in re.split(r"\band\b", expr, flags=re.IGNORECASE) if p.strip()]
            if len(parts) >= 2:
                return parts
        if expr.count("=") >= 2 and "," in expr:
            parts = [p.strip() for p in expr.split(",") if p.strip()]
            if all(self._is_equation(p) for p in parts):
                return parts
        return [expr]
