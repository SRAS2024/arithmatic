import sympy
from sympy import (
    Symbol, symbols, sympify, simplify, factor, expand,
    diff, integrate, limit, series, summation, product,
    oo, pi, E, I, S, Rational,
    sin, cos, tan, log, exp, sqrt,
    Function, Derivative, Integral, Limit,
    trigsimp, cancel, apart,
)
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations,
    implicit_multiplication_application, convert_xor,
)
from typing import Any, Optional
from app.utils.latex_utils import (
    expr_to_latex, derivative_to_latex, integral_to_latex, limit_to_latex,
)


class CalculusService:
    """Calculus operations using SymPy."""

    TRANSFORMATIONS = standard_transformations + (
        implicit_multiplication_application,
        convert_xor,
    )

    def parse_expr(self, expr_str: str) -> Any:
        try:
            return parse_expr(expr_str, transformations=self.TRANSFORMATIONS)
        except Exception:
            return sympify(expr_str)

    def derivative(self, expr_str: str, variable: str = "x", order: int = 1) -> dict:
        """Compute derivatives."""
        steps = []
        try:
            expr = self.parse_expr(expr_str)
            var = Symbol(variable)

            steps.append(f"Find d{''.join(['']*order)}{'/' + 'd' + variable * order if order == 1 else '^' + str(order) + '/d' + variable + '^' + str(order)} of {expr_to_latex(expr)}")

            result = expr
            for i in range(order):
                prev = result
                result = diff(result, var)
                result_simplified = simplify(result)
                if i == 0 and order == 1:
                    steps.append(f"Apply differentiation rules")
                    # Show intermediate steps for common cases
                    expanded = expand(prev)
                    if expanded != prev:
                        steps.append(f"Expand: {expr_to_latex(expanded)}")
                    result = result_simplified
                    steps.append(f"Derivative: {expr_to_latex(result)}")
                elif order > 1:
                    steps.append(f"Derivative (order {i + 1}): {expr_to_latex(result_simplified)}")
                    result = result_simplified

            result = simplify(result)

            # Try further simplification
            trig_version = trigsimp(result)
            if len(str(trig_version)) < len(str(result)):
                result = trig_version
                steps.append(f"Trig simplified: {expr_to_latex(result)}")

            return {
                "answer": str(result),
                "steps": steps,
                "latex": expr_to_latex(result),
                "result": result,
            }
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": "", "result": None}

    def integral(self, expr_str: str, variable: str = "x",
                 lower: str = None, upper: str = None) -> dict:
        """Compute integrals (definite or indefinite)."""
        steps = []
        try:
            expr = self.parse_expr(expr_str)
            var = Symbol(variable)
            is_definite = lower is not None and upper is not None

            if is_definite:
                lower_val = self.parse_expr(lower)
                upper_val = self.parse_expr(upper)
                steps.append(f"Compute definite integral from {expr_to_latex(lower_val)} to {expr_to_latex(upper_val)} of {expr_to_latex(expr)} d{variable}")
            else:
                steps.append(f"Compute indefinite integral of {expr_to_latex(expr)} d{variable}")

            # Compute the antiderivative
            antideriv = integrate(expr, var)
            steps.append(f"Antiderivative: {expr_to_latex(antideriv)}")

            if is_definite:
                result = integrate(expr, (var, lower_val, upper_val))
                result = simplify(result)
                steps.append(f"Evaluate from {lower} to {upper}")
                steps.append(f"= [{expr_to_latex(antideriv)}] from {lower} to {upper}")

                upper_eval = antideriv.subs(var, upper_val)
                lower_eval = antideriv.subs(var, lower_val)
                steps.append(f"= ({expr_to_latex(upper_eval)}) - ({expr_to_latex(lower_eval)})")
                steps.append(f"= {expr_to_latex(result)}")

                decimal_val = None
                try:
                    decimal_val = float(result.evalf())
                except Exception:
                    pass

                return {
                    "answer": str(result),
                    "steps": steps,
                    "latex": expr_to_latex(result),
                    "result": result,
                    "decimal": decimal_val,
                }
            else:
                antideriv_simplified = simplify(antideriv)
                result_str = f"{antideriv_simplified} + C"
                steps.append(f"Add constant of integration: {expr_to_latex(antideriv_simplified)} + C")

                return {
                    "answer": result_str,
                    "steps": steps,
                    "latex": expr_to_latex(antideriv_simplified) + " + C",
                    "result": antideriv_simplified,
                    "decimal": None,
                }
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": "", "result": None, "decimal": None}

    def compute_limit(self, expr_str: str, variable: str = "x",
                      point: str = "0", direction: str = "") -> dict:
        """Compute limits."""
        steps = []
        try:
            expr = self.parse_expr(expr_str)
            var = Symbol(variable)
            point_val = self.parse_expr(point)

            dir_text = ""
            if direction == "+":
                dir_text = " from the right"
            elif direction == "-":
                dir_text = " from the left"

            steps.append(f"Compute limit as {variable} -> {point}{dir_text} of {expr_to_latex(expr)}")

            # Direct substitution first
            try:
                direct = expr.subs(var, point_val)
                if direct.is_finite and not direct.has(sympy.zoo) and not direct.has(sympy.nan):
                    steps.append(f"Direct substitution: {expr_to_latex(direct)}")
            except Exception:
                pass

            if direction == "+":
                result = limit(expr, var, point_val, "+")
            elif direction == "-":
                result = limit(expr, var, point_val, "-")
            else:
                result = limit(expr, var, point_val)

            steps.append(f"Limit = {expr_to_latex(result)}")

            # Check if limit exists from both sides
            if not direction:
                try:
                    left = limit(expr, var, point_val, "-")
                    right = limit(expr, var, point_val, "+")
                    if left != right:
                        steps.append(f"Left-hand limit: {expr_to_latex(left)}")
                        steps.append(f"Right-hand limit: {expr_to_latex(right)}")
                        steps.append("Note: left and right limits differ")
                except Exception:
                    pass

            return {
                "answer": str(result),
                "steps": steps,
                "latex": expr_to_latex(result),
                "result": result,
            }
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": "", "result": None}

    def taylor_series(self, expr_str: str, variable: str = "x",
                      point: str = "0", order: int = 6) -> dict:
        """Compute Taylor/Maclaurin series."""
        steps = []
        try:
            expr = self.parse_expr(expr_str)
            var = Symbol(variable)
            point_val = self.parse_expr(point)

            series_name = "Maclaurin" if point_val == 0 else "Taylor"
            steps.append(f"Compute {series_name} series of {expr_to_latex(expr)} around {variable} = {point}")
            steps.append(f"Order: {order}")

            result = series(expr, var, point_val, n=order)
            steps.append(f"Series: {expr_to_latex(result)}")

            # Remove the O() term for a polynomial approximation
            poly_approx = result.removeO()
            steps.append(f"Polynomial approximation: {expr_to_latex(poly_approx)}")

            return {
                "answer": str(result),
                "steps": steps,
                "latex": expr_to_latex(result),
                "polynomial": str(poly_approx),
                "polynomial_latex": expr_to_latex(poly_approx),
                "result": result,
            }
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": "", "result": None}

    def compute_sum(self, expr_str: str, variable: str = "n",
                    lower: str = "1", upper: str = "oo") -> dict:
        """Compute a summation."""
        steps = []
        try:
            expr = self.parse_expr(expr_str)
            var = Symbol(variable)
            lower_val = self.parse_expr(lower)
            upper_val = self.parse_expr(upper)

            steps.append(f"Compute sum of {expr_to_latex(expr)} for {variable} = {lower} to {upper}")

            result = summation(expr, (var, lower_val, upper_val))
            result = simplify(result)
            steps.append(f"Sum = {expr_to_latex(result)}")

            decimal_val = None
            try:
                decimal_val = float(result.evalf())
            except Exception:
                pass

            return {
                "answer": str(result),
                "steps": steps,
                "latex": expr_to_latex(result),
                "result": result,
                "decimal": decimal_val,
            }
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": "", "result": None}

    def solve_differential_equation(self, equation_str: str) -> dict:
        """Solve ordinary differential equations."""
        steps = []
        try:
            x = Symbol("x")
            y = Function("y")

            steps.append(f"Solve ODE: {equation_str}")

            # Parse various ODE formats
            expr_str = equation_str
            # Handle y' = f(x, y) format
            expr_str = expr_str.replace("y'", "Derivative(y(x), x)")
            expr_str = expr_str.replace("y''", "Derivative(y(x), x, x)")
            expr_str = expr_str.replace("y'''", "Derivative(y(x), x, x, x)")
            expr_str = expr_str.replace("dy/dx", "Derivative(y(x), x)")
            expr_str = expr_str.replace("d^2y/dx^2", "Derivative(y(x), x, x)")

            # Ensure y(x) is used
            expr_str = expr_str.replace("y", "y(x)")
            # Fix double replacements
            expr_str = expr_str.replace("y(x)(x)", "y(x)")
            expr_str = expr_str.replace("Derivative(y(x)(x)", "Derivative(y(x)")

            if "=" in expr_str:
                parts = expr_str.split("=", 1)
                lhs = self.parse_expr(parts[0].strip())
                rhs = self.parse_expr(parts[1].strip())
                from sympy import Eq as SymEq
                ode = SymEq(lhs, rhs)
            else:
                ode = self.parse_expr(expr_str)

            solution = sympy.dsolve(ode, y(x))
            steps.append(f"Solution: {expr_to_latex(solution)}")

            return {
                "answer": str(solution),
                "steps": steps,
                "latex": expr_to_latex(solution),
                "result": solution,
            }
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": "", "result": None}
