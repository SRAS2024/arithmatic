"""Graph generation service using matplotlib and sympy."""

import base64
import io
import logging
import re
from typing import Any, Optional

logger = logging.getLogger(__name__)

try:
    import matplotlib
    matplotlib.use("Agg")  # non-interactive backend
    import matplotlib.pyplot as plt
    _MPL_AVAILABLE = True
except ImportError:
    _MPL_AVAILABLE = False

try:
    import numpy as np
    _NP_AVAILABLE = True
except ImportError:
    _NP_AVAILABLE = False


class GraphService:
    """Generate graphs/charts and return them as base64-encoded PNGs."""

    # Default styling
    _COLORS = [
        "#2563eb", "#dc2626", "#16a34a", "#9333ea",
        "#ea580c", "#0891b2", "#4f46e5", "#be123c",
    ]

    def generate_graph(
        self,
        expression: str,
        graph_type: str = "function",
        options: Optional[dict] = None,
    ) -> dict:
        """Generate a graph and return the result.

        Args:
            expression: The expression or data description.
            graph_type: One of function, bar, pie, scatter, histogram,
                        line, parametric, polar.
            options: Extra options (x_range, y_range, title, data, etc.).

        Returns:
            dict compatible with GraphResponse.
        """
        if not _MPL_AVAILABLE:
            return {"image_base64": "", "error": "matplotlib is not installed"}
        if not _NP_AVAILABLE:
            return {"image_base64": "", "error": "numpy is not installed"}

        opts = options or {}

        dispatch = {
            "function": self._plot_function,
            "bar": self._plot_bar,
            "pie": self._plot_pie,
            "scatter": self._plot_scatter,
            "histogram": self._plot_histogram,
            "line": self._plot_line,
            "parametric": self._plot_parametric,
            "polar": self._plot_polar,
        }

        handler = dispatch.get(graph_type, self._plot_function)

        try:
            fig = handler(expression, opts)
            b64, w, h = self._fig_to_base64(fig)
            return {"image_base64": b64, "width": w, "height": h}
        except Exception as exc:
            logger.error("Graph generation failed: %s", exc)
            return {"image_base64": "", "error": str(exc)}

    # ------------------------------------------------------------------
    # Plot handlers
    # ------------------------------------------------------------------

    def _plot_function(self, expression: str, opts: dict) -> "plt.Figure":
        """Plot y = f(x) for a symbolic expression."""
        from sympy import Symbol, lambdify
        from sympy.parsing.sympy_parser import (
            parse_expr,
            standard_transformations,
            implicit_multiplication_application,
            convert_xor,
        )

        transformations = standard_transformations + (
            implicit_multiplication_application,
            convert_xor,
        )

        x = Symbol("x")
        expr = parse_expr(expression, local_dict={"x": x}, transformations=transformations)

        x_min, x_max = opts.get("x_range", (-10, 10))
        x_vals = np.linspace(float(x_min), float(x_max), 500)

        f = lambdify(x, expr, modules=["numpy"])
        y_vals = np.array([self._safe_eval(f, xi) for xi in x_vals])

        fig, ax = self._new_figure(opts)
        ax.plot(x_vals, y_vals, color=self._COLORS[0], linewidth=2)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        title = opts.get("title", f"y = {expression}")
        ax.set_title(title)
        ax.axhline(0, color="gray", linewidth=0.5)
        ax.axvline(0, color="gray", linewidth=0.5)
        ax.grid(True, alpha=0.3)

        if "y_range" in opts:
            ax.set_ylim(opts["y_range"])

        fig.tight_layout()
        return fig

    def _plot_bar(self, expression: str, opts: dict) -> "plt.Figure":
        x_data = opts.get("x", opts.get("labels", []))
        y_data = opts.get("y", opts.get("values", []))
        if not x_data or not y_data:
            x_data, y_data = self._parse_data_expression(expression)
        fig, ax = self._new_figure(opts)
        colors = self._COLORS[: len(x_data)]
        ax.bar([str(v) for v in x_data], [float(v) for v in y_data], color=colors)
        ax.set_title(opts.get("title", "Bar Chart"))
        ax.set_ylabel(opts.get("ylabel", "Value"))
        fig.tight_layout()
        return fig

    def _plot_pie(self, expression: str, opts: dict) -> "plt.Figure":
        labels = opts.get("labels", [])
        values = opts.get("values", [])
        if not labels or not values:
            labels, values = self._parse_data_expression(expression)
        fig, ax = self._new_figure(opts)
        colors = self._COLORS[: len(labels)]
        ax.pie(
            [float(v) for v in values],
            labels=[str(l) for l in labels],
            colors=colors,
            autopct="%1.1f%%",
            startangle=90,
        )
        ax.set_title(opts.get("title", "Pie Chart"))
        fig.tight_layout()
        return fig

    def _plot_scatter(self, expression: str, opts: dict) -> "plt.Figure":
        x_data = opts.get("x", [])
        y_data = opts.get("y", [])
        if not x_data or not y_data:
            x_data, y_data = self._parse_xy_expression(expression)
        fig, ax = self._new_figure(opts)
        ax.scatter(
            [float(v) for v in x_data],
            [float(v) for v in y_data],
            color=self._COLORS[0],
            alpha=0.7,
            s=50,
        )
        ax.set_xlabel(opts.get("xlabel", "x"))
        ax.set_ylabel(opts.get("ylabel", "y"))
        ax.set_title(opts.get("title", "Scatter Plot"))
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        return fig

    def _plot_histogram(self, expression: str, opts: dict) -> "plt.Figure":
        data = opts.get("data", [])
        if not data:
            data = self._parse_list_expression(expression)
        fig, ax = self._new_figure(opts)
        bins = opts.get("bins", "auto")
        ax.hist(
            [float(v) for v in data],
            bins=bins,
            color=self._COLORS[0],
            edgecolor="white",
            alpha=0.8,
        )
        ax.set_xlabel(opts.get("xlabel", "Value"))
        ax.set_ylabel(opts.get("ylabel", "Frequency"))
        ax.set_title(opts.get("title", "Histogram"))
        fig.tight_layout()
        return fig

    def _plot_line(self, expression: str, opts: dict) -> "plt.Figure":
        x_data = opts.get("x", [])
        y_data = opts.get("y", [])
        if not x_data or not y_data:
            x_data, y_data = self._parse_xy_expression(expression)
        fig, ax = self._new_figure(opts)
        ax.plot(
            [float(v) for v in x_data],
            [float(v) for v in y_data],
            color=self._COLORS[0],
            linewidth=2,
            marker="o",
            markersize=4,
        )
        ax.set_xlabel(opts.get("xlabel", "x"))
        ax.set_ylabel(opts.get("ylabel", "y"))
        ax.set_title(opts.get("title", "Line Chart"))
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        return fig

    def _plot_parametric(self, expression: str, opts: dict) -> "plt.Figure":
        from sympy import Symbol, lambdify
        from sympy.parsing.sympy_parser import (
            parse_expr,
            standard_transformations,
            implicit_multiplication_application,
            convert_xor,
        )

        transformations = standard_transformations + (
            implicit_multiplication_application,
            convert_xor,
        )

        t = Symbol("t")
        x_expr_str = opts.get("x_expr", expression)
        y_expr_str = opts.get("y_expr", f"sin({expression})")

        x_expr = parse_expr(x_expr_str, local_dict={"t": t}, transformations=transformations)
        y_expr = parse_expr(y_expr_str, local_dict={"t": t}, transformations=transformations)

        t_min, t_max = opts.get("t_range", (0, 2 * 3.14159265))
        t_vals = np.linspace(float(t_min), float(t_max), 500)

        fx = lambdify(t, x_expr, modules=["numpy"])
        fy = lambdify(t, y_expr, modules=["numpy"])

        x_vals = np.array([self._safe_eval(fx, tv) for tv in t_vals])
        y_vals = np.array([self._safe_eval(fy, tv) for tv in t_vals])

        fig, ax = self._new_figure(opts)
        ax.plot(x_vals, y_vals, color=self._COLORS[0], linewidth=2)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_title(opts.get("title", "Parametric Plot"))
        ax.set_aspect("equal", adjustable="datalim")
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        return fig

    def _plot_polar(self, expression: str, opts: dict) -> "plt.Figure":
        from sympy import Symbol, lambdify
        from sympy.parsing.sympy_parser import (
            parse_expr,
            standard_transformations,
            implicit_multiplication_application,
            convert_xor,
        )

        transformations = standard_transformations + (
            implicit_multiplication_application,
            convert_xor,
        )

        theta = Symbol("theta")
        # Allow "t" as alias for theta in the expression
        expr = parse_expr(
            expression,
            local_dict={"theta": theta, "t": theta},
            transformations=transformations,
        )

        t_min, t_max = opts.get("t_range", (0, 2 * 3.14159265))
        t_vals = np.linspace(float(t_min), float(t_max), 500)

        f = lambdify(theta, expr, modules=["numpy"])
        r_vals = np.array([self._safe_eval(f, tv) for tv in t_vals])

        fig = plt.figure(figsize=(7, 7), dpi=150)
        ax = fig.add_subplot(111, projection="polar")
        ax.plot(t_vals, r_vals, color=self._COLORS[0], linewidth=2)
        ax.set_title(opts.get("title", "Polar Plot"), va="bottom")
        fig.tight_layout()
        return fig

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def _new_figure(self, opts: dict):
        """Create a new matplotlib figure + axes with standard styling."""
        w = opts.get("width", 800) / 100
        h = opts.get("height", 600) / 100
        dpi = opts.get("dpi", 150)
        fig, ax = plt.subplots(figsize=(w, h), dpi=dpi)
        return fig, ax

    @staticmethod
    def _safe_eval(func, val):
        """Evaluate func(val) returning NaN on failure."""
        try:
            result = float(func(val))
            if abs(result) > 1e15:
                return float("nan")
            return result
        except Exception:
            return float("nan")

    @staticmethod
    def _fig_to_base64(fig) -> tuple:
        """Render figure to PNG and return (base64_str, width_px, height_px)."""
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        data = buf.getvalue()
        b64 = base64.b64encode(data).decode("ascii")

        # Read dimensions from the PNG header (bytes 16-23)
        width = int.from_bytes(data[16:20], "big")
        height = int.from_bytes(data[20:24], "big")
        return b64, width, height

    @staticmethod
    def _parse_data_expression(expression: str):
        """Parse 'label1:val1, label2:val2, ...' into (labels, values)."""
        labels, values = [], []
        for part in expression.split(","):
            part = part.strip()
            if ":" in part:
                l, v = part.split(":", 1)
                labels.append(l.strip())
                try:
                    values.append(float(v.strip()))
                except ValueError:
                    values.append(0)
            else:
                labels.append(part)
                try:
                    values.append(float(part))
                except ValueError:
                    values.append(0)
        return labels, values

    @staticmethod
    def _parse_xy_expression(expression: str):
        """Parse paired data from expression, e.g. '(1,2),(3,4),...'."""
        import re as _re
        pairs = _re.findall(r"\(\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)\s*\)", expression)
        if pairs:
            x = [float(p[0]) for p in pairs]
            y = [float(p[1]) for p in pairs]
            return x, y
        # Fallback: comma separated -> split in half
        nums = _re.findall(r"-?[\d.]+", expression)
        nums = [float(n) for n in nums]
        half = len(nums) // 2
        return nums[:half], nums[half : half * 2]

    @staticmethod
    def _parse_list_expression(expression: str):
        """Extract a flat list of numbers from the expression."""
        import re as _re
        nums = _re.findall(r"-?[\d.]+", expression)
        return [float(n) for n in nums]
