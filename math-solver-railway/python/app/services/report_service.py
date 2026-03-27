"""PDF report generation service using ReportLab."""

import base64
import io
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        Image as RLImage,
        HRFlowable,
    )
    _RL_AVAILABLE = True
except ImportError:
    _RL_AVAILABLE = False


class ReportService:
    """Generate professional PDF reports for math solutions."""

    def generate_pdf(self, data: dict) -> bytes:
        """Generate a PDF report and return the raw bytes.

        Args:
            data: dict with keys problem, answer, steps, latex,
                  graph_base64, source_type, timestamp.

        Returns:
            Raw PDF bytes.
        """
        return self._build_pdf(
            problem=data.get("problem", ""),
            answer=data.get("answer", ""),
            steps=data.get("steps", []),
            latex=data.get("latex"),
            graph_base64=data.get("graph_base64"),
            title=data.get("title", "Math Solution Report"),
            include_timestamp=data.get("include_timestamp", True),
        )

    def generate_report(
        self,
        problem: str,
        answer: str,
        steps: Optional[list] = None,
        latex: Optional[str] = None,
        graph_base64: Optional[str] = None,
        title: str = "Math Solution Report",
        include_timestamp: bool = True,
    ) -> dict:
        """Generate a PDF report and return dict compatible with ReportResponse.

        This is the entry point used by the /report route.
        """
        if not _RL_AVAILABLE:
            return {"pdf_base64": "", "filename": "report.pdf", "error": "reportlab is not installed"}

        try:
            pdf_bytes = self._build_pdf(
                problem=problem,
                answer=answer,
                steps=steps or [],
                latex=latex,
                graph_base64=graph_base64,
                title=title,
                include_timestamp=include_timestamp,
            )
            pdf_b64 = base64.b64encode(pdf_bytes).decode("ascii")
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"math_report_{timestamp_str}.pdf"
            return {"pdf_base64": pdf_b64, "filename": filename}
        except Exception as exc:
            logger.error("Report generation failed: %s", exc)
            return {"pdf_base64": "", "filename": "report.pdf", "error": str(exc)}

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _build_pdf(
        self,
        problem: str,
        answer: str,
        steps: list,
        latex: Optional[str],
        graph_base64: Optional[str],
        title: str,
        include_timestamp: bool,
    ) -> bytes:
        if not _RL_AVAILABLE:
            raise RuntimeError("reportlab is not installed")

        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=letter,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            rightMargin=0.75 * inch,
        )

        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            fontSize=20,
            spaceAfter=6,
            textColor=colors.HexColor("#1e3a5f"),
        )
        heading_style = ParagraphStyle(
            "ReportHeading",
            parent=styles["Heading2"],
            fontSize=14,
            spaceBefore=12,
            spaceAfter=6,
            textColor=colors.HexColor("#2563eb"),
        )
        body_style = ParagraphStyle(
            "ReportBody",
            parent=styles["BodyText"],
            fontSize=11,
            leading=16,
        )
        math_style = ParagraphStyle(
            "ReportMath",
            parent=styles["BodyText"],
            fontSize=12,
            leading=18,
            fontName="Courier",
            leftIndent=20,
            backColor=colors.HexColor("#f3f4f6"),
            borderPadding=8,
            spaceBefore=4,
            spaceAfter=4,
        )
        step_style = ParagraphStyle(
            "ReportStep",
            parent=styles["BodyText"],
            fontSize=11,
            leading=15,
            leftIndent=20,
            bulletIndent=10,
        )
        answer_style = ParagraphStyle(
            "ReportAnswer",
            parent=styles["BodyText"],
            fontSize=13,
            leading=18,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#16a34a"),
            spaceBefore=6,
            spaceAfter=6,
        )

        elements = []

        # --- Header ---
        elements.append(Paragraph(self._escape(title), title_style))
        if include_timestamp:
            ts = datetime.now().strftime("%B %d, %Y at %H:%M")
            elements.append(Paragraph(f"Generated: {ts}", body_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1")))
        elements.append(Spacer(1, 12))

        # --- Problem ---
        elements.append(Paragraph("Problem", heading_style))
        elements.append(Paragraph(self._escape(problem), body_style))
        elements.append(Spacer(1, 8))

        # --- Solution Steps ---
        if steps:
            elements.append(Paragraph("Solution Steps", heading_style))
            for i, step in enumerate(steps, 1):
                text = f"<b>Step {i}:</b> {self._escape(step)}"
                elements.append(Paragraph(text, step_style))
            elements.append(Spacer(1, 8))

        # --- Answer ---
        elements.append(Paragraph("Answer", heading_style))
        elements.append(Paragraph(self._escape(answer), answer_style))
        elements.append(Spacer(1, 8))

        # --- LaTeX ---
        if latex:
            elements.append(Paragraph("Mathematical Notation", heading_style))
            elements.append(Paragraph(self._escape(latex), math_style))
            elements.append(Spacer(1, 8))

        # --- Graph ---
        if graph_base64:
            try:
                graph_bytes = base64.b64decode(graph_base64)
                img_buf = io.BytesIO(graph_bytes)
                elements.append(Paragraph("Graph", heading_style))
                rl_img = RLImage(img_buf, width=5 * inch, height=3.75 * inch)
                elements.append(rl_img)
                elements.append(Spacer(1, 8))
            except Exception as exc:
                logger.warning("Could not embed graph in report: %s", exc)

        # --- Footer line ---
        elements.append(Spacer(1, 20))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1")))
        footer_style = ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontSize=8,
            textColor=colors.gray,
        )
        elements.append(Paragraph("Generated by Arithmetic Math Solver", footer_style))

        doc.build(elements)
        return buf.getvalue()

    @staticmethod
    def _escape(text: str) -> str:
        """Escape XML-sensitive characters for ReportLab Paragraph."""
        if not text:
            return ""
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        return text
