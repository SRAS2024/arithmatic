"""
Arithmetic - Symbolic Service Tests
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'python'))

from app.services.symbolic_service import SymbolicService


class TestSymbolicService:
    """Tests for the symbolic math solving service."""

    def test_solve_linear_equation(self):
        result = SymbolicService.solve("2*x + 5 = 17")
        assert result is not None
        assert 'solution' in result
        assert result['solution'] is not None

    def test_solve_quadratic_equation(self):
        result = SymbolicService.solve("x**2 - 5*x + 6 = 0")
        assert result is not None
        assert 'solution' in result

    def test_simplify_expression(self):
        result = SymbolicService.simplify("(x**2 - 4)/(x - 2)")
        assert result is not None

    def test_factor_expression(self):
        result = SymbolicService.factor("x**2 - 5*x + 6")
        assert result is not None

    def test_expand_expression(self):
        result = SymbolicService.expand("(x + 1)*(x + 2)")
        assert result is not None

    def test_solve_system(self):
        result = SymbolicService.solve_system(["x + y = 5", "2*x - y = 1"])
        assert result is not None

    def test_partial_fractions(self):
        result = SymbolicService.partial_fractions("1/(x**2 - 1)")
        assert result is not None

    def test_arithmetic(self):
        result = SymbolicService.evaluate("2 + 3 * 4")
        assert result is not None
        assert result['result'] == 14

    def test_invalid_input(self):
        result = SymbolicService.solve("not a math problem xyz!!!")
        assert 'error' in result or result.get('solution') is None


class TestSymbolicSteps:
    """Tests for step-by-step solution generation."""

    def test_steps_included_for_equation(self):
        result = SymbolicService.solve("3*x + 9 = 0")
        assert 'steps' in result
        assert len(result['steps']) > 0

    def test_latex_output(self):
        result = SymbolicService.solve("x**2 = 4")
        assert 'latex' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
