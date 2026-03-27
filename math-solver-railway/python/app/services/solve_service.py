import re
from typing import Any, Optional

from app.services.parser_service import ParserService
from app.services.symbolic_service import SymbolicService
from app.services.numeric_service import NumericService
from app.services.calculus_service import CalculusService
from app.services.linear_algebra_service import LinearAlgebraService
from app.services.stats_service import StatsService
from app.services.verification_service import VerificationService
from app.utils.latex_utils import expr_to_latex
from app.utils.math_utils import safe_sympify, safe_float


class SolveService:
    """Main solver orchestrator that routes to appropriate services."""

    def __init__(self):
        self.parser = ParserService()
        self.symbolic = SymbolicService()
        self.numeric = NumericService()
        self.calculus = CalculusService()
        self.linear_algebra = LinearAlgebraService()
        self.stats = StatsService()
        self.verifier = VerificationService()

    def solve(self, expression: str, problem_type: str = None,
              variables: list = None, precision: int = 15,
              show_steps: bool = True, verify: bool = True) -> dict:
        """Main entry point for solving any math problem."""

        # Parse the expression
        parsed = self.parser.parse(expression)
        detected_type = problem_type or parsed["problem_type"]
        normalized = parsed["normalized"]
        detected_vars = variables or parsed["variables"]

        result = {
            "answer": "",
            "steps": [],
            "latex": None,
            "simplified": None,
            "decimal_approx": None,
            "confidence": 0.0,
            "graph_data": None,
            "problem_type": detected_type,
            "verification": None,
            "error": None,
        }

        try:
            if detected_type == "arithmetic":
                sol = self._solve_arithmetic(normalized)
            elif detected_type == "algebra":
                sol = self._solve_algebra(normalized, expression)
            elif detected_type == "equation":
                sol = self._solve_equation(normalized, detected_vars)
            elif detected_type == "system":
                sol = self._solve_system(expression, detected_vars)
            elif detected_type == "calculus":
                sol = self._solve_calculus(expression, normalized, detected_vars)
            elif detected_type == "differential_equation":
                sol = self._solve_differential_equation(expression)
            elif detected_type == "linear_algebra":
                sol = self._solve_linear_algebra(expression)
            elif detected_type == "stats":
                sol = self._solve_stats(expression)
            elif detected_type == "optimization":
                sol = self._solve_optimization(normalized, detected_vars)
            else:
                # Try arithmetic first, then algebra
                sol = self._solve_arithmetic(normalized)
                if "Error" in sol.get("answer", "Error"):
                    sol = self._solve_algebra(normalized, expression)

            result.update({
                "answer": sol.get("answer", ""),
                "steps": sol.get("steps", []),
                "latex": sol.get("latex"),
                "confidence": sol.get("confidence", 0.8),
            })

            # Compute simplified form and decimal approximation
            if result["answer"] and "Error" not in result["answer"]:
                self._add_simplification(result)
                self._add_decimal_approx(result, precision)

                # Generate graph data for plottable expressions
                graph_data = self._generate_graph_data(expression, detected_type, detected_vars)
                if graph_data:
                    result["graph_data"] = graph_data

            # Verify if requested
            if verify and result["answer"] and "Error" not in result["answer"]:
                solutions = sol.get("solutions", sol.get("result", result["answer"]))
                var = detected_vars[0] if detected_vars else "x"
                verification = self.verifier.verify_solution(
                    expression, solutions, variable=var, problem_type=detected_type
                )
                result["verification"] = verification.get("message", "")
                # Adjust confidence based on verification
                if verification.get("verified"):
                    result["confidence"] = max(result["confidence"], verification.get("confidence", 0.8))
                else:
                    result["confidence"] = min(result["confidence"], verification.get("confidence", 0.5))

        except Exception as e:
            result["error"] = str(e)
            result["answer"] = f"Error: {e}"
            result["confidence"] = 0.0

        return result

    def _solve_arithmetic(self, expression: str) -> dict:
        """Solve arithmetic expressions."""
        steps = []
        try:
            result = self.symbolic.evaluate(expression)
            if "Error" not in result.get("answer", "Error"):
                return {
                    "answer": result["answer"],
                    "steps": result["steps"],
                    "latex": result["latex"],
                    "confidence": 1.0,
                    "result": result.get("result"),
                }

            # Fallback: try direct Python evaluation for simple arithmetic
            cleaned = expression.replace("^", "**")
            # Only evaluate if it looks safe
            if re.match(r"^[\d\s+\-*/().%]+$", cleaned):
                val = eval(cleaned)
                steps.append(f"{expression} = {val}")
                return {
                    "answer": str(val),
                    "steps": steps,
                    "latex": str(val),
                    "confidence": 1.0,
                    "result": val,
                }
            return result
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": "", "confidence": 0.0}

    def _solve_algebra(self, normalized: str, original: str) -> dict:
        """Solve algebraic problems: simplify, factor, expand, etc."""
        lower = original.lower().strip()

        # Detect the specific operation
        if lower.startswith("factor"):
            expr = re.sub(r"^factor\s*", "", lower, flags=re.IGNORECASE).strip("() ")
            if not expr:
                expr = normalized
            result = self.symbolic.factor_expression(expr)
        elif lower.startswith("expand"):
            expr = re.sub(r"^expand\s*", "", lower, flags=re.IGNORECASE).strip("() ")
            if not expr:
                expr = normalized
            result = self.symbolic.expand_expression(expr)
        elif "partial" in lower and "fraction" in lower:
            expr = re.sub(r"partial\s*fractions?\s*(of)?\s*", "", lower, flags=re.IGNORECASE).strip()
            if not expr:
                expr = normalized
            result = self.symbolic.partial_fractions(expr)
        elif lower.startswith("simplify"):
            expr = re.sub(r"^simplify\s*", "", lower, flags=re.IGNORECASE).strip("() ")
            if not expr:
                expr = normalized
            result = self.symbolic.simplify_expression(expr)
        elif "=" in normalized:
            # It's an equation
            return self._solve_equation(normalized, [])
        else:
            # Default: simplify
            result = self.symbolic.simplify_expression(normalized)

        result["confidence"] = result.get("confidence", 0.9)
        return result

    def _solve_equation(self, expression: str, variables: list) -> dict:
        """Solve a single equation."""
        var = variables[0] if variables else None
        result = self.symbolic.solve_equation(expression, variable=var)

        # If symbolic fails, try numeric
        if not result.get("solutions") and "Error" not in result.get("answer", ""):
            var_name = var or "x"
            numeric_result = self.numeric.solve_equation_numeric(expression, variable=var_name)
            if numeric_result.get("roots"):
                result["answer"] = numeric_result["answer"]
                result["steps"] = result.get("steps", []) + ["Falling back to numerical methods"] + numeric_result["steps"]
                result["solutions"] = numeric_result["roots"]
                result["confidence"] = 0.85

        result.setdefault("confidence", 0.9)
        return result

    def _solve_system(self, expression: str, variables: list) -> dict:
        """Solve a system of equations."""
        equations = self.parser.split_system(expression)
        result = self.symbolic.solve_system(equations, variables=variables)
        result.setdefault("confidence", 0.9)
        return result

    def _solve_calculus(self, original: str, normalized: str, variables: list) -> dict:
        """Route calculus problems."""
        lower = original.lower().strip()
        var = variables[0] if variables else "x"

        # Detect the specific calculus operation
        if re.search(r"\bderivative\b|\bdifferentiate\b|\bd/d[a-z]\b|\bdiff\b", lower):
            expr, var_name, order = self._parse_derivative_command(original, var)
            return self.calculus.derivative(expr, variable=var_name, order=order)

        elif re.search(r"\bintegral\b|\bintegrate\b|\bantiderivative\b", lower):
            expr, var_name, lower_bound, upper_bound = self._parse_integral_command(original, var)
            return self.calculus.integral(expr, variable=var_name, lower=lower_bound, upper=upper_bound)

        elif re.search(r"\blimit\b|\blim\b", lower):
            expr, var_name, point, direction = self._parse_limit_command(original, var)
            return self.calculus.compute_limit(expr, variable=var_name, point=point, direction=direction)

        elif re.search(r"\btaylor\b|\bmaclaurin\b|\bseries\b", lower):
            expr, var_name, point, order = self._parse_series_command(original, var)
            return self.calculus.taylor_series(expr, variable=var_name, point=point, order=order)

        elif re.search(r"\bsum\b", lower) and re.search(r"[nki]\s*=", lower):
            expr, var_name, lower_val, upper_val = self._parse_sum_command(original)
            return self.calculus.compute_sum(expr, variable=var_name, lower=lower_val, upper=upper_val)

        else:
            # Default: try derivative
            return self.calculus.derivative(normalized, variable=var)

    def _solve_differential_equation(self, expression: str) -> dict:
        """Solve a differential equation."""
        result = self.calculus.solve_differential_equation(expression)
        result.setdefault("confidence", 0.8)
        return result

    def _solve_linear_algebra(self, expression: str) -> dict:
        """Solve linear algebra problems."""
        result = self.linear_algebra.process(expression)
        result.setdefault("confidence", 0.9)
        return result

    def _solve_stats(self, expression: str) -> dict:
        """Solve statistics problems."""
        result = self.stats.process(expression)
        result.setdefault("confidence", 0.9)
        return result

    def _solve_optimization(self, expression: str, variables: list) -> dict:
        """Solve optimization problems."""
        steps = []
        try:
            lower = expression.lower()
            find_max = "max" in lower

            # Extract the function to optimize
            func_str = re.sub(r"\b(minimize|maximize|optimize|min|max)\s*(of)?\s*", "", expression, flags=re.IGNORECASE).strip()

            var = variables[0] if variables else "x"

            # Try symbolic first: find critical points
            import sympy
            from sympy import Symbol, diff, solve, simplify
            from sympy.parsing.sympy_parser import parse_expr

            transformations = self.symbolic.TRANSFORMATIONS
            expr = parse_expr(func_str, transformations=transformations)
            v = Symbol(var)

            steps.append(f"Function: f({var}) = {expr_to_latex(expr)}")

            # Find critical points
            deriv = diff(expr, v)
            steps.append(f"f'({var}) = {expr_to_latex(deriv)}")

            critical = solve(deriv, v)
            steps.append(f"Critical points: {critical}")

            # Second derivative test
            second_deriv = diff(deriv, v)
            steps.append(f"f''({var}) = {expr_to_latex(second_deriv)}")

            results = []
            for cp in critical:
                sd_val = second_deriv.subs(v, cp)
                f_val = expr.subs(v, cp)
                nature = "unknown"
                if sd_val > 0:
                    nature = "local minimum"
                elif sd_val < 0:
                    nature = "local maximum"
                elif sd_val == 0:
                    nature = "inflection point"
                results.append({"point": cp, "value": simplify(f_val), "nature": nature})
                steps.append(f"At {var} = {cp}: f = {simplify(f_val)}, f'' = {sd_val} ({nature})")

            if results:
                if find_max:
                    best = max(results, key=lambda r: float(r["value"].evalf()) if r["value"].is_finite else float("-inf"))
                    answer = f"Maximum at {var} = {best['point']}, f = {best['value']}"
                else:
                    best = min(results, key=lambda r: float(r["value"].evalf()) if r["value"].is_finite else float("inf"))
                    answer = f"Minimum at {var} = {best['point']}, f = {best['value']}"
            else:
                answer = "No critical points found"

            return {"answer": answer, "steps": steps, "latex": answer, "confidence": 0.9}

        except Exception as e:
            # Fallback to numeric
            try:
                func_str = re.sub(r"\b(minimize|maximize|optimize|min|max)\s*(of)?\s*", "", expression, flags=re.IGNORECASE).strip()
                var = variables[0] if variables else "x"
                find_max = "max" in expression.lower()
                return self.numeric.optimize_function(func_str, variable=var, find_max=find_max)
            except Exception as e2:
                return {"answer": f"Error: {e2}", "steps": steps, "latex": "", "confidence": 0.0}

    def _add_simplification(self, result: dict):
        """Add simplified form to result."""
        try:
            answer = result["answer"]
            # Don't try to simplify non-expression answers
            if any(w in answer.lower() for w in ["error", "no solution", "verified"]):
                return
            # Try to extract just the expression part
            if "=" in answer:
                parts = answer.split("=")
                if len(parts) == 2:
                    expr_part = parts[1].strip().rstrip(",")
                    expr = safe_sympify(expr_part)
                    if expr is not None:
                        from sympy import simplify
                        simplified = simplify(expr)
                        result["simplified"] = str(simplified)
            else:
                expr = safe_sympify(answer)
                if expr is not None:
                    from sympy import simplify
                    simplified = simplify(expr)
                    result["simplified"] = str(simplified)
        except Exception:
            pass

    def _add_decimal_approx(self, result: dict, precision: int):
        """Add decimal approximation to result."""
        try:
            answer = result["answer"]
            if any(w in answer.lower() for w in ["error", "no solution"]):
                return
            # Extract expression from answer
            expr_str = answer
            if "=" in answer:
                parts = answer.split("=")
                if len(parts) >= 2:
                    expr_str = parts[-1].strip().rstrip(",")

            # Handle multiple solutions
            if "," in expr_str and "=" in expr_str:
                return  # Complex multi-solution answer

            expr = safe_sympify(expr_str)
            if expr is not None:
                val = safe_float(expr.evalf(precision))
                if val is not None:
                    result["decimal_approx"] = f"{val:.{min(precision, 15)}g}"
        except Exception:
            pass

    def _generate_graph_data(self, expression: str, problem_type: str,
                             variables: list) -> Optional[dict]:
        """Generate graph data hint for the frontend."""
        if problem_type in ("arithmetic", "stats", "linear_algebra"):
            return None
        if not variables:
            return None
        return {
            "expression": expression,
            "type": "function",
            "variable": variables[0] if variables else "x",
        }

    # --- Command parsers ---

    def _parse_derivative_command(self, text: str, default_var: str) -> tuple:
        """Parse derivative command, returning (expression, variable, order)."""
        lower = text.lower()
        order = 1
        # Check for order
        order_match = re.search(r"(\d+)(?:st|nd|rd|th)\s*derivative", lower)
        if order_match:
            order = int(order_match.group(1))
        elif "second" in lower:
            order = 2
        elif "third" in lower:
            order = 3

        # Extract variable
        var = default_var
        var_match = re.search(r"(?:with respect to|wrt|d/d)\s*([a-zA-Z])", lower)
        if var_match:
            var = var_match.group(1)

        # Extract expression
        expr = text
        for pattern in [
            r"(?:derivative|differentiate|diff)\s+(?:of\s+)?(.+?)(?:\s+with|\s+wrt|\s+d/d|\s*$)",
            r"d/d[a-z]\s*\(?\s*(.+?)\s*\)?\s*$",
        ]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                expr = match.group(1).strip()
                break

        # Clean up
        expr = re.sub(r"\bwith respect to\b.*$", "", expr, flags=re.IGNORECASE).strip()
        expr = re.sub(r"\bwrt\b.*$", "", expr, flags=re.IGNORECASE).strip()

        return expr, var, order

    def _parse_integral_command(self, text: str, default_var: str) -> tuple:
        """Parse integral command, returning (expression, variable, lower, upper)."""
        lower_text = text.lower()
        var = default_var
        lower_bound = None
        upper_bound = None

        # Check for bounds
        bounds_match = re.search(r"from\s+(-?[\d.]+|[-\w]+)\s+to\s+(-?[\d.]+|[-\w]+|oo|inf)", lower_text)
        if bounds_match:
            lower_bound = bounds_match.group(1)
            upper_bound = bounds_match.group(2)
            if upper_bound in ("inf", "infinity"):
                upper_bound = "oo"

        # Extract variable
        var_match = re.search(r"(?:with respect to|wrt|d)\s*([a-zA-Z])", lower_text)
        if var_match:
            var = var_match.group(1)

        # Extract expression
        expr = text
        for pattern in [
            r"(?:integrate|integral)\s+(?:of\s+)?(.+?)(?:\s+from|\s+with|\s+wrt|\s+d[a-z]|\s*$)",
            r"(?:integrate|integral)\s+(.+)",
        ]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                expr = match.group(1).strip()
                break

        expr = re.sub(r"\bfrom\b.*$", "", expr, flags=re.IGNORECASE).strip()
        expr = re.sub(r"\bwith respect to\b.*$", "", expr, flags=re.IGNORECASE).strip()
        expr = re.sub(r"\bwrt\b.*$", "", expr, flags=re.IGNORECASE).strip()
        expr = re.sub(r"\s+d[a-z]\s*$", "", expr).strip()

        return expr, var, lower_bound, upper_bound

    def _parse_limit_command(self, text: str, default_var: str) -> tuple:
        """Parse limit command, returning (expression, variable, point, direction)."""
        lower_text = text.lower()
        var = default_var
        point = "0"
        direction = ""

        # Extract point
        point_match = re.search(r"(?:as|->|to)\s*([a-zA-Z])\s*(?:->|approaches?|to|=)\s*(-?[\d.]+|oo|inf|infinity|pi|e)", lower_text)
        if point_match:
            var = point_match.group(1)
            point = point_match.group(2)
            if point in ("inf", "infinity"):
                point = "oo"

        # Check for direction
        if any(w in lower_text for w in ["from right", "right", "from above", "+"]):
            direction = "+"
        elif any(w in lower_text for w in ["from left", "left", "from below", "-"]):
            direction = "-"

        # Extract expression
        expr = text
        for pattern in [
            r"(?:limit|lim)\s+(?:of\s+)?(.+?)(?:\s+as\s|\s+->|\s+when|\s*$)",
            r"(?:limit|lim)\s+(.+)",
        ]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                expr = match.group(1).strip()
                break

        expr = re.sub(r"\bas\b.*$", "", expr, flags=re.IGNORECASE).strip()
        expr = re.sub(r"->.*$", "", expr).strip()

        return expr, var, point, direction

    def _parse_series_command(self, text: str, default_var: str) -> tuple:
        """Parse series command, returning (expression, variable, point, order)."""
        lower_text = text.lower()
        var = default_var
        point = "0"
        order = 6

        # Extract point
        point_match = re.search(r"(?:around|about|at)\s*([a-zA-Z])\s*=\s*(-?[\d.]+)", lower_text)
        if point_match:
            point = point_match.group(2)

        # Extract order
        order_match = re.search(r"(?:order|degree|terms?)\s*(?:=\s*)?(\d+)", lower_text)
        if order_match:
            order = int(order_match.group(1))

        # Extract expression
        expr = text
        for pattern in [
            r"(?:taylor|maclaurin|series)\s+(?:of\s+|expansion\s+of\s+)?(.+?)(?:\s+around|\s+about|\s+at|\s+order|\s*$)",
            r"(?:taylor|maclaurin|series)\s+(.+)",
        ]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                expr = match.group(1).strip()
                break

        expr = re.sub(r"\b(around|about|at|order|degree|terms?)\b.*$", "", expr, flags=re.IGNORECASE).strip()

        return expr, var, point, order

    def _parse_sum_command(self, text: str) -> tuple:
        """Parse summation command."""
        lower_text = text.lower()
        var = "n"
        lower_val = "1"
        upper_val = "oo"

        # Extract variable and bounds: n=1 to 100
        bounds_match = re.search(r"([a-zA-Z])\s*=\s*(-?[\d]+)\s*(?:to|\.\.)\s*(-?[\d]+|oo|inf|infinity)", lower_text)
        if bounds_match:
            var = bounds_match.group(1)
            lower_val = bounds_match.group(2)
            upper_val = bounds_match.group(3)
            if upper_val in ("inf", "infinity"):
                upper_val = "oo"

        # Extract expression
        expr = text
        match = re.search(r"sum\s+(?:of\s+)?(.+?)(?:\s+for|\s+where|\s+[a-zA-Z]\s*=|\s*$)", text, re.IGNORECASE)
        if match:
            expr = match.group(1).strip()
        else:
            expr = re.sub(r"\bsum\b\s*", "", text, flags=re.IGNORECASE).strip()
            expr = re.sub(r"[a-zA-Z]\s*=\s*\d+\s*(to|\.\.)\s*[\d\w]+", "", expr).strip()
            expr = re.sub(r"\bfor\b.*$", "", expr, flags=re.IGNORECASE).strip()

        return expr, var, lower_val, upper_val
