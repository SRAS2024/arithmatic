import sympy
from sympy import (
    Symbol, symbols, sympify, solve, simplify, factor, expand,
    apart, together, cancel, trigsimp, powsimp, radsimp,
    Eq, Rational, oo, pi, E, I, S,
    sin, cos, tan, cot, sec, csc, log, exp, sqrt, Abs,
    Poly, gcd, lcm, degree,
)
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations,
    implicit_multiplication_application, convert_xor,
)
from typing import Any, Optional
from app.utils.latex_utils import expr_to_latex, equation_to_latex


class SymbolicService:
    """Symbolic math using SymPy."""

    TRANSFORMATIONS = standard_transformations + (
        implicit_multiplication_application,
        convert_xor,
    )

    def parse_expression(self, expr_str: str) -> Any:
        """Parse a string into a SymPy expression."""
        try:
            return parse_expr(expr_str, transformations=self.TRANSFORMATIONS)
        except Exception:
            return sympify(expr_str)

    def solve_equation(self, equation_str: str, variable: str = None) -> dict:
        """Solve a single equation."""
        steps = []
        try:
            if "=" in equation_str:
                parts = equation_str.split("=", 1)
                lhs = self.parse_expression(parts[0].strip())
                rhs = self.parse_expression(parts[1].strip())
                steps.append(f"Given equation: {expr_to_latex(lhs)} = {expr_to_latex(rhs)}")
                equation = Eq(lhs, rhs)
                expr_to_solve = lhs - rhs
            else:
                expr_to_solve = self.parse_expression(equation_str)
                equation = Eq(expr_to_solve, 0)
                steps.append(f"Solve: {expr_to_latex(expr_to_solve)} = 0")

            free_syms = sorted(expr_to_solve.free_symbols, key=lambda s: str(s))
            if variable:
                var = Symbol(variable)
            elif free_syms:
                var = free_syms[0]
            else:
                result = simplify(expr_to_solve)
                return {
                    "answer": str(result),
                    "steps": [f"Expression evaluates to: {expr_to_latex(result)}"],
                    "latex": expr_to_latex(result),
                    "solutions": [result],
                }

            steps.append(f"Solving for {var}")

            # Try to simplify first
            simplified = simplify(expr_to_solve)
            if simplified != expr_to_solve:
                steps.append(f"Simplified: {expr_to_latex(simplified)} = 0")

            solutions = solve(equation, var)

            if not solutions:
                solutions = solve(expr_to_solve, var)

            if not solutions:
                return {
                    "answer": "No solution found",
                    "steps": steps + ["No symbolic solution exists or could be found"],
                    "latex": "",
                    "solutions": [],
                }

            if isinstance(solutions, dict):
                solutions = list(solutions.values())

            for i, sol in enumerate(solutions):
                sol_simplified = simplify(sol)
                solutions[i] = sol_simplified
                steps.append(f"Solution {i + 1}: {var} = {expr_to_latex(sol_simplified)}")

            if len(solutions) == 1:
                answer = f"{var} = {solutions[0]}"
                latex = equation_to_latex(var, solutions[0])
            else:
                answer = ", ".join(f"{var} = {s}" for s in solutions)
                latex = ", ".join(equation_to_latex(var, s) for s in solutions)

            return {
                "answer": answer,
                "steps": steps,
                "latex": latex,
                "solutions": solutions,
            }
        except Exception as e:
            return {
                "answer": f"Error: {e}",
                "steps": steps + [f"Error during solving: {e}"],
                "latex": "",
                "solutions": [],
            }

    def solve_system(self, equations: list[str], variables: list[str] = None) -> dict:
        """Solve a system of equations."""
        steps = []
        try:
            eqs = []
            for eq_str in equations:
                if "=" in eq_str:
                    parts = eq_str.split("=", 1)
                    lhs = self.parse_expression(parts[0].strip())
                    rhs = self.parse_expression(parts[1].strip())
                    eqs.append(Eq(lhs, rhs))
                    steps.append(f"Equation: {expr_to_latex(lhs)} = {expr_to_latex(rhs)}")
                else:
                    expr = self.parse_expression(eq_str)
                    eqs.append(Eq(expr, 0))
                    steps.append(f"Equation: {expr_to_latex(expr)} = 0")

            all_syms = set()
            for eq in eqs:
                all_syms.update(eq.free_symbols)
            all_syms = sorted(all_syms, key=lambda s: str(s))

            if variables:
                vars_to_solve = [Symbol(v) for v in variables]
            else:
                vars_to_solve = all_syms

            steps.append(f"Variables: {', '.join(str(v) for v in vars_to_solve)}")
            steps.append(f"Solving system of {len(eqs)} equations")

            solutions = solve(eqs, vars_to_solve)

            if isinstance(solutions, dict):
                answer_parts = []
                for var, val in solutions.items():
                    val_s = simplify(val)
                    answer_parts.append(f"{var} = {val_s}")
                    steps.append(f"Solution: {var} = {expr_to_latex(val_s)}")
                answer = ", ".join(answer_parts)
                latex = ", ".join(equation_to_latex(k, simplify(v)) for k, v in solutions.items())
            elif isinstance(solutions, list):
                if solutions and isinstance(solutions[0], dict):
                    answer_parts = []
                    for i, sol_dict in enumerate(solutions):
                        parts = []
                        for var, val in sol_dict.items():
                            parts.append(f"{var} = {simplify(val)}")
                        answer_parts.append(f"Solution {i + 1}: {', '.join(parts)}")
                        steps.append(answer_parts[-1])
                    answer = "; ".join(answer_parts)
                    latex = answer
                elif solutions and isinstance(solutions[0], tuple):
                    answer_parts = []
                    for i, sol_tuple in enumerate(solutions):
                        parts = []
                        for var, val in zip(vars_to_solve, sol_tuple):
                            parts.append(f"{var} = {simplify(val)}")
                        answer_parts.append(f"Solution {i + 1}: {', '.join(parts)}")
                        steps.append(answer_parts[-1])
                    answer = "; ".join(answer_parts)
                    latex = answer
                else:
                    answer = str(solutions)
                    latex = answer
                    steps.append(f"Solutions: {answer}")
            else:
                answer = str(solutions)
                latex = answer
                steps.append(f"Solutions: {answer}")

            return {
                "answer": answer,
                "steps": steps,
                "latex": latex,
                "solutions": solutions,
            }
        except Exception as e:
            return {
                "answer": f"Error: {e}",
                "steps": steps + [f"Error: {e}"],
                "latex": "",
                "solutions": [],
            }

    def simplify_expression(self, expr_str: str) -> dict:
        """Simplify an expression."""
        steps = []
        try:
            expr = self.parse_expression(expr_str)
            steps.append(f"Original: {expr_to_latex(expr)}")

            result = simplify(expr)
            steps.append(f"Simplified: {expr_to_latex(result)}")

            # Try additional simplification strategies
            trig_result = trigsimp(expr)
            if trig_result != result and len(str(trig_result)) < len(str(result)):
                result = trig_result
                steps.append(f"Trig simplified: {expr_to_latex(result)}")

            return {
                "answer": str(result),
                "steps": steps,
                "latex": expr_to_latex(result),
                "simplified": result,
            }
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": "", "simplified": None}

    def factor_expression(self, expr_str: str) -> dict:
        """Factor an expression."""
        steps = []
        try:
            expr = self.parse_expression(expr_str)
            steps.append(f"Original: {expr_to_latex(expr)}")

            result = factor(expr)
            steps.append(f"Factored: {expr_to_latex(result)}")

            return {
                "answer": str(result),
                "steps": steps,
                "latex": expr_to_latex(result),
                "factored": result,
            }
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": "", "factored": None}

    def expand_expression(self, expr_str: str) -> dict:
        """Expand an expression."""
        steps = []
        try:
            expr = self.parse_expression(expr_str)
            steps.append(f"Original: {expr_to_latex(expr)}")

            result = expand(expr)
            steps.append(f"Expanded: {expr_to_latex(result)}")

            return {
                "answer": str(result),
                "steps": steps,
                "latex": expr_to_latex(result),
                "expanded": result,
            }
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": "", "expanded": None}

    def partial_fractions(self, expr_str: str, var: str = None) -> dict:
        """Decompose into partial fractions."""
        steps = []
        try:
            expr = self.parse_expression(expr_str)
            steps.append(f"Original: {expr_to_latex(expr)}")

            if var:
                v = Symbol(var)
            else:
                free = sorted(expr.free_symbols, key=lambda s: str(s))
                v = free[0] if free else Symbol("x")

            result = apart(expr, v)
            steps.append(f"Partial fractions: {expr_to_latex(result)}")

            return {
                "answer": str(result),
                "steps": steps,
                "latex": expr_to_latex(result),
                "result": result,
            }
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": "", "result": None}

    def evaluate(self, expr_str: str) -> dict:
        """Evaluate a numeric expression."""
        steps = []
        try:
            expr = self.parse_expression(expr_str)
            steps.append(f"Expression: {expr_to_latex(expr)}")

            result = simplify(expr)
            steps.append(f"Result: {expr_to_latex(result)}")

            decimal = None
            try:
                decimal = float(result.evalf())
            except Exception:
                pass

            return {
                "answer": str(result),
                "steps": steps,
                "latex": expr_to_latex(result),
                "decimal": decimal,
                "result": result,
            }
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": "", "decimal": None, "result": None}
