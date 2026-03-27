import numpy as np
from scipy import optimize, integrate as sci_integrate, linalg
from typing import Any, Optional
import warnings

warnings.filterwarnings("ignore")


class NumericService:
    """Numerical computation using scipy/numpy as fallback."""

    def solve_equation_numeric(self, func_str: str, variable: str = "x",
                                initial_guess: float = 1.0,
                                bounds: tuple = (-100, 100)) -> dict:
        """Solve an equation numerically using root-finding."""
        steps = []
        try:
            import sympy
            from sympy.parsing.sympy_parser import (
                parse_expr, standard_transformations,
                implicit_multiplication_application, convert_xor,
            )
            transformations = standard_transformations + (
                implicit_multiplication_application, convert_xor,
            )

            if "=" in func_str:
                parts = func_str.split("=", 1)
                lhs = parse_expr(parts[0].strip(), transformations=transformations)
                rhs = parse_expr(parts[1].strip(), transformations=transformations)
                expr = lhs - rhs
            else:
                expr = parse_expr(func_str, transformations=transformations)

            var = sympy.Symbol(variable)
            f_lambda = sympy.lambdify(var, expr, modules=["numpy"])

            steps.append(f"Attempting numerical root-finding for: {func_str}")

            # Try multiple initial guesses
            roots = set()
            guesses = [initial_guess, 0.0, 1.0, -1.0, 0.5, -0.5, 2.0, -2.0, 5.0, -5.0, 10.0, -10.0]

            for guess in guesses:
                try:
                    root = optimize.brentq(f_lambda, guess - 10, guess + 10)
                    root_rounded = round(root, 10)
                    if abs(f_lambda(root)) < 1e-8:
                        roots.add(root_rounded)
                except Exception:
                    pass
                try:
                    result = optimize.fsolve(f_lambda, guess, full_output=True)
                    root = result[0][0]
                    info = result[1]
                    if abs(f_lambda(root)) < 1e-8:
                        roots.add(round(root, 10))
                except Exception:
                    pass

            roots = sorted(roots)
            if roots:
                for i, r in enumerate(roots):
                    steps.append(f"Root {i + 1}: {variable} = {r}")
                answer = ", ".join(f"{variable} = {r}" for r in roots)
            else:
                answer = "No numerical solution found"
                steps.append("Could not find numerical roots")

            return {
                "answer": answer,
                "steps": steps,
                "roots": roots,
                "method": "numerical",
            }
        except Exception as e:
            return {
                "answer": f"Error: {e}",
                "steps": steps + [f"Numerical error: {e}"],
                "roots": [],
                "method": "numerical",
            }

    def integrate_numeric(self, func_str: str, variable: str = "x",
                          lower: float = 0, upper: float = 1) -> dict:
        """Compute a definite integral numerically."""
        steps = []
        try:
            import sympy
            from sympy.parsing.sympy_parser import (
                parse_expr, standard_transformations,
                implicit_multiplication_application, convert_xor,
            )
            transformations = standard_transformations + (
                implicit_multiplication_application, convert_xor,
            )

            expr = parse_expr(func_str, transformations=transformations)
            var = sympy.Symbol(variable)
            f_lambda = sympy.lambdify(var, expr, modules=["numpy"])

            steps.append(f"Numerically integrating from {lower} to {upper}")

            result, error = sci_integrate.quad(f_lambda, lower, upper)

            steps.append(f"Result: {result}")
            steps.append(f"Estimated error: {error}")

            return {
                "answer": str(result),
                "steps": steps,
                "value": result,
                "error_estimate": error,
                "method": "numerical quadrature",
            }
        except Exception as e:
            return {
                "answer": f"Error: {e}",
                "steps": steps + [f"Integration error: {e}"],
                "value": None,
                "error_estimate": None,
                "method": "numerical quadrature",
            }

    def optimize_function(self, func_str: str, variable: str = "x",
                          bounds: tuple = (-10, 10),
                          find_max: bool = False) -> dict:
        """Find minimum/maximum of a function numerically."""
        steps = []
        try:
            import sympy
            from sympy.parsing.sympy_parser import (
                parse_expr, standard_transformations,
                implicit_multiplication_application, convert_xor,
            )
            transformations = standard_transformations + (
                implicit_multiplication_application, convert_xor,
            )

            expr = parse_expr(func_str, transformations=transformations)
            var = sympy.Symbol(variable)
            f_lambda = sympy.lambdify(var, expr, modules=["numpy"])

            goal = "maximum" if find_max else "minimum"
            steps.append(f"Finding {goal} of f({variable}) = {func_str}")
            steps.append(f"Search range: [{bounds[0]}, {bounds[1]}]")

            if find_max:
                neg_f = lambda x: -f_lambda(x)
                result = optimize.minimize_scalar(neg_f, bounds=bounds, method="bounded")
                opt_x = result.x
                opt_y = f_lambda(opt_x)
            else:
                result = optimize.minimize_scalar(f_lambda, bounds=bounds, method="bounded")
                opt_x = result.x
                opt_y = result.fun

            steps.append(f"Optimal {variable} = {round(opt_x, 10)}")
            steps.append(f"Optimal value = {round(opt_y, 10)}")

            return {
                "answer": f"{goal} at {variable} = {round(opt_x, 10)}, value = {round(opt_y, 10)}",
                "steps": steps,
                "optimal_x": opt_x,
                "optimal_y": opt_y,
                "method": "numerical optimization",
            }
        except Exception as e:
            return {
                "answer": f"Error: {e}",
                "steps": steps + [f"Optimization error: {e}"],
                "optimal_x": None,
                "optimal_y": None,
                "method": "numerical optimization",
            }

    def solve_ode_numeric(self, func_str: str, t_span: tuple = (0, 10),
                          y0: list = None, num_points: int = 100) -> dict:
        """Solve an ODE numerically using scipy."""
        steps = []
        try:
            if y0 is None:
                y0 = [1.0]

            import sympy
            from sympy.parsing.sympy_parser import (
                parse_expr, standard_transformations,
                implicit_multiplication_application, convert_xor,
            )
            transformations = standard_transformations + (
                implicit_multiplication_application, convert_xor,
            )

            expr = parse_expr(func_str, transformations=transformations)
            t_sym, y_sym = sympy.symbols("t y")
            f_lambda = sympy.lambdify((t_sym, y_sym), expr, modules=["numpy"])

            steps.append(f"Solving ODE: dy/dt = {func_str}")
            steps.append(f"Time span: [{t_span[0]}, {t_span[1]}]")
            steps.append(f"Initial condition: y({t_span[0]}) = {y0[0]}")

            t_eval = np.linspace(t_span[0], t_span[1], num_points)
            solution = sci_integrate.solve_ivp(
                lambda t, y: f_lambda(t, y[0]),
                t_span, y0, t_eval=t_eval, method="RK45"
            )

            steps.append(f"Solution computed with {len(solution.t)} points")
            steps.append(f"y({t_span[1]}) = {solution.y[0][-1]:.6f}")

            return {
                "answer": f"ODE solved numerically, y({t_span[1]}) = {solution.y[0][-1]:.6f}",
                "steps": steps,
                "t": solution.t.tolist(),
                "y": solution.y[0].tolist(),
                "method": "Runge-Kutta (RK45)",
            }
        except Exception as e:
            return {
                "answer": f"Error: {e}",
                "steps": steps + [f"ODE error: {e}"],
                "t": [],
                "y": [],
                "method": "Runge-Kutta (RK45)",
            }

    def matrix_operations(self, matrix_data: list, operation: str = "det") -> dict:
        """Perform numerical matrix operations."""
        steps = []
        try:
            A = np.array(matrix_data, dtype=float)
            steps.append(f"Matrix ({A.shape[0]}x{A.shape[1]}):")
            steps.append(str(A))

            if operation == "det":
                result = np.linalg.det(A)
                steps.append(f"Determinant = {result}")
                return {"answer": str(result), "steps": steps, "value": result}

            elif operation == "inverse":
                result = np.linalg.inv(A)
                steps.append(f"Inverse:\n{result}")
                return {"answer": str(result.tolist()), "steps": steps, "value": result.tolist()}

            elif operation == "eigenvalues":
                eigenvalues, eigenvectors = np.linalg.eig(A)
                steps.append(f"Eigenvalues: {eigenvalues}")
                steps.append(f"Eigenvectors:\n{eigenvectors}")
                return {
                    "answer": f"Eigenvalues: {eigenvalues.tolist()}",
                    "steps": steps,
                    "eigenvalues": eigenvalues.tolist(),
                    "eigenvectors": eigenvectors.tolist(),
                }

            elif operation == "rank":
                result = np.linalg.matrix_rank(A)
                steps.append(f"Rank = {result}")
                return {"answer": str(result), "steps": steps, "value": result}

            elif operation == "norm":
                result = np.linalg.norm(A)
                steps.append(f"Frobenius norm = {result}")
                return {"answer": str(result), "steps": steps, "value": result}

            elif operation == "svd":
                U, s, Vt = np.linalg.svd(A)
                steps.append(f"Singular values: {s}")
                return {
                    "answer": f"Singular values: {s.tolist()}",
                    "steps": steps,
                    "U": U.tolist(),
                    "s": s.tolist(),
                    "Vt": Vt.tolist(),
                }

            else:
                return {"answer": "Unknown operation", "steps": steps, "value": None}

        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps + [f"Error: {e}"], "value": None}

    def linear_regression(self, x_data: list, y_data: list) -> dict:
        """Perform linear regression."""
        steps = []
        try:
            x = np.array(x_data, dtype=float)
            y = np.array(y_data, dtype=float)
            steps.append(f"Data points: {len(x)}")

            coeffs = np.polyfit(x, y, 1)
            slope, intercept = coeffs[0], coeffs[1]

            y_pred = slope * x + intercept
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_squared = 1 - ss_res / ss_tot if ss_tot != 0 else 0

            steps.append(f"Slope: {slope:.6f}")
            steps.append(f"Intercept: {intercept:.6f}")
            steps.append(f"R-squared: {r_squared:.6f}")
            steps.append(f"Equation: y = {slope:.6f}x + {intercept:.6f}")

            return {
                "answer": f"y = {slope:.6f}x + {intercept:.6f} (R^2 = {r_squared:.6f})",
                "steps": steps,
                "slope": slope,
                "intercept": intercept,
                "r_squared": r_squared,
            }
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "slope": None, "intercept": None, "r_squared": None}
