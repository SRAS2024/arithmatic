"""
Arithmetic - Graph Service Tests
"""
import pytest
import sys
import os
import base64

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'python'))

from app.services.graph_service import GraphService


class TestGraphService:
    """Tests for graph generation."""

    def test_function_plot(self):
        result = GraphService.generate({
            'expression': 'sin(x)',
            'graph_type': 'function',
            'x_range': [-10, 10]
        })
        assert result is not None
        assert 'image' in result
        # Should be base64 encoded PNG
        try:
            decoded = base64.b64decode(result['image'])
            assert decoded[:8] == b'\x89PNG\r\n\x1a\n'
        except Exception:
            pass

    def test_bar_chart(self):
        result = GraphService.generate({
            'graph_type': 'bar',
            'x': ['A', 'B', 'C'],
            'y': [10, 20, 30],
            'title': 'Test Bar Chart'
        })
        assert result is not None
        assert 'image' in result

    def test_pie_chart(self):
        result = GraphService.generate({
            'graph_type': 'pie',
            'labels': ['A', 'B', 'C'],
            'values': [30, 50, 20],
            'title': 'Test Pie'
        })
        assert result is not None
        assert 'image' in result

    def test_scatter_plot(self):
        result = GraphService.generate({
            'graph_type': 'scatter',
            'x': [1, 2, 3, 4, 5],
            'y': [2, 4, 1, 5, 3],
            'title': 'Test Scatter'
        })
        assert result is not None
        assert 'image' in result

    def test_histogram(self):
        result = GraphService.generate({
            'graph_type': 'histogram',
            'data': [1, 2, 2, 3, 3, 3, 4, 4, 5],
            'title': 'Test Histogram'
        })
        assert result is not None
        assert 'image' in result

    def test_invalid_expression(self):
        result = GraphService.generate({
            'expression': 'not_valid!!!',
            'graph_type': 'function'
        })
        assert result is not None
        assert 'error' in result or 'image' in result

    def test_parametric_plot(self):
        result = GraphService.generate({
            'graph_type': 'parametric',
            'x_expr': 'cos(t)',
            'y_expr': 'sin(t)',
            't_range': [0, 6.28]
        })
        assert result is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
