import sympy
from sympy import (
    Matrix, Symbol, symbols, sympify, simplify, Rational,
    eye, zeros, ones, diag,
)
from typing import Any, Optional
import re
from app.utils.latex_utils import expr_to_latex, matrix_to_latex


class LinearAlgebraService:
    """Linear algebra operations using SymPy."""

    def parse_matrix(self, matrix_str: str) -> Matrix:
        """Parse a matrix from string representation."""
        # Handle [[1,2],[3,4]] format
        matrix_str = matrix_str.strip()
        if matrix_str.startswith("Matrix("):
            return sympify(matrix_str)

        # Try direct evaluation
        try:
            data = eval(matrix_str, {"__builtins__": {}})
            return Matrix(data)
        except Exception:
            pass

        # Try parsing [[a,b],[c,d]] format
        try:
            cleaned = matrix_str.replace(" ", "")
            # Extract rows
            row_pattern = r"\[([^\[\]]+)\]"
            rows = re.findall(row_pattern, cleaned)
            if rows:
                matrix_data = []
                for row in rows:
                    elements = [sympify(e.strip()) for e in row.split(",")]
                    matrix_data.append(elements)
                return Matrix(matrix_data)
        except Exception:
            pass

        # Try as space/comma separated values for augmented matrix
        try:
            lines = matrix_str.strip().split("\n")
            matrix_data = []
            for line in lines:
                elements = [sympify(e.strip()) for e in re.split(r"[,\s]+", line.strip()) if e.strip()]
                if elements:
                    matrix_data.append(elements)
            if matrix_data:
                return Matrix(matrix_data)
        except Exception:
            pass

        raise ValueError(f"Cannot parse matrix from: {matrix_str}")

    def determinant(self, matrix_str: str) -> dict:
        """Compute the determinant of a matrix."""
        steps = []
        try:
            M = self.parse_matrix(matrix_str)
            steps.append(f"Matrix:\n{matrix_to_latex(M)}")
            steps.append(f"Size: {M.rows}x{M.cols}")

            if M.rows != M.cols:
                return {"answer": "Error: Matrix must be square", "steps": steps, "latex": ""}

            det = M.det()
            det_simplified = simplify(det)
            steps.append(f"Determinant = {expr_to_latex(det_simplified)}")

            return {
                "answer": str(det_simplified),
                "steps": steps,
                "latex": expr_to_latex(det_simplified),
                "result": det_simplified,
            }
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": ""}

    def inverse(self, matrix_str: str) -> dict:
        """Compute the inverse of a matrix."""
        steps = []
        try:
            M = self.parse_matrix(matrix_str)
            steps.append(f"Matrix:\n{matrix_to_latex(M)}")

            if M.rows != M.cols:
                return {"answer": "Error: Matrix must be square", "steps": steps, "latex": ""}

            det = M.det()
            steps.append(f"Determinant = {expr_to_latex(det)}")

            if det == 0:
                return {"answer": "Matrix is singular (det = 0), no inverse exists", "steps": steps, "latex": ""}

            inv = M.inv()
            inv_simplified = inv.applyfunc(simplify)
            steps.append(f"Inverse:\n{matrix_to_latex(inv_simplified)}")

            return {
                "answer": str(inv_simplified.tolist()),
                "steps": steps,
                "latex": matrix_to_latex(inv_simplified),
                "result": inv_simplified,
            }
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": ""}

    def eigenvalues(self, matrix_str: str) -> dict:
        """Compute eigenvalues and eigenvectors."""
        steps = []
        try:
            M = self.parse_matrix(matrix_str)
            steps.append(f"Matrix:\n{matrix_to_latex(M)}")

            if M.rows != M.cols:
                return {"answer": "Error: Matrix must be square", "steps": steps, "latex": ""}

            # Eigenvalues with multiplicities
            eigenvals = M.eigenvals()
            steps.append("Eigenvalues (with multiplicities):")
            eigenval_strs = []
            for val, mult in eigenvals.items():
                val_s = simplify(val)
                eigenval_strs.append(f"  lambda = {expr_to_latex(val_s)} (multiplicity {mult})")
            steps.extend(eigenval_strs)

            # Eigenvectors
            eigenvects = M.eigenvects()
            steps.append("Eigenvectors:")
            for val, mult, vects in eigenvects:
                val_s = simplify(val)
                for v in vects:
                    steps.append(f"  lambda = {expr_to_latex(val_s)}: {matrix_to_latex(v)}")

            answer_parts = [f"lambda = {simplify(val)}" for val in eigenvals.keys()]
            answer = "Eigenvalues: " + ", ".join(answer_parts)

            return {
                "answer": answer,
                "steps": steps,
                "latex": answer,
                "eigenvalues": {str(k): v for k, v in eigenvals.items()},
            }
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": ""}

    def row_reduce(self, matrix_str: str) -> dict:
        """Row reduce a matrix to RREF."""
        steps = []
        try:
            M = self.parse_matrix(matrix_str)
            steps.append(f"Original matrix:\n{matrix_to_latex(M)}")

            rref, pivot_cols = M.rref()
            steps.append(f"Row Reduced Echelon Form (RREF):\n{matrix_to_latex(rref)}")
            steps.append(f"Pivot columns: {list(pivot_cols)}")

            return {
                "answer": str(rref.tolist()),
                "steps": steps,
                "latex": matrix_to_latex(rref),
                "rref": rref,
                "pivots": list(pivot_cols),
            }
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": ""}

    def rank(self, matrix_str: str) -> dict:
        """Compute the rank of a matrix."""
        steps = []
        try:
            M = self.parse_matrix(matrix_str)
            steps.append(f"Matrix:\n{matrix_to_latex(M)}")

            r = M.rank()
            steps.append(f"Rank = {r}")

            return {"answer": str(r), "steps": steps, "latex": str(r), "result": r}
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": ""}

    def nullspace(self, matrix_str: str) -> dict:
        """Compute the nullspace of a matrix."""
        steps = []
        try:
            M = self.parse_matrix(matrix_str)
            steps.append(f"Matrix:\n{matrix_to_latex(M)}")

            ns = M.nullspace()
            if not ns:
                steps.append("Nullspace is trivial (only the zero vector)")
                return {"answer": "Nullspace = {0}", "steps": steps, "latex": "\\{\\mathbf{0}\\}"}

            steps.append(f"Nullspace basis ({len(ns)} vector(s)):")
            for i, v in enumerate(ns):
                steps.append(f"  v{i + 1} = {matrix_to_latex(v)}")

            return {
                "answer": str([v.tolist() for v in ns]),
                "steps": steps,
                "latex": ", ".join(matrix_to_latex(v) for v in ns),
            }
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": ""}

    def transpose(self, matrix_str: str) -> dict:
        """Compute the transpose of a matrix."""
        steps = []
        try:
            M = self.parse_matrix(matrix_str)
            steps.append(f"Matrix:\n{matrix_to_latex(M)}")

            result = M.T
            steps.append(f"Transpose:\n{matrix_to_latex(result)}")

            return {
                "answer": str(result.tolist()),
                "steps": steps,
                "latex": matrix_to_latex(result),
                "result": result,
            }
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": ""}

    def multiply(self, matrix_a_str: str, matrix_b_str: str) -> dict:
        """Multiply two matrices."""
        steps = []
        try:
            A = self.parse_matrix(matrix_a_str)
            B = self.parse_matrix(matrix_b_str)
            steps.append(f"A ({A.rows}x{A.cols}):\n{matrix_to_latex(A)}")
            steps.append(f"B ({B.rows}x{B.cols}):\n{matrix_to_latex(B)}")

            if A.cols != B.rows:
                return {
                    "answer": f"Error: Cannot multiply {A.rows}x{A.cols} by {B.rows}x{B.cols}",
                    "steps": steps,
                    "latex": "",
                }

            result = A * B
            result = result.applyfunc(simplify)
            steps.append(f"A * B ({result.rows}x{result.cols}):\n{matrix_to_latex(result)}")

            return {
                "answer": str(result.tolist()),
                "steps": steps,
                "latex": matrix_to_latex(result),
                "result": result,
            }
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": ""}

    def solve_linear_system(self, matrix_str: str, b_str: str = None) -> dict:
        """Solve Ax = b using the augmented matrix or separate A and b."""
        steps = []
        try:
            M = self.parse_matrix(matrix_str)

            if b_str:
                b = self.parse_matrix(b_str)
                steps.append(f"Coefficient matrix A:\n{matrix_to_latex(M)}")
                steps.append(f"Right-hand side b:\n{matrix_to_latex(b)}")
                augmented = M.row_join(b)
            else:
                augmented = M
                steps.append(f"Augmented matrix:\n{matrix_to_latex(augmented)}")

            rref, pivots = augmented.rref()
            steps.append(f"RREF:\n{matrix_to_latex(rref)}")

            n_vars = augmented.cols - 1
            # Extract solution
            solution = []
            for i in range(min(rref.rows, n_vars)):
                if i in pivots and i < n_vars:
                    solution.append(rref[i, -1])
                else:
                    solution.append(Symbol(f"t{i}"))

            steps.append(f"Solution: {solution}")

            return {
                "answer": str(solution),
                "steps": steps,
                "latex": str(solution),
                "solution": solution,
            }
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": ""}

    def process(self, expression: str) -> dict:
        """Process a linear algebra expression/command."""
        steps = []
        expr_lower = expression.lower()
        try:
            # Detect operation from expression
            if "det" in expr_lower or "determinant" in expr_lower:
                matrix_part = self._extract_matrix_part(expression)
                return self.determinant(matrix_part)
            elif "inverse" in expr_lower or "inv(" in expr_lower:
                matrix_part = self._extract_matrix_part(expression)
                return self.inverse(matrix_part)
            elif "eigenval" in expr_lower or "eigenvec" in expr_lower:
                matrix_part = self._extract_matrix_part(expression)
                return self.eigenvalues(matrix_part)
            elif "rref" in expr_lower or "row reduce" in expr_lower or "row_reduce" in expr_lower:
                matrix_part = self._extract_matrix_part(expression)
                return self.row_reduce(matrix_part)
            elif "rank" in expr_lower:
                matrix_part = self._extract_matrix_part(expression)
                return self.rank(matrix_part)
            elif "nullspace" in expr_lower or "null space" in expr_lower:
                matrix_part = self._extract_matrix_part(expression)
                return self.nullspace(matrix_part)
            elif "transpose" in expr_lower:
                matrix_part = self._extract_matrix_part(expression)
                return self.transpose(matrix_part)
            else:
                # Default: try to parse as matrix and compute common properties
                M = self.parse_matrix(expression)
                steps.append(f"Matrix ({M.rows}x{M.cols}):\n{matrix_to_latex(M)}")

                if M.rows == M.cols:
                    det = simplify(M.det())
                    steps.append(f"Determinant: {expr_to_latex(det)}")
                    steps.append(f"Rank: {M.rank()}")

                    eigenvals = M.eigenvals()
                    ev_strs = [f"{simplify(k)} (mult. {v})" for k, v in eigenvals.items()]
                    steps.append(f"Eigenvalues: {', '.join(ev_strs)}")

                    return {
                        "answer": f"det = {det}, rank = {M.rank()}",
                        "steps": steps,
                        "latex": matrix_to_latex(M),
                    }
                else:
                    r = M.rank()
                    steps.append(f"Rank: {r}")
                    rref_m, pivots = M.rref()
                    steps.append(f"RREF:\n{matrix_to_latex(rref_m)}")
                    return {
                        "answer": f"Rank = {r}",
                        "steps": steps,
                        "latex": matrix_to_latex(M),
                    }
        except Exception as e:
            return {"answer": f"Error: {e}", "steps": steps, "latex": ""}

    def _extract_matrix_part(self, expression: str) -> str:
        """Extract the matrix portion from an expression."""
        # Find [[...]] pattern
        match = re.search(r"\[[\s\S]*\]", expression)
        if match:
            return match.group(0)
        # Find Matrix(...) pattern
        match = re.search(r"Matrix\s*\([\s\S]*\)", expression)
        if match:
            return match.group(0)
        # Remove command words and return rest
        for word in ["det", "determinant", "inverse", "inv", "eigenvalues", "eigenvectors",
                      "rref", "row_reduce", "rank", "nullspace", "transpose", "of"]:
            expression = re.sub(rf"\b{word}\b", "", expression, flags=re.IGNORECASE)
        return expression.strip()
