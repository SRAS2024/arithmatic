"""
Arithmetic - Verification Service Tests
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'python'))

from app.services.verification_service import VerificationService


class TestVerificationService:
    """Tests for solution verification."""

    def test_verify_correct_solution(self):
        result = VerificationService.verify(
            expression="2*x + 5 = 17",
            solution={"x": 6},
            problem_type="algebra"
        )
        assert result['verified'] is True

    def test_verify_incorrect_solution(self):
        result = VerificationService.verify(
            expression="2*x + 5 = 17",
            solution={"x": 5},
            problem_type="algebra"
        )
        assert result['verified'] is False

    def test_verify_arithmetic(self):
        result = VerificationService.verify(
            expression="2 + 3",
            solution={"result": 5},
            problem_type="arithmetic"
        )
        assert result['verified'] is True

    def test_confidence_level(self):
        result = VerificationService.verify(
            expression="x**2 = 4",
            solution={"x": [2, -2]},
            problem_type="algebra"
        )
        assert 'confidence' in result
        assert result['confidence'] in ['high', 'medium', 'low']

    def test_handle_unverifiable(self):
        result = VerificationService.verify(
            expression="some complex thing",
            solution={"result": "unknown"},
            problem_type="unknown"
        )
        assert 'confidence' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
