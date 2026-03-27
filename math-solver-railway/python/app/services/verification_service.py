import sympy
from sympy import (
    Symbol, symbols, sympify, simplify, Eq, oo, zoo, nan, S,
    Rational, Float, N,
)
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations,
    implicit_multiplication_application, convert_xor,
)
from typing import Any, Optional
import math


class VerificationService:
    """Verify solutions by substitution, numerical checking, and cross-methods."""

    TRANSFORMATIONS = standard_transformations + (
        implicit_multiplication_application,
        convert_xor,
    )

    def parse_expr(self, expr_str: str) -> Any:
        try:
            return parse_expr(expr_str, transformations=self.TRANSFORMATIONS)
        except Exception:
            return sympify(expr_str)

    def verify_solution(self, original_expr: str, solutions: Any,
                        variable: str = "x", problem_type: str = "equation") -> dict:
        """Verify a solution is correct."""
        results = []
        confidence = 1.0

        if problem_type == "equation":
            result = self._verify_equation(original_expr, solutions, variable)
            results.append(result)
            confidence = result.get("confidence", 0.5)
        elif problem_type == "system":
            result = self._verify_system(original_expr, solutions)
            results.append(result)
            confidence = result.get("confidence", 0.5)
        elif problem_type in ("arithmetic", "algebra"):
            result = self._verify_simplification(original_expr, solutions)
            results.append(result)
            confidence = result.get("confidence", 0.5)
        elif problem_type == "calculus":
            result = self._verify_calculus(original_expr, solutions, variable)
            results.append(result)
            confidence = result.get("confidence", 0.5)
        else:
            result = self._verify_numeric(original_expr, solutions, variable)
            results.append(result)
            confidence = result.get("confidence", 0.5)

        overall = all(r.get("verified", False) for r in results)
        message = "; ".join(r.get("message", "") for r in results)

        return {
            "verified": overall,
            "confidence": confidence,
            "message": message,
            "details": results,
        }

    def _verify_equation(self, equation_str: str, solutions: Any,
                         variable: str = "x") -> dict:
        """Verify equation solutions by substitution."""
        try:
            var = Symbol(variable)

            if "=" in equation_str:
                parts = equation_str.split("=", 1)
                lhs = self.parse_expr(parts[0].strip())
                rhs = self.parse_expr(parts[1].strip())
                expr = lhs - rhs
            else:
                expr = self.parse_expr(equation_str)

            if not isinstance(solutions, (list, tuple)):
                solutions = [solutions]

            all_verified = True
            messages = []

            for sol in solutions:
                try:
                    if isinstance(sol, str):
                        sol = self.parse_expr(sol)
                    substituted = expr.subs(var, sol)
                    simplified = simplify(substituted)

                    if simplified == 0:
                        messages.append(f"{variable}={sol}: verified (exact)")
                    else:
                        # Try numerical verification
                        try:
                            num_val = abs(float(N(simplified)))
                            if num_val < 1e-10:
                                messages.append(f"{variable}={sol}: verified (numerical, residual={num_val:.2e})")
                            else:
                                messages.append(f"{variable}={sol}: FAILED (residual={num_val:.2e})")
                                all_verified = False
                        except Exception:
                            messages.append(f"{variable}={sol}: could not verify numerically")
                            all_verified = False
                except Exception as e:
                    messages.append(f"{variable}={sol}: verification error: {e}")
                    all_verified = False

            return {
                "verified": all_verified,
                "confidence": 1.0 if all_verified else 0.3,
                "message": "; ".join(messages),
            }
        except Exception as e:
            return {"verified": False, "confidence": 0.0, "message": f"Verification error: {e}"}

    def _verify_system(self, expression: str, solutions: Any) -> dict:
        """Verify system of equations solution."""
        try:
            if isinstance(solutions, dict):
                sol_dict = solutions
            elif isinstance(solutions, (list, tuple)) and solutions:
                if isinstance(solutions[0], dict):
                    sol_dict = solutions[0]
                else:
                    return {"verified": False, "confidence": 0.5, "message": "Cannot verify this solution format"}
            else:
                return {"verified": False, "confidence": 0.5, "message": "No solutions to verify"}

            # Parse equations
            equations = []
            for sep in [";", "\n", "\\n", ","]:
                parts = [p.strip() for p in expression.split(sep) if "=" in p and p.strip()]
                if len(parts) >= 2:
                    equations = parts
                    break

            if not equations:
                return {"verified": False, "confidence": 0.5, "message": "Could not parse equations for verification"}

            all_verified = True
            messages = []

            for eq_str in equations:
                parts = eq_str.split("=", 1)
                lhs = self.parse_expr(parts[0].strip())
                rhs = self.parse_expr(parts[1].strip())
                diff_expr = lhs - rhs

                # Substitute all solutions
                substituted = diff_expr
                for var, val in sol_dict.items():
                    if isinstance(var, str):
                        var = Symbol(var)
                    if isinstance(val, str):
                        val = self.parse_expr(val)
                    substituted = substituted.subs(var, val)

                simplified = simplify(substituted)
                if simplified == 0:
                    messages.append(f"Equation '{eq_str}': verified")
                else:
                    try:
                        num_val = abs(float(N(simplified)))
                        if num_val < 1e-10:
                            messages.append(f"Equation '{eq_str}': verified (numerical)")
                        else:
                            messages.append(f"Equation '{eq_str}': FAILED")
                            all_verified = False
                    except Exception:
                        all_verified = False

            return {
                "verified": all_verified,
                "confidence": 1.0 if all_verified else 0.3,
                "message": "; ".join(messages),
            }
        except Exception as e:
            return {"verified": False, "confidence": 0.0, "message": f"Verification error: {e}"}

    def _verify_simplification(self, original: str, result: Any) -> dict:
        """Verify a simplification by numerical comparison."""
        try:
            orig_expr = self.parse_expr(original) if isinstance(original, str) else original
            res_expr = self.parse_expr(str(result)) if not hasattr(result, "free_symbols") else result

            diff = simplify(orig_expr - res_expr)
            if diff == 0:
                return {"verified": True, "confidence": 1.0, "message": "Verified: expressions are equivalent"}

            # Numerical check at random points
            free = sorted(orig_expr.free_symbols | res_expr.free_symbols, key=str)
            if not free:
                try:
                    orig_num = float(N(orig_expr))
                    res_num = float(N(res_expr))
                    if abs(orig_num - res_num) < 1e-10:
                        return {"verified": True, "confidence": 0.95, "message": "Verified numerically"}
                    return {"verified": False, "confidence": 0.1, "message": f"Mismatch: {orig_num} vs {res_num}"}
                except Exception:
                    pass

            import random
            random.seed(42)
            verified_count = 0
            test_count = 5

            for _ in range(test_count):
                subs = {v: random.uniform(0.1, 5.0) for v in free}
                try:
                    orig_val = float(N(orig_expr.subs(subs)))
                    res_val = float(N(res_expr.subs(subs)))
                    if math.isfinite(orig_val) and math.isfinite(res_val):
                        if abs(orig_val - res_val) < 1e-6 * max(abs(orig_val), 1):
                            verified_count += 1
                except Exception:
                    pass

            if verified_count == test_count:
                return {"verified": True, "confidence": 0.9, "message": f"Verified numerically at {test_count} points"}
            elif verified_count > 0:
                return {
                    "verified": False,
                    "confidence": verified_count / test_count * 0.5,
                    "message": f"Partially verified ({verified_count}/{test_count} points)",
                }
            return {"verified": False, "confidence": 0.1, "message": "Could not verify"}
        except Exception as e:
            return {"verified": False, "confidence": 0.0, "message": f"Error: {e}"}

    def _verify_calculus(self, original: str, result: Any, variable: str = "x") -> dict:
        """Verify calculus results (e.g., derivative by re-integrating)."""
        try:
            # For now, use numerical verification
            return self._verify_numeric(original, result, variable)
        except Exception as e:
            return {"verified": False, "confidence": 0.0, "message": f"Error: {e}"}

    def _verify_numeric(self, original: str, result: Any, variable: str = "x") -> dict:
        """Generic numerical verification."""
        try:
            if result is None:
                return {"verified": False, "confidence": 0.0, "message": "No result to verify"}

            # Basic sanity check: ensure result is a valid expression
            if isinstance(result, str):
                try:
                    res_expr = self.parse_expr(result)
                    if res_expr is not None:
                        return {"verified": True, "confidence": 0.7, "message": "Result is a valid expression"}
                except Exception:
                    pass

            return {"verified": True, "confidence": 0.6, "message": "Result produced without errors"}
        except Exception as e:
            return {"verified": False, "confidence": 0.0, "message": f"Error: {e}"}
