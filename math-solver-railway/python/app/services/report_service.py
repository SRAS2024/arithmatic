"""
Report Service - Generate PDF and HTML solution reports.
"""
import io
import base64
from datetime import datetime
from typing import Optional


class ReportService:
    """Generate professional solution reports in PDF and HTML formats."""

    @staticmethod
    def generate_pdf(data: dict) -> bytes:
        """Generate a PDF solution report.

        Args:
            data: Dict with problem, answer, steps, latex, graph_base64, source_type, timestamp

        Returns:
            PDF file bytes
        """
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch, mm
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
        except ImportError:
            raise RuntimeError('reportlab not installed')

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                               topMargin=30*mm, bottomMargin=25*mm,
                               leftMargin=25*mm, rightMargin=25*mm)

        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'ReportTitle', parent=styles['Title'],
            fontSize=24, textColor=colors.HexColor('#5e6ad2'),
            spaceAfter=6, alignment=TA_CENTER
        )
        subtitle_style = ParagraphStyle(
            'ReportSubtitle', parent=styles['Normal'],
            fontSize=10, textColor=colors.HexColor('#6b7280'),
            alignment=TA_CENTER, spaceAfter=20
        )
        heading_style = ParagraphStyle(
            'SectionHeading', parent=styles['Heading2'],
            fontSize=14, textColor=colors.HexColor('#5e6ad2'),
            spaceBefore=16, spaceAfter=8,
            borderWidth=0, borderPadding=0
        )
        body_style = ParagraphStyle(
            'ReportBody', parent=styles['Normal'],
            fontSize=11, leading=16, spaceAfter=8,
            textColor=colors.HexColor('#374151')
        )
        answer_style = ParagraphStyle(
            'AnswerStyle', parent=styles['Normal'],
            fontSize=16, leading=22, alignment=TA_CENTER,
            textColor=colors.HexColor('#065f46'),
            backColor=colors.HexColor('#ecfdf5'),
            borderWidth=1, borderColor=colors.HexColor('#86efac'),
            borderPadding=12, borderRadius=8,
            spaceAfter=12
        )
        step_style = ParagraphStyle(
            'StepStyle', parent=styles['Normal'],
            fontSize=10, leading=15, leftIndent=20,
            textColor=colors.HexColor('#374151'),
            spaceAfter=4
        )
        meta_style = ParagraphStyle(
            'MetaStyle', parent=styles['Normal'],
            fontSize=9, textColor=colors.HexColor('#9ca3af'),
            alignment=TA_CENTER
        )

        story = []

        # Header
        story.append(Paragraph('Arithmetic', title_style))
        story.append(Paragraph('Mathematical Solution Report', subtitle_style))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#5e6ad2'), spaceAfter=15))

        # Meta info
        timestamp = data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        source_type = data.get('source_type', 'typed')
        method = data.get('method', 'auto')
        meta_text = f'Date: {timestamp} &nbsp; | &nbsp; Source: {source_type} &nbsp; | &nbsp; Method: {method}'
        story.append(Paragraph(meta_text, meta_style))
        story.append(Spacer(1, 15))

        # Problem
        problem = data.get('problem', 'N/A')
        story.append(Paragraph('Problem', heading_style))
        story.append(Paragraph(ReportService._escape(problem), body_style))
        story.append(Spacer(1, 8))

        # Extracted text (if from upload)
        extracted = data.get('extracted_text', '')
        if extracted:
            story.append(Paragraph('Extracted Text', heading_style))
            story.append(Paragraph(ReportService._escape(extracted), body_style))
            story.append(Spacer(1, 8))

        # Answer
        answer = data.get('answer', 'N/A')
        story.append(Paragraph('Final Answer', heading_style))
        story.append(Paragraph(f'<b>{ReportService._escape(answer)}</b>', answer_style))

        # Simplified / Decimal
        simplified = data.get('simplified', '')
        decimal_approx = data.get('decimal_approx', '')
        if simplified:
            story.append(Paragraph(f'Simplified: {ReportService._escape(simplified)}', body_style))
        if decimal_approx:
            story.append(Paragraph(f'Decimal Approximation: {ReportService._escape(decimal_approx)}', body_style))
        story.append(Spacer(1, 8))

        # Steps
        steps = data.get('steps', [])
        if steps:
            story.append(Paragraph('Step-by-Step Solution', heading_style))
            for i, step in enumerate(steps, 1):
                story.append(Paragraph(f'<b>Step {i}:</b> {ReportService._escape(str(step))}', step_style))
            story.append(Spacer(1, 8))

        # Graph
        graph_b64 = data.get('graph_base64', '')
        if graph_b64:
            story.append(Paragraph('Graph', heading_style))
            try:
                img_data = base64.b64decode(graph_b64)
                img_buf = io.BytesIO(img_data)
                img = Image(img_buf, width=5*inch, height=3*inch)
                story.append(img)
                story.append(Spacer(1, 12))
            except Exception:
                story.append(Paragraph('(Graph could not be embedded)', body_style))

        # Confidence
        confidence = data.get('confidence', '')
        if confidence:
            story.append(Paragraph('Confidence', heading_style))
            story.append(Paragraph(f'{confidence}', body_style))

        # Footer
        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e5e7eb')))
        story.append(Spacer(1, 8))
        story.append(Paragraph(
            f'Generated by Arithmetic — Premium Mathematical Intelligence Platform<br/>{timestamp}',
            meta_style
        ))

        doc.build(story)
        return buf.getvalue()

    @staticmethod
    def generate_html(data: dict) -> str:
        """Generate an HTML solution report.

        Args:
            data: Dict with problem, answer, steps, etc.

        Returns:
            HTML string
        """
        timestamp = data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        source_type = data.get('source_type', 'typed')
        method = data.get('method', 'auto')
        problem = ReportService._escape(data.get('problem', 'N/A'))
        answer = ReportService._escape(data.get('answer', 'N/A'))
        simplified = data.get('simplified', '')
        decimal_approx = data.get('decimal_approx', '')
        steps = data.get('steps', [])
        extracted = data.get('extracted_text', '')
        graph_b64 = data.get('graph_base64', '')
        confidence = data.get('confidence', '')

        steps_html = ''
        if steps:
            items = ''.join(f'<li>{ReportService._escape(str(s))}</li>' for s in steps)
            steps_html = f'''
            <div class="section">
                <h2>Step-by-Step Solution</h2>
                <ol class="steps-list">{items}</ol>
            </div>'''

        extracted_html = ''
        if extracted:
            extracted_html = f'''
            <div class="section">
                <h2>Extracted Text</h2>
                <div class="problem-box" style="font-family: monospace; font-size: 0.95rem;">{ReportService._escape(extracted)}</div>
            </div>'''

        graph_html = ''
        if graph_b64:
            graph_html = f'''
            <div class="section">
                <h2>Graph</h2>
                <div class="graph-container">
                    <img src="data:image/png;base64,{graph_b64}" alt="Solution graph">
                </div>
            </div>'''

        extra_html = ''
        if simplified:
            extra_html += f'<p style="margin-top:10px;color:#6b7280;">Simplified: {ReportService._escape(simplified)}</p>'
        if decimal_approx:
            extra_html += f'<p style="color:#6b7280;">Decimal: {ReportService._escape(decimal_approx)}</p>'

        confidence_html = ''
        if confidence:
            level = 'high' if 'high' in str(confidence).lower() else ('medium' if 'medium' in str(confidence).lower() else 'low')
            confidence_html = f'''
            <div class="section">
                <h2>Confidence</h2>
                <span class="confidence-badge confidence-{level}">{ReportService._escape(str(confidence))}</span>
            </div>'''

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Arithmetic - Solution Report</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; background: #fff; color: #1a1a2e; line-height: 1.7; padding: 40px; max-width: 800px; margin: 0 auto; }}
        .report-header {{ text-align: center; padding-bottom: 30px; border-bottom: 3px solid #5e6ad2; margin-bottom: 30px; }}
        .report-header h1 {{ font-size: 2rem; color: #5e6ad2; margin-bottom: 8px; }}
        .report-header .subtitle {{ color: #6b7280; font-size: 0.95rem; }}
        .meta-info {{ display: flex; justify-content: space-between; flex-wrap: wrap; gap: 10px; margin-bottom: 30px; padding: 16px 20px; background: #f8f9fc; border-radius: 12px; font-size: 0.9rem; color: #4b5563; }}
        .section {{ margin-bottom: 28px; }}
        .section h2 {{ font-size: 1.15rem; color: #5e6ad2; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #e5e7eb; }}
        .problem-box {{ background: #f0f1ff; border: 1px solid #d4d6f0; border-radius: 10px; padding: 16px 20px; font-size: 1.05rem; }}
        .answer-box {{ background: linear-gradient(135deg, #f0fdf4, #ecfdf5); border: 1px solid #86efac; border-radius: 10px; padding: 20px; font-size: 1.2rem; font-weight: 600; text-align: center; }}
        .steps-list {{ list-style: none; counter-reset: step-counter; }}
        .steps-list li {{ counter-increment: step-counter; padding: 12px 16px 12px 48px; position: relative; margin-bottom: 8px; background: #fafbff; border-radius: 8px; border: 1px solid #e8eaf0; }}
        .steps-list li::before {{ content: counter(step-counter); position: absolute; left: 14px; top: 12px; width: 24px; height: 24px; background: #5e6ad2; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: 600; }}
        .graph-container {{ text-align: center; margin: 20px 0; }}
        .graph-container img {{ max-width: 100%; border-radius: 10px; border: 1px solid #e5e7eb; }}
        .confidence-badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 500; }}
        .confidence-high {{ background: #dcfce7; color: #166534; }}
        .confidence-medium {{ background: #fef3c7; color: #92400e; }}
        .confidence-low {{ background: #fee2e2; color: #991b1b; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb; text-align: center; color: #9ca3af; font-size: 0.85rem; }}
    </style>
</head>
<body>
    <div class="report-header">
        <h1>Arithmetic</h1>
        <p class="subtitle">Mathematical Solution Report</p>
    </div>
    <div class="meta-info">
        <span><strong>Date:</strong> {timestamp}</span>
        <span><strong>Source:</strong> {source_type}</span>
        <span><strong>Method:</strong> {method}</span>
    </div>
    <div class="section">
        <h2>Problem</h2>
        <div class="problem-box">{problem}</div>
    </div>
    {extracted_html}
    <div class="section">
        <h2>Final Answer</h2>
        <div class="answer-box">{answer}</div>
        {extra_html}
    </div>
    {steps_html}
    {graph_html}
    {confidence_html}
    <div class="footer">
        <p>Generated by Arithmetic &mdash; Premium Mathematical Intelligence Platform</p>
        <p>{timestamp}</p>
    </div>
</body>
</html>'''
        return html

    @staticmethod
    def _escape(text: str) -> str:
        """Escape HTML special characters."""
        if not text:
            return ''
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))
