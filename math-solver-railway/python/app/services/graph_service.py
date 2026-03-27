"""
Graph Service - Generate mathematical plots and charts using matplotlib.
"""
import io
import base64
import numpy as np

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Set global style
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
rcParams['font.size'] = 11
rcParams['axes.linewidth'] = 0.8
rcParams['grid.alpha'] = 0.3


class GraphService:
    """Generate various types of mathematical plots and charts."""

    COLORS = ['#5e6ad2', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#6366f1']

    @staticmethod
    def generate(spec: dict) -> dict:
        """Generate a graph from specification.

        Args:
            spec: Dict with graph_type, expression/data, options

        Returns:
            Dict with 'image' (base64 PNG) or 'error'
        """
        graph_type = spec.get('graph_type', 'function')

        try:
            if graph_type == 'function':
                return GraphService._function_plot(spec)
            elif graph_type == 'bar':
                return GraphService._bar_chart(spec)
            elif graph_type == 'pie':
                return GraphService._pie_chart(spec)
            elif graph_type == 'scatter':
                return GraphService._scatter_plot(spec)
            elif graph_type == 'histogram':
                return GraphService._histogram(spec)
            elif graph_type == 'line':
                return GraphService._line_chart(spec)
            elif graph_type == 'parametric':
                return GraphService._parametric_plot(spec)
            elif graph_type == 'polar':
                return GraphService._polar_plot(spec)
            else:
                # Default to function plot
                return GraphService._function_plot(spec)
        except Exception as e:
            return {'error': f'Graph generation failed: {str(e)}'}

    @staticmethod
    def _function_plot(spec: dict) -> dict:
        """Plot y = f(x)."""
        expression = spec.get('expression', '')
        x_range = spec.get('x_range', [-10, 10])
        title = spec.get('title', f'y = {expression}')

        import sympy
        from sympy import Symbol, lambdify
        from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

        x = Symbol('x')
        transformations = standard_transformations + (implicit_multiplication_application,)

        try:
            expr = parse_expr(expression, local_dict={'x': x, 'e': sympy.E, 'pi': sympy.pi},
                            transformations=transformations)
        except Exception as e:
            return {'error': f'Failed to parse expression: {e}'}

        f = lambdify(x, expr, modules=['numpy'])

        x_vals = np.linspace(float(x_range[0]), float(x_range[1]), 1000)

        try:
            y_vals = f(x_vals)
            if isinstance(y_vals, (int, float)):
                y_vals = np.full_like(x_vals, y_vals)
            y_vals = np.real(np.array(y_vals, dtype=complex))
            # Remove extreme values for better visualization
            y_vals = np.where(np.abs(y_vals) > 1e6, np.nan, y_vals)
        except Exception as e:
            return {'error': f'Failed to evaluate expression: {e}'}

        fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
        ax.plot(x_vals, y_vals, color=GraphService.COLORS[0], linewidth=2.2, label=f'y = {expression}')
        ax.axhline(y=0, color='#888', linewidth=0.5, alpha=0.5)
        ax.axvline(x=0, color='#888', linewidth=0.5, alpha=0.5)
        ax.set_xlabel('x', fontsize=12)
        ax.set_ylabel('y', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.grid(True, alpha=0.2)
        ax.legend(fontsize=10)
        fig.tight_layout()

        return GraphService._fig_to_base64(fig)

    @staticmethod
    def _bar_chart(spec: dict) -> dict:
        """Generate a bar chart."""
        x = spec.get('x', [])
        y = spec.get('y', [])
        title = spec.get('title', 'Bar Chart')
        x_title = spec.get('x_title', '')
        y_title = spec.get('y_title', '')

        if not x or not y:
            return {'error': 'Bar chart requires x and y data'}

        fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
        colors = [GraphService.COLORS[i % len(GraphService.COLORS)] for i in range(len(x))]
        bars = ax.bar(x, y, color=colors, width=0.6, edgecolor='white', linewidth=0.5)

        # Add value labels on bars
        for bar, val in zip(bars, y):
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(y)*0.01,
                    f'{val}', ha='center', va='bottom', fontsize=10, fontweight='500')

        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        if x_title:
            ax.set_xlabel(x_title, fontsize=12)
        if y_title:
            ax.set_ylabel(y_title, fontsize=12)
        ax.grid(axis='y', alpha=0.2)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        fig.tight_layout()

        return GraphService._fig_to_base64(fig)

    @staticmethod
    def _pie_chart(spec: dict) -> dict:
        """Generate a pie chart."""
        labels = spec.get('labels', [])
        values = spec.get('values', [])
        title = spec.get('title', 'Pie Chart')

        if not labels or not values:
            return {'error': 'Pie chart requires labels and values'}

        fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
        colors = [GraphService.COLORS[i % len(GraphService.COLORS)] for i in range(len(labels))]

        wedges, texts, autotexts = ax.pie(
            values, labels=labels, colors=colors, autopct='%1.1f%%',
            startangle=90, pctdistance=0.8,
            wedgeprops=dict(width=0.65, edgecolor='white', linewidth=2)
        )

        for text in texts:
            text.set_fontsize(11)
        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')

        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        fig.tight_layout()

        return GraphService._fig_to_base64(fig)

    @staticmethod
    def _scatter_plot(spec: dict) -> dict:
        """Generate a scatter plot."""
        x = spec.get('x', [])
        y = spec.get('y', [])
        title = spec.get('title', 'Scatter Plot')

        if not x or not y:
            return {'error': 'Scatter plot requires x and y data'}

        fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
        ax.scatter(x, y, color=GraphService.COLORS[0], s=60, alpha=0.7, edgecolors='white', linewidth=0.5)
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel(spec.get('x_title', 'x'), fontsize=12)
        ax.set_ylabel(spec.get('y_title', 'y'), fontsize=12)
        ax.grid(True, alpha=0.2)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        fig.tight_layout()

        return GraphService._fig_to_base64(fig)

    @staticmethod
    def _histogram(spec: dict) -> dict:
        """Generate a histogram."""
        data = spec.get('data', [])
        title = spec.get('title', 'Histogram')
        bins = spec.get('bins', 'auto')

        if not data:
            return {'error': 'Histogram requires data'}

        fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
        ax.hist(data, bins=bins, color=GraphService.COLORS[0], alpha=0.8,
                edgecolor='white', linewidth=0.8)
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel(spec.get('x_title', 'Value'), fontsize=12)
        ax.set_ylabel(spec.get('y_title', 'Frequency'), fontsize=12)
        ax.grid(axis='y', alpha=0.2)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        fig.tight_layout()

        return GraphService._fig_to_base64(fig)

    @staticmethod
    def _line_chart(spec: dict) -> dict:
        """Generate a line chart."""
        x = spec.get('x', [])
        y = spec.get('y', [])
        title = spec.get('title', 'Line Chart')

        if not x or not y:
            return {'error': 'Line chart requires x and y data'}

        fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
        ax.plot(x, y, color=GraphService.COLORS[0], linewidth=2, marker='o',
                markersize=5, markerfacecolor='white', markeredgecolor=GraphService.COLORS[0],
                markeredgewidth=1.5)
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel(spec.get('x_title', ''), fontsize=12)
        ax.set_ylabel(spec.get('y_title', ''), fontsize=12)
        ax.grid(True, alpha=0.2)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        fig.tight_layout()

        return GraphService._fig_to_base64(fig)

    @staticmethod
    def _parametric_plot(spec: dict) -> dict:
        """Generate a parametric plot."""
        x_expr = spec.get('x_expr', 'cos(t)')
        y_expr = spec.get('y_expr', 'sin(t)')
        t_range = spec.get('t_range', [0, 2 * np.pi])
        title = spec.get('title', f'Parametric: x={x_expr}, y={y_expr}')

        import sympy
        from sympy import Symbol, lambdify
        from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

        t = Symbol('t')
        transformations = standard_transformations + (implicit_multiplication_application,)
        local = {'t': t, 'e': sympy.E, 'pi': sympy.pi}

        try:
            x_sym = parse_expr(x_expr, local_dict=local, transformations=transformations)
            y_sym = parse_expr(y_expr, local_dict=local, transformations=transformations)
        except Exception as e:
            return {'error': f'Failed to parse parametric expressions: {e}'}

        fx = lambdify(t, x_sym, modules=['numpy'])
        fy = lambdify(t, y_sym, modules=['numpy'])

        t_vals = np.linspace(float(t_range[0]), float(t_range[1]), 1000)
        x_vals = fx(t_vals)
        y_vals = fy(t_vals)

        fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
        ax.plot(x_vals, y_vals, color=GraphService.COLORS[0], linewidth=2)
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('x', fontsize=12)
        ax.set_ylabel('y', fontsize=12)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.2)
        fig.tight_layout()

        return GraphService._fig_to_base64(fig)

    @staticmethod
    def _polar_plot(spec: dict) -> dict:
        """Generate a polar plot."""
        expression = spec.get('expression', 'sin(3*theta)')
        title = spec.get('title', f'r = {expression}')

        import sympy
        from sympy import Symbol, lambdify
        from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

        theta = Symbol('theta')
        transformations = standard_transformations + (implicit_multiplication_application,)
        local = {'theta': theta, 'e': sympy.E, 'pi': sympy.pi}

        try:
            expr = parse_expr(expression, local_dict=local, transformations=transformations)
        except Exception as e:
            return {'error': f'Failed to parse polar expression: {e}'}

        f = lambdify(theta, expr, modules=['numpy'])
        theta_vals = np.linspace(0, 2 * np.pi, 1000)
        r_vals = f(theta_vals)

        fig, ax = plt.subplots(figsize=(8, 8), dpi=150, subplot_kw=dict(projection='polar'))
        ax.plot(theta_vals, r_vals, color=GraphService.COLORS[0], linewidth=2)
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        fig.tight_layout()

        return GraphService._fig_to_base64(fig)

    @staticmethod
    def _fig_to_base64(fig) -> dict:
        """Convert matplotlib figure to base64 PNG."""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close(fig)
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode('utf-8')
        return {'image': b64}
